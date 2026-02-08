import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const weeklyData = [
  { name: 'Week 1', onTime: 1250, delayed: 85 },
  { name: 'Week 2', onTime: 1320, delayed: 72 },
  { name: 'Week 3', onTime: 1180, delayed: 95 },
  { name: 'Week 4', onTime: 1420, delayed: 68 },
]

const regionData = [
  { name: 'Northeast', value: 35 },
  { name: 'Midwest', value: 28 },
  { name: 'Southeast', value: 22 },
  { name: 'West', value: 15 },
]

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6']

const tableData = [
  { date: '2024-01-15', shipments: 1342, onTime: 96.2, avgDelay: 1.2 },
  { date: '2024-01-14', shipments: 1285, onTime: 95.8, avgDelay: 1.4 },
  { date: '2024-01-13', shipments: 1198, onTime: 97.1, avgDelay: 0.9 },
  { date: '2024-01-12', shipments: 1456, onTime: 94.5, avgDelay: 1.8 },
  { date: '2024-01-11', shipments: 1378, onTime: 96.8, avgDelay: 1.1 },
]

export default function Analytics() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-600 mt-1">Performance metrics and insights</p>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Bar Chart */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Weekly Delivery Performance</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={weeklyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="onTime" fill="#10b981" name="On Time" />
                <Bar dataKey="delayed" fill="#ef4444" name="Delayed" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pie Chart */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Shipments by Region</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={regionData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {regionData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Data Table */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Recent Performance</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4 font-medium text-gray-600">Date</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Shipments</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">On-Time %</th>
                <th className="text-left py-3 px-4 font-medium text-gray-600">Avg Delay (hrs)</th>
              </tr>
            </thead>
            <tbody>
              {tableData.map((row) => (
                <tr key={row.date} className="border-b hover:bg-gray-50">
                  <td className="py-3 px-4">{row.date}</td>
                  <td className="py-3 px-4">{row.shipments.toLocaleString()}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded-full text-sm ${
                      row.onTime >= 96 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                    }`}>
                      {row.onTime}%
                    </span>
                  </td>
                  <td className="py-3 px-4">{row.avgDelay}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
