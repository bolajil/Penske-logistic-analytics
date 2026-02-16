"""
Session & Timeout Management for Penske Logistics Analytics
============================================================
Production-grade session handling with:
- Configurable timeouts per service (LLM, embedding, search, database)
- Exponential backoff retry with jitter
- Circuit breaker pattern (stop hammering dead services)
- Model fallback chain (GPT-4 → GPT-3.5 → cached → error message)
- Session lifecycle management (create, refresh, expire)
- Audit logging for every timeout, retry, and fallback event

Usage:
    from session_manager import SessionManager, TimeoutConfig

    manager = SessionManager()
    
    # Simple retry with timeout
    result = manager.call_with_retry(my_api_function, args=("prompt",), timeout=10)
    
    # LLM call with model fallback
    result = manager.call_llm_with_fallback(client, messages, primary_model="gpt-4")
    
    # Full session lifecycle
    session = manager.create_session(user_id="dispatcher_42")
    manager.refresh_session(session.session_id)
    manager.expire_session(session.session_id)
"""

import time
import uuid
import logging
import threading
import functools
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

class ServiceType(Enum):
    """Service categories with different timeout profiles."""
    LLM = "llm"
    EMBEDDING = "embedding"
    SEARCH = "search"
    DATABASE = "database"
    TOOL_CALL = "tool_call"


@dataclass
class TimeoutConfig:
    """Timeout and retry configuration per service type.
    
    Attributes:
        timeout_seconds: Max wait time for a single call
        max_retries: Number of retry attempts before giving up
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        backoff_factor: Multiplier for exponential backoff (delay *= factor each retry)
        jitter: Add randomness to delay to prevent thundering herd
    """
    timeout_seconds: float = 10.0
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    backoff_factor: float = 2.0
    jitter: bool = True


# Production-tested defaults per service type
DEFAULT_TIMEOUT_CONFIGS: Dict[ServiceType, TimeoutConfig] = {
    ServiceType.LLM: TimeoutConfig(
        timeout_seconds=30.0,   # LLM calls can be slow (especially GPT-4)
        max_retries=3,
        base_delay=2.0,
        max_delay=30.0,
        backoff_factor=2.0,
    ),
    ServiceType.EMBEDDING: TimeoutConfig(
        timeout_seconds=15.0,   # Embedding calls are faster
        max_retries=3,
        base_delay=1.0,
        max_delay=15.0,
        backoff_factor=2.0,
    ),
    ServiceType.SEARCH: TimeoutConfig(
        timeout_seconds=10.0,   # Search should be fast
        max_retries=2,
        base_delay=0.5,
        max_delay=5.0,
        backoff_factor=2.0,
    ),
    ServiceType.DATABASE: TimeoutConfig(
        timeout_seconds=15.0,   # DB queries (Snowflake, etc.)
        max_retries=2,
        base_delay=1.0,
        max_delay=10.0,
        backoff_factor=2.0,
    ),
    ServiceType.TOOL_CALL: TimeoutConfig(
        timeout_seconds=10.0,   # Agent tool calls
        max_retries=2,
        base_delay=1.0,
        max_delay=10.0,
        backoff_factor=2.0,
    ),
}


# ---------------------------------------------------------------------------
# Circuit Breaker
# ---------------------------------------------------------------------------

class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation — requests flow through
    OPEN = "open"           # Service is down — reject requests immediately
    HALF_OPEN = "half_open" # Testing if service recovered — allow one request


