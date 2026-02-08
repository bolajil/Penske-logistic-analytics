import { TrendingUp, Package, Clock, CheckCircle } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const stats = [
  { label: 'Total Shipments', value: '12,543', change: '+12%', icon: Package, color: 'blue' },
  { label: 'On-Time Rate', value: '96.2%', change: '+2.1%', icon: CheckCircle, color: 'green' },
  { label: 'Avg Response', value: '45ms', change: '-5ms', icon: Clock, color: 'purple' },
  { label: 'Predictions', value: '3,421', change: '+18%', icon: TrendingUp, color: 'orange' },
]

const chartData = [
  { name: 'Mon', shipments: 1200, predicted: 1180 },
  { name: 'Tue', shipments: 1350, predicted: 1320 },
  { name: 'Wed', shipments: 1280, predicted: 1300 },
  { name: 'Thu', shipments: 1420, predicted: 1380 },
  { name: 'Fri', shipments: 1550, predicted: 1520 },
  { name: 'Sat', shipments: 980, predicted: 1000 },
  { name: 'Sun', shipments: 850, predicted: 880 },
]

export default function Dashboard() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Overview of your logistics performance</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.label} className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">{stat.label}</p>
                  <p className="text-2xl font-bold mt-1">{stat.value}</p>
                  <p className={`text-sm mt-1 ${
                    stat.change.startsWith('+') ? 'text-green-600' : 'text-blue-600'
                  }`}>
                    {stat.change} from last week
                  </p>
                </div>
                <div className={`p-3 rounded-lg bg-${stat.color}-100`}>
                  <Icon className={`w-6 h-6 text-${stat.color}-600`} />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Chart */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Shipments vs Predictions</h2>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="shipments" 
                stroke="#3b82f6" 
                strokeWidth={2}
                name="Actual"
              />
              <Line 
                type="monotone" 
                dataKey="predicted" 
                stroke="#10b981" 
                strokeWidth={2}
                strokeDasharray="5 5"
                name="Predicted"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
