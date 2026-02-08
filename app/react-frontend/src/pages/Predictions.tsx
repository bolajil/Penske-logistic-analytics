import { useState } from 'react'
import { Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'

interface PredictionResult {
  prediction: number
  confidence: number
  latency: number
}

export default function Predictions() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<PredictionResult | null>(null)
  const [formData, setFormData] = useState({
    shipmentVolume: 1250,
    fuelPrice: 3.45,
    weatherSeverity: 0,
    dayOfWeek: 2,
    isHoliday: false,
    previousDayVolume: 1180,
    region: 'Northeast',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    // Simulate API call (demo mode)
    await new Promise((resolve) => setTimeout(resolve, 800))
    
    setResult({
      prediction: Math.floor(Math.random() * 600) + 1200,
      confidence: Math.random() * 0.13 + 0.85,
      latency: Math.floor(Math.random() * 50) + 30,
    })
    
    toast.success('Prediction complete!')
    setLoading(false)
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Demand Prediction</h1>
        <p className="text-gray-600 mt-1">Predict logistics demand using ML models</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Form */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-6">Input Features</h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Shipment Volume
                </label>
                <input
                  type="number"
                  className="input"
                  value={formData.shipmentVolume}
                  onChange={(e) => setFormData({ ...formData, shipmentVolume: +e.target.value })}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Fuel Price ($/gal)
                </label>
                <input
                  type="number"
                  step="0.01"
                  className="input"
                  value={formData.fuelPrice}
                  onChange={(e) => setFormData({ ...formData, fuelPrice: +e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Weather Severity (0-3)
                </label>
                <input
                  type="number"
                  min="0"
                  max="3"
                  className="input"
                  value={formData.weatherSeverity}
                  onChange={(e) => setFormData({ ...formData, weatherSeverity: +e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Day of Week (1-7)
                </label>
                <input
                  type="number"
                  min="1"
                  max="7"
                  className="input"
                  value={formData.dayOfWeek}
                  onChange={(e) => setFormData({ ...formData, dayOfWeek: +e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Previous Day Volume
                </label>
                <input
                  type="number"
                  className="input"
                  value={formData.previousDayVolume}
                  onChange={(e) => setFormData({ ...formData, previousDayVolume: +e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Region
                </label>
                <select
                  className="input"
                  value={formData.region}
                  onChange={(e) => setFormData({ ...formData, region: e.target.value })}
                >
                  <option value="Midwest">Midwest</option>
                  <option value="Northeast">Northeast</option>
                  <option value="Southeast">Southeast</option>
                  <option value="West">West</option>
                </select>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="isHoliday"
                checked={formData.isHoliday}
                onChange={(e) => setFormData({ ...formData, isHoliday: e.target.checked })}
                className="w-4 h-4 text-primary-600 rounded"
              />
              <label htmlFor="isHoliday" className="text-sm text-gray-700">
                Is Holiday
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Predicting...
                </>
              ) : (
                'Predict Demand'
              )}
            </button>
          </form>
        </div>

        {/* Results */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-6">Prediction Result</h2>
          
          {result ? (
            <div className="space-y-6">
              <div className="text-center p-8 bg-primary-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-2">Predicted Demand</p>
                <p className="text-5xl font-bold text-primary-700">
                  {result.prediction.toLocaleString()}
                </p>
                <p className="text-gray-500 mt-1">shipments</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-green-50 rounded-lg text-center">
                  <p className="text-sm text-gray-600">Confidence</p>
                  <p className="text-2xl font-bold text-green-700">
                    {(result.confidence * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg text-center">
                  <p className="text-sm text-gray-600">Latency</p>
                  <p className="text-2xl font-bold text-purple-700">
                    {result.latency}ms
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <p>Enter features and click predict to see results</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