@dataclass
class CircuitBreaker:
    """Circuit breaker prevents hammering a dead service.
    
    State transitions:
        CLOSED → OPEN:     When failure_count >= failure_threshold
        OPEN → HALF_OPEN:  After recovery_timeout seconds
        HALF_OPEN → CLOSED: If test request succeeds
        HALF_OPEN → OPEN:   If test request fails
    
    Penske example:
        Azure OpenAI has an outage. After 5 failures in 60 seconds,
        the circuit opens. All requests immediately fall back to
        GPT-3.5 or cached responses. After 30 seconds, one test
        request goes through. If it succeeds, circuit closes and
        normal operation resumes.
    """
    service_name: str
    failure_threshold: int = 5          # Failures before opening circuit
    recovery_timeout: float = 30.0      # Seconds before trying again
    monitoring_window: float = 60.0     # Window to count failures
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[float] = None
    last_state_change: Optional[float] = None
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def record_success(self):
        """Record a successful call."""
        with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.last_state_change = time.time()
                logger.info(f"Circuit CLOSED for {self.service_name} — service recovered")
            elif self.state == CircuitState.CLOSED:
                self.failure_count = 0

    def record_failure(self):
        """Record a failed call."""
        with self._lock:
            now = time.time()
            self.last_failure_time = now

            # Reset count if outside monitoring window
            if self.last_state_change and (now - self.last_state_change) > self.monitoring_window:
                self.failure_count = 0

            self.failure_count += 1

            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                self.last_state_change = now
                logger.warning(f"Circuit OPEN for {self.service_name} — test request failed")
            elif self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.last_state_change = now
                logger.warning(
                    f"Circuit OPEN for {self.service_name} — "
                    f"{self.failure_count} failures in {self.monitoring_window}s"
                )

    def allow_request(self) -> bool:
        """Check if a request should be allowed through."""
        with self._lock:
            if self.state == CircuitState.CLOSED:
                return True
            elif self.state == CircuitState.OPEN:
                if (time.time() - (self.last_state_change or 0)) > self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.last_state_change = time.time()
                    logger.info(f"Circuit HALF_OPEN for {self.service_name} — testing recovery")
                    return True
                return False
            elif self.state == CircuitState.HALF_OPEN:
                return True
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status for monitoring dashboards."""
        return {
            "service": self.service_name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure": datetime.fromtimestamp(self.last_failure_time).isoformat()
                if self.last_failure_time else None,
        }


# ---------------------------------------------------------------------------
# Session Management
# ---------------------------------------------------------------------------

class SessionState(Enum):
    ACTIVE = "active"
    IDLE = "idle"
    EXPIRED = "expired"


@dataclass
class Session:
    """Represents a user or agent session with timeout tracking.
    
    Penske example:
        A dispatcher opens the shipment tracking assistant.
        Session created with 30-min idle timeout. If they stop
        interacting for 30 minutes, session expires and context
        is saved. If they come back, a new session starts with
        a summary of the previous one.
    """
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    idle_timeout: timedelta = field(default_factory=lambda: timedelta(minutes=30))
    max_lifetime: timedelta = field(default_factory=lambda: timedelta(hours=8))
    state: SessionState = SessionState.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)
    interaction_count: int = 0
    total_tokens_used: int = 0
    errors: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def is_expired(self) -> bool:
        """Check if session has expired due to idle timeout or max lifetime."""
        now = datetime.now()
        idle_expired = (now - self.last_activity) > self.idle_timeout
        lifetime_expired = (now - self.created_at) > self.max_lifetime
        return idle_expired or lifetime_expired

    @property
    def time_remaining(self) -> timedelta:
        """Time until idle timeout."""
        elapsed = datetime.now() - self.last_activity
        remaining = self.idle_timeout - elapsed
        return max(remaining, timedelta(0))

    def touch(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.now()
        self.interaction_count += 1

    def add_tokens(self, count: int):
        """Track token usage for cost monitoring."""
        self.total_tokens_used += count

    def record_error(self, error_type: str, details: str):
        """Log an error that occurred during this session."""
        self.errors.append({
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "details": details,
        })

    def get_summary(self) -> Dict[str, Any]:
        """Get session summary for logging and monitoring."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "duration_minutes": (datetime.now() - self.created_at).total_seconds() / 60,
            "time_remaining_minutes": self.time_remaining.total_seconds() / 60,
            "interaction_count": self.interaction_count,
            "total_tokens_used": self.total_tokens_used,
            "error_count": len(self.errors),
        }


# ---------------------------------------------------------------------------
# Session Manager (main class)
# ---------------------------------------------------------------------------

