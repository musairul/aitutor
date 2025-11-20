import { useState, useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import api from '../api'

function WeekDetail({ onLogout }) {
  const { weekId } = useParams()
  const [week, setWeek] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchWeek()
  }, [weekId])

  const fetchWeek = async () => {
    try {
      const response = await api.get(`/modules/weeks/${weekId}`)
      setWeek(response.data)
    } catch (error) {
      console.error('Error fetching week:', error)
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

  if (!week) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Week not found</p>
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
          <Link to="/modules" className="btn btn-ghost">Modules</Link>
          <Link to="/dashboard" className="btn btn-ghost">Dashboard</Link>
          <button onClick={onLogout} className="btn btn-ghost">Logout</button>
        </div>
      </div>

      <div className="container mx-auto p-8 max-w-6xl">
        <div className="mb-8">
          <Link to={`/modules/${week.module_id}`} className="btn btn-ghost btn-sm mb-4">
            ← Back to Module
          </Link>
          <h1 className="text-4xl font-bold mb-2">Week {week.week_number}: {week.title}</h1>
          <p className="text-gray-500">{week.lessons.length} lessons</p>
        </div>

        <div className="grid gap-6">
          {week.lessons.map((lesson) => (
            <div key={lesson.id} className="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow">
              <div className="card-body">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h2 className="card-title text-2xl mb-2">
                      Lesson {lesson.lesson_number}: {lesson.title}
                    </h2>
                    
                    {lesson.completed && (
                      <div className="badge badge-success gap-2 mb-3">
                        ✅ Completed
                      </div>
                    )}
                    
                    {!lesson.completed && lesson.progress_percentage > 0 && (
                      <div>
                        <div className="badge badge-info gap-2 mb-2">
                          In Progress
                        </div>
                        <div className="w-full bg-base-300 rounded-full h-2 mb-3">
                          <div 
                            className="bg-primary h-2 rounded-full transition-all" 
                            style={{ width: `${lesson.progress_percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                <div className="card-actions justify-end mt-4">
                  <Link 
                    to={`/lessons/${lesson.id}`}
                    className="btn btn-primary"
                  >
                    {lesson.completed ? 'Review →' : lesson.progress_percentage > 0 ? 'Continue →' : 'Start →'}
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default WeekDetail
