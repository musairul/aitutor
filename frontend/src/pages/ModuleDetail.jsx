import { useState, useEffect } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import api from '../api'

function ModuleDetail({ onLogout }) {
  const { moduleId } = useParams()
  const navigate = useNavigate()
  const [module, setModule] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchModule()
  }, [moduleId])

  const fetchModule = async () => {
    try {
      const response = await api.get(`/modules/${moduleId}`)
      setModule(response.data)
    } catch (error) {
      console.error('Error fetching module:', error)
      alert('Error loading module')
      navigate('/modules')
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

  if (!module) {
    return null
  }

  return (
    <div className="min-h-screen bg-base-200">
      <div className="navbar bg-base-100">
        <div className="flex-1">
          <Link to="/dashboard" className="btn btn-ghost text-xl">🎓 AI Tutor</Link>
        </div>
        <div className="flex-none">
          <Link to="/dashboard" className="btn btn-ghost">Dashboard</Link>
          <Link to="/modules" className="btn btn-ghost">Modules</Link>
          <button onClick={onLogout} className="btn btn-ghost">Logout</button>
        </div>
      </div>

      <div className="container mx-auto p-8">
        {/* Module Header */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="text-6xl">{module.emoji}</div>
            <div className="flex-1">
              <h1 className="text-4xl font-bold">{module.name}</h1>
              <p className="text-gray-500">
                {module.lessons?.length || 0} lessons • Processing: {module.processing_status}
              </p>
              
              {/* Overall Progress */}
              {module.lessons && module.lessons.length > 0 && (() => {
                const completedLessons = module.lessons.filter(l => l.completed).length
                const totalLessons = module.lessons.length
                const overallProgress = totalLessons > 0 ? (completedLessons / totalLessons) * 100 : 0
                
                return (
                  <div className="mt-3">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-sm font-semibold">
                        {completedLessons} of {totalLessons} lessons completed
                      </span>
                      {completedLessons === totalLessons && totalLessons > 0 && (
                        <div className="badge badge-success gap-1">
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Module Complete!
                        </div>
                      )}
                    </div>
                    <div className="w-full max-w-md bg-base-300 rounded-full h-3">
                      <div 
                        className="bg-success h-3 rounded-full transition-all duration-300"
                        style={{ width: `${overallProgress}%` }}
                      ></div>
                    </div>
                  </div>
                )
              })()}
            </div>
          </div>
        </div>

        {/* Lessons */}
        {module.lessons && module.lessons.length > 0 ? (
          <div className="space-y-3">
            {module.lessons.map((lesson) => (
              <div
                key={lesson.id}
                className="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow cursor-pointer"
                onClick={() => navigate(`/lesson/${lesson.id}`)}
              >
                <div className="card-body">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="badge badge-neutral">Lesson {lesson.lesson_number}</span>
                        <h3 className="font-semibold text-xl">{lesson.title}</h3>
                        {lesson.completed && (
                          <div className="badge badge-success gap-1">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                            </svg>
                            Completed
                          </div>
                        )}
                        {!lesson.completed && lesson.progress_percentage > 0 && (
                          <div className="badge badge-info">
                            In Progress
                          </div>
                        )}
                      </div>
                    </div>
                    <button className="btn btn-primary ml-4">
                      {lesson.completed ? 'Review →' : lesson.progress_percentage > 0 ? 'Continue →' : 'Start →'}
                    </button>
                  </div>
                  
                  {/* Progress bar for in-progress lessons */}
                  {!lesson.completed && lesson.progress_percentage > 0 && (
                    <div className="mt-3">
                      <div className="flex items-center gap-2 text-xs text-gray-600 mb-1">
                        <span>Progress</span>
                        <span className="font-semibold">{Math.round(lesson.progress_percentage)}%</span>
                      </div>
                      <div className="w-full bg-base-300 rounded-full h-2">
                        <div 
                          className="bg-primary h-2 rounded-full transition-all duration-300"
                          style={{ width: `${lesson.progress_percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <p className="text-xl text-gray-500">
              No content available yet. The module may still be processing.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default ModuleDetail
