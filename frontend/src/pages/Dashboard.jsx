import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api'

function Dashboard({ onLogout }) {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/lesson/dashboard')
      setDashboardData(response.data)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-base-200">
      <div className="navbar bg-base-100">
        <div className="flex-1">
          <Link to="/dashboard" className="btn btn-ghost text-xl">🎓 AI Tutor</Link>
        </div>
        <div className="flex-none">
          <button onClick={onLogout} className="btn btn-ghost">Logout</button>
        </div>
      </div>

      <div className="container mx-auto p-8">
        <h1 className="text-4xl font-bold mb-8">Dashboard</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Latest Lesson Card */}
          {dashboardData?.latest_lesson ? (
            <div className="card bg-base-100 shadow-xl">
              <div className="card-body">
                <h2 className="card-title">Continue Learning</h2>
                <p className="text-3xl">{dashboardData.latest_lesson.module_emoji}</p>
                <p className="font-semibold">{dashboardData.latest_lesson.module_name}</p>
                <p className="text-sm">{dashboardData.latest_lesson.lesson_title}</p>
                <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
                  <div 
                    className="bg-primary h-2.5 rounded-full" 
                    style={{ width: `${dashboardData.latest_lesson.progress_percentage}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {Math.round(dashboardData.latest_lesson.progress_percentage)}% Complete
                </p>
                <div className="card-actions justify-end mt-4">
                  <button 
                    onClick={() => navigate(`/lesson/${dashboardData.latest_lesson.lesson_id}`)}
                    className="btn btn-primary btn-sm"
                  >
                    Continue
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="card bg-base-100 shadow-xl">
              <div className="card-body">
                <h2 className="card-title">No Active Lessons</h2>
                <p>Create a module to get started!</p>
              </div>
            </div>
          )}

          {/* Modules Card */}
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title">My Modules</h2>
              <p className="text-5xl font-bold">{dashboardData?.modules_count || 0}</p>
              <p className="text-sm text-gray-500">Total modules</p>
              <div className="card-actions justify-end mt-4">
                <Link to="/modules" className="btn btn-secondary btn-sm">
                  View Modules
                </Link>
              </div>
            </div>
          </div>

          {/* Insights Card */}
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title">Insights</h2>
              {dashboardData?.insights && dashboardData.insights.length > 0 ? (
                <div className="space-y-2">
                  {dashboardData.insights.slice(0, 3).map((insight, idx) => (
                    <div key={idx} className="text-sm border-l-2 border-primary pl-2">
                      {insight.text}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">Complete lessons to see personalized insights</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
