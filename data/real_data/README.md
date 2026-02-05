# Real Data Directory

This folder is designated for actual Penske Logistics data files.

## Required Data Files

Place your production data files here following these specifications:

### 1. fleet_operations.csv
| Column | Type | Description |
|--------|------|-------------|
| vehicle_id | string | Unique vehicle identifier |
| date | datetime | Operation date |
| region | string | Geographic region |
| service_type | string | Service category |
| miles_driven | float | Total miles for the day |
| fuel_consumed | float | Gallons of fuel used |
| load_capacity_used | float | Percentage of capacity utilized |
| driver_id | string | Driver identifier |
| on_time_deliveries | int | Number of on-time deliveries |
| total_deliveries | int | Total deliveries attempted |

### 2. warehouse_metrics.csv
| Column | Type | Description |
|--------|------|-------------|
| warehouse_id | string | Facility identifier |
| date | datetime | Metric date |
| region | string | Geographic region |
| throughput_units | int | Units processed |
| labor_hours | float | Total labor hours |
| inventory_accuracy | float | Accuracy percentage |
| order_fill_rate | float | Order completion rate |
| dock_utilization | float | Dock usage percentage |

### 3. customer_data.csv
| Column | Type | Description |
|--------|------|-------------|
| customer_id | string | Customer identifier |
| company_name | string | Company name |
| industry | string | Industry vertical |
| region | string | Primary operating region |
| annual_revenue | float | Customer's annual revenue |
| contract_value | float | Annual contract value |
| services_used | string | Comma-separated service types |
| tenure_months | int | Months as customer |
| satisfaction_score | float | NPS or satisfaction rating |
| is_active | boolean | Current customer status |

### 4. maintenance_records.csv
| Column | Type | Description |
|--------|------|-------------|
| maintenance_id | string | Record identifier |
| vehicle_id | string | Vehicle identifier |
| date | datetime | Service date |
| maintenance_type | string | Preventive/Corrective/Emergency |
| cost | float | Total maintenance cost |
| downtime_hours | float | Vehicle downtime |
| parts_replaced | string | Parts list |
| mileage_at_service | int | Odometer reading |

### 5. delivery_performance.csv
| Column | Type | Description |
|--------|------|-------------|
| delivery_id | string | Shipment identifier |
| date | datetime | Delivery date |
| origin_region | string | Pickup region |
| destination_region | string | Delivery region |
| service_type | string | LTL/FTL/Expedited |
| scheduled_time | datetime | Promised delivery time |
| actual_time | datetime | Actual delivery time |
| weight_lbs | float | Shipment weight |
| customer_id | string | Customer identifier |
| driver_id | string | Driver identifier |

### 6. regional_demand.csv
| Column | Type | Description |
|--------|------|-------------|
| date | datetime | Record date |
| region | string | Geographic region |
| service_type | string | Service category |
| shipment_volume | int | Number of shipments |
| total_weight | float | Total weight shipped |
| total_revenue | float | Revenue generated |
| fleet_vehicles_available | int | Available vehicles |
| warehouse_capacity_used | float | Capacity percentage |

## Data Security Notes

- **DO NOT** commit actual production data to version control
- All files in this directory are gitignored by default
- Ensure data is encrypted at rest
- Follow Penske's data governance policies
- Use secure transfer methods (SFTP, encrypted S3, etc.)

## Data Validation

Run the validation script after placing data:
```bash
python -m src.data_prep --validate --path data/real_data/
```