class SessionManager:
    """Production session and timeout manager for Penske Logistics AI services.
    
    Handles:
    1. Session lifecycle (create, refresh, expire, cleanup)
    2. Retry with exponential backoff + jitter
    3. Circuit breaker per service
    4. LLM model fallback chain
    5. Timeout enforcement via thread pool
    6. Audit logging for every event
    
    Usage:
        manager = SessionManager()
        
        # Create a session for a dispatcher
        session = manager.create_session(user_id="dispatcher_42")
        
        # Make an API call with retry + timeout
        result = manager.call_with_retry(
            func=my_api_call,
            args=("prompt",),
            service_type=ServiceType.LLM,
        )
        
        # LLM call with automatic model fallback
        result = manager.call_llm_with_fallback(
            client=openai_client,
            messages=[{"role": "user", "content": "Where is PEN-2026-001?"}],
        )
    """

    def __init__(
        self,
        timeout_configs: Optional[Dict[ServiceType, TimeoutConfig]] = None,
        session_idle_timeout_minutes: int = 30,
        session_max_lifetime_hours: int = 8,
        max_concurrent_calls: int = 10,
    ):
        self._configs = timeout_configs or DEFAULT_TIMEOUT_CONFIGS
        self._session_idle_timeout = timedelta(minutes=session_idle_timeout_minutes)
        self._session_max_lifetime = timedelta(hours=session_max_lifetime_hours)
        self._sessions: Dict[str, Session] = {}
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._executor = ThreadPoolExecutor(max_workers=max_concurrent_calls)
        self._lock = threading.Lock()
        self._audit_log: List[Dict[str, Any]] = []

    # -----------------------------------------------------------------------
    # Session Lifecycle
    # -----------------------------------------------------------------------

    def create_session(
        self,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Session:
        """Create a new session for a user or agent."""
        session = Session(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            idle_timeout=self._session_idle_timeout,
            max_lifetime=self._session_max_lifetime,
            metadata=metadata or {},
        )
        with self._lock:
            self._sessions[session.session_id] = session
        self._log_event("session_created", session_id=session.session_id, user_id=user_id)
        logger.info(f"Session created: {session.session_id} for user {user_id}")
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID. Returns None if expired or not found."""
        session = self._sessions.get(session_id)
        if session is None:
            return None
        if session.is_expired:
            self.expire_session(session_id)
            return None
        return session

    def refresh_session(self, session_id: str) -> bool:
        """Refresh session activity timestamp (call on every user interaction)."""
        session = self.get_session(session_id)
        if session is None:
            return False
        session.touch()
        self._log_event("session_refreshed", session_id=session_id)
        return True

    def expire_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Expire a session and return its summary."""
        session = self._sessions.get(session_id)
        if session is None:
            return None
        session.state = SessionState.EXPIRED
        summary = session.get_summary()
        self._log_event("session_expired", session_id=session_id, details=summary)
        logger.info(f"Session expired: {session_id} (duration: {summary['duration_minutes']:.1f}min)")
        return summary

    def cleanup_expired_sessions(self) -> int:
        """Remove all expired sessions. Returns count of cleaned sessions."""
        expired_ids = [
            sid for sid, s in self._sessions.items() if s.is_expired
        ]
        for sid in expired_ids:
            self.expire_session(sid)
            del self._sessions[sid]
        if expired_ids:
            logger.info(f"Cleaned up {len(expired_ids)} expired sessions")
        return len(expired_ids)

    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions for monitoring."""
        return [
            s.get_summary() for s in self._sessions.values()
            if s.state == SessionState.ACTIVE and not s.is_expired
        ]

    # -----------------------------------------------------------------------
    # Retry with Timeout
    # -----------------------------------------------------------------------

    def call_with_retry(
        self,
        func: Callable,
        args: tuple = (),
        kwargs: Optional[Dict] = None,
        service_type: ServiceType = ServiceType.LLM,
        config: Optional[TimeoutConfig] = None,
        circuit_name: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Any:
        """Execute a function with retry, timeout, and circuit breaker.
        
        Args:
            func: The function to call
            args: Positional arguments for func
            kwargs: Keyword arguments for func
            service_type: Type of service (determines default timeout config)
            config: Override timeout config (optional)
            circuit_name: Circuit breaker name (optional, defaults to service_type)
            session_id: Session to track this call against (optional)
            
        Returns:
            The result of func(*args, **kwargs)
            
        Raises:
            TimeoutError: If all retries exhausted
            CircuitBreakerOpenError: If circuit is open
        """
        kwargs = kwargs or {}
        cfg = config or self._configs.get(service_type, TimeoutConfig())
        cb_name = circuit_name or service_type.value
        breaker = self._get_or_create_breaker(cb_name)

        # Check circuit breaker
        if not breaker.allow_request():
            self._log_event(
                "circuit_breaker_rejected",
                service=cb_name,
                state=breaker.state.value,
            )
            raise CircuitBreakerOpenError(
                f"Circuit breaker OPEN for {cb_name}. "
                f"Service appears down. Retry after {breaker.recovery_timeout}s."
            )

        last_exception = None

        for attempt in range(1, cfg.max_retries + 1):
            try:
                result = self._execute_with_timeout(
                    func, args, kwargs, cfg.timeout_seconds
                )
                breaker.record_success()
                self._log_event(
                    "call_success",
                    service=cb_name,
                    attempt=attempt,
                    session_id=session_id,
                )
                return result

            except FuturesTimeoutError:
                last_exception = TimeoutError(
                    f"{cb_name} timed out after {cfg.timeout_seconds}s (attempt {attempt}/{cfg.max_retries})"
                )
                breaker.record_failure()
                self._log_event(
                    "call_timeout",
                    service=cb_name,
                    attempt=attempt,
                    timeout=cfg.timeout_seconds,
                    session_id=session_id,
                )
                logger.warning(str(last_exception))

            except Exception as e:
                last_exception = e
                breaker.record_failure()
                self._log_event(
                    "call_error",
                    service=cb_name,
                    attempt=attempt,
                    error=str(e),
                    session_id=session_id,
                )
                logger.warning(
                    f"{cb_name} error on attempt {attempt}/{cfg.max_retries}: {e}"
                )

            # Wait before retry (exponential backoff with optional jitter)
            if attempt < cfg.max_retries:
                delay = self._calculate_backoff(attempt, cfg)
                logger.info(f"Retrying {cb_name} in {delay:.1f}s...")
                time.sleep(delay)

        # All retries exhausted
        if session_id:
            session = self.get_session(session_id)
            if session:
                session.record_error("all_retries_exhausted", str(last_exception))

        raise last_exception

    def _execute_with_timeout(
        self, func: Callable, args: tuple, kwargs: dict, timeout: float
    ) -> Any:
        """Run a function in a thread with a timeout."""
        future = self._executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout)
        except FuturesTimeoutError:
            future.cancel()
            raise

    @staticmethod
    def _calculate_backoff(attempt: int, config: TimeoutConfig) -> float:
        """Calculate delay with exponential backoff and optional jitter."""
        import random
        delay = config.base_delay * (config.backoff_factor ** (attempt - 1))
        delay = min(delay, config.max_delay)
        if config.jitter:
            delay = delay * (0.5 + random.random())  # 50%-150% of calculated delay
        return delay

    # -----------------------------------------------------------------------
    # LLM Model Fallback Chain
    # -----------------------------------------------------------------------

    def call_llm_with_fallback(
        self,
        client: Any,
        messages: List[Dict[str, str]],
        primary_model: str = "gpt-4",
        fallback_models: Optional[List[str]] = None,
        cached_response: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Call LLM with automatic model fallback chain.
        
        Fallback order:
            1. Primary model (e.g., GPT-4)
            2. Fallback models in order (e.g., GPT-3.5-turbo)
            3. Cached response (if provided)
            4. Graceful error message
        
        Returns:
            {
                "content": "response text",
                "model_used": "gpt-4" or "gpt-3.5-turbo" or "cache" or "error",
                "attempt_log": [...],
                "tokens_used": 150,
            }
        """
        fallback_models = fallback_models or ["gpt-3.5-turbo"]
        all_models = [primary_model] + fallback_models
        attempt_log = []

        for model in all_models:
            try:
                def _make_call():
                    return client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )

                response = self.call_with_retry(
                    func=_make_call,
                    service_type=ServiceType.LLM,
                    circuit_name=f"llm_{model}",
                    session_id=session_id,
                )

                tokens_used = getattr(response.usage, 'total_tokens', 0) if response.usage else 0
                if session_id:
                    session = self.get_session(session_id)
                    if session:
                        session.add_tokens(tokens_used)

                result = {
                    "content": response.choices[0].message.content,
                    "model_used": model,
                    "attempt_log": attempt_log,
                    "tokens_used": tokens_used,
                }
                self._log_event(
                    "llm_success", model=model, tokens=tokens_used, session_id=session_id
                )
                return result

            except Exception as e:
                attempt_log.append({
                    "model": model,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                })
                logger.warning(f"LLM fallback: {model} failed — {e}")
                continue

        # All models failed — try cached response
        if cached_response:
            self._log_event("llm_cache_fallback", session_id=session_id)
            return {
                "content": cached_response,
                "model_used": "cache",
                "attempt_log": attempt_log,
                "tokens_used": 0,
            }

        # Everything failed
        error_msg = (
            "I'm temporarily unable to process your request. "
            "Please try again in a moment, or contact support if the issue persists."
        )
        self._log_event("llm_all_failed", session_id=session_id, attempts=attempt_log)
        return {
            "content": error_msg,
            "model_used": "error",
            "attempt_log": attempt_log,
            "tokens_used": 0,
        }

    # -----------------------------------------------------------------------
    # External Tool Fallback (Slack, Email, Jira, etc.)
    # -----------------------------------------------------------------------

    def call_tool_with_fallback(
        self,
        tool_name: str,
        primary_func: Callable,
        fallback_funcs: Optional[List[Dict[str, Any]]] = None,
        args: tuple = (),
        kwargs: Optional[Dict] = None,
        config: Optional[TimeoutConfig] = None,
        session_id: Optional[str] = None,
        queue_on_failure: bool = True,
    ) -> Dict[str, Any]:
        """Call an external tool (Slack, email, Jira, etc.) with fallback chain.
        
        Unlike LLM fallback (which swaps models), tool fallback swaps CHANNELS.
        If Slack is down, send via email. If email is down, queue for retry.
        
        Fallback order:
            1. Primary tool (e.g., Slack API)
            2. Fallback tools in order (e.g., email, Teams, SMS)
            3. Queue for async retry (if queue_on_failure=True)
            4. Return failure with details for the agent to handle
        
        Args:
            tool_name: Name of the primary tool (for logging/circuit breaker)
            primary_func: The primary tool function to call
            fallback_funcs: List of fallback options, each a dict with:
                - "name": str — tool name (e.g., "email", "teams")
                - "func": Callable — the fallback function
                - "args": tuple — args for the fallback (optional)
                - "kwargs": dict — kwargs for the fallback (optional)
            args: Positional arguments for primary_func
            kwargs: Keyword arguments for primary_func
            config: Override timeout config (optional)
            session_id: Session to track this call against (optional)
            queue_on_failure: If True, queue the action for async retry
            
        Returns:
            {
                "success": True/False,
                "tool_used": "slack" or "email" or "queued" or "failed",
                "result": <tool response or None>,
                "attempt_log": [...],
                "queued": True/False,
            }
            
        Penske example:
            Agent needs to notify a dispatcher about a delayed shipment.
            Slack API is rate-limited → falls back to email → succeeds.
            
            result = manager.call_tool_with_fallback(
                tool_name="slack",
                primary_func=slack_client.send_message,
                args=("#dispatch-alerts", "PEN-2026-001 delayed 90min"),
                fallback_funcs=[
                    {"name": "email", "func": send_email,
                     "args": ("dispatch@penske.com", "Shipment Delay Alert",
                              "PEN-2026-001 delayed 90min on I-35")},
                    {"name": "teams", "func": teams_client.send,
                     "args": ("dispatch-channel", "PEN-2026-001 delayed 90min")},
                ],
            )
        """
        kwargs = kwargs or {}
        cfg = config or self._configs.get(ServiceType.TOOL_CALL, TimeoutConfig())
        attempt_log = []

        # --- Try primary tool ---
        try:
            result = self.call_with_retry(
                func=primary_func,
                args=args,
                kwargs=kwargs,
                service_type=ServiceType.TOOL_CALL,
                config=cfg,
                circuit_name=f"tool_{tool_name}",
                session_id=session_id,
            )
            self._log_event(
                "tool_success", tool=tool_name, session_id=session_id
            )
            return {
                "success": True,
                "tool_used": tool_name,
                "result": result,
                "attempt_log": attempt_log,
                "queued": False,
            }
        except Exception as e:
            attempt_log.append({
                "tool": tool_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            })
            logger.warning(f"Primary tool {tool_name} failed: {e}")

        # --- Try fallback tools ---
        for fallback in (fallback_funcs or []):
            fb_name = fallback["name"]
            fb_func = fallback["func"]
            fb_args = fallback.get("args", ())
            fb_kwargs = fallback.get("kwargs", {})

            try:
                result = self.call_with_retry(
                    func=fb_func,
                    args=fb_args,
                    kwargs=fb_kwargs,
                    service_type=ServiceType.TOOL_CALL,
                    config=cfg,
                    circuit_name=f"tool_{fb_name}",
                    session_id=session_id,
                )
                self._log_event(
                    "tool_fallback_success",
                    primary_tool=tool_name,
                    fallback_tool=fb_name,
                    session_id=session_id,
                )
                logger.info(f"Tool fallback: {tool_name} → {fb_name} succeeded")
                return {
                    "success": True,
                    "tool_used": fb_name,
                    "result": result,
                    "attempt_log": attempt_log,
                    "queued": False,
                }
            except Exception as e:
                attempt_log.append({
                    "tool": fb_name,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                })
                logger.warning(f"Fallback tool {fb_name} failed: {e}")
                continue

        # --- All tools failed — queue for async retry ---
        if queue_on_failure:
            queued_action = {
                "tool": tool_name,
                "args": str(args),
                "kwargs": str(kwargs),
                "fallbacks_tried": [f.get("name") for f in (fallback_funcs or [])],
                "queued_at": datetime.now().isoformat(),
                "retry_after": datetime.now().isoformat(),
            }
            self._log_event(
                "tool_queued_for_retry",
                action=queued_action,
                session_id=session_id,
            )
            logger.warning(
                f"All tools failed for {tool_name}. Action queued for async retry."
            )

            if session_id:
                session = self.get_session(session_id)
                if session:
                    session.record_error(
                        "tool_all_failed_queued",
                        f"{tool_name} and all fallbacks failed. Queued for retry."
                    )

            return {
                "success": False,
                "tool_used": "queued",
                "result": None,
                "attempt_log": attempt_log,
                "queued": True,
                "queued_action": queued_action,
            }

        # --- No queue, just fail ---
        self._log_event(
            "tool_all_failed", tool=tool_name, session_id=session_id, attempts=attempt_log
        )
        return {
            "success": False,
            "tool_used": "failed",
            "result": None,
            "attempt_log": attempt_log,
            "queued": False,
        }

    # -----------------------------------------------------------------------
    # Circuit Breaker Management
    # -----------------------------------------------------------------------

    def _get_or_create_breaker(self, name: str) -> CircuitBreaker:
        """Get or create a circuit breaker for a service."""
        if name not in self._circuit_breakers:
            self._circuit_breakers[name] = CircuitBreaker(service_name=name)
        return self._circuit_breakers[name]

    def get_circuit_status(self) -> Dict[str, Dict]:
        """Get status of all circuit breakers for monitoring."""
        return {
            name: cb.get_status()
            for name, cb in self._circuit_breakers.items()
        }

    def reset_circuit(self, service_name: str):
        """Manually reset a circuit breaker (e.g., after a known fix)."""
        if service_name in self._circuit_breakers:
            cb = self._circuit_breakers[service_name]
            cb.state = CircuitState.CLOSED
            cb.failure_count = 0
            logger.info(f"Circuit manually reset for {service_name}")

    # -----------------------------------------------------------------------
    # Audit Logging
    # -----------------------------------------------------------------------

    def _log_event(self, event_type: str, **details):
        """Log an audit event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            **details,
        }
        self._audit_log.append(event)
        # Keep last 10,000 events in memory
        if len(self._audit_log) > 10000:
            self._audit_log = self._audit_log[-5000:]

    def get_audit_log(self, last_n: int = 100) -> List[Dict]:
        """Get recent audit events."""
        return self._audit_log[-last_n:]

    def get_stats(self) -> Dict[str, Any]:
        """Get overall session manager statistics."""
        active = [s for s in self._sessions.values() if not s.is_expired]
        return {
            "active_sessions": len(active),
            "total_sessions_created": len(self._sessions),
            "circuit_breakers": self.get_circuit_status(),
            "recent_events": len(self._audit_log),
            "timeout_configs": {
                st.value: {
                    "timeout_s": cfg.timeout_seconds,
                    "max_retries": cfg.max_retries,
                }
                for st, cfg in self._configs.items()
            },
        }

    def shutdown(self):
        """Clean shutdown — expire all sessions and stop executor."""
        for sid in list(self._sessions.keys()):
            self.expire_session(sid)
        self._executor.shutdown(wait=False)
        logger.info("SessionManager shut down")


# ---------------------------------------------------------------------------
# Custom Exceptions
# ---------------------------------------------------------------------------

class CircuitBreakerOpenError(Exception):
    """Raised when a circuit breaker is open and rejecting requests."""
    pass


class SessionExpiredError(Exception):
    """Raised when an operation is attempted on an expired session."""
    pass


# ---------------------------------------------------------------------------
# Decorator for easy integration
# ---------------------------------------------------------------------------

def with_timeout_retry(
    service_type: ServiceType = ServiceType.LLM,
    config: Optional[TimeoutConfig] = None,
    manager: Optional[SessionManager] = None,
):
    """Decorator to add timeout + retry to any function.
    
    Usage:
        @with_timeout_retry(service_type=ServiceType.LLM)
        def call_openai(prompt):
            return client.chat.completions.create(...)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            mgr = manager or SessionManager()
            return mgr.call_with_retry(
                func=func,
                args=args,
                kwargs=kwargs,
                service_type=service_type,
                config=config,
            )
        return wrapper
    return decorator
