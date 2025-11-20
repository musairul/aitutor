import { useState, useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import api from '../api'
import InfoCard from '../components/InfoCard'
import FlashCard from '../components/FlashCard'
import Quiz from '../components/Quiz'
import MindMap from '../components/MindMap'
import PracticeExercise from '../components/PracticeExercise'
import CustomComponent from '../components/CustomComponent'

function Lesson({ onLogout }) {
  const { lessonId } = useParams()
  const [lesson, setLesson] = useState(null)
  const [loading, setLoading] = useState(true)
  const [currentComponentIndex, setCurrentComponentIndex] = useState(0)
  const [visibleComponents, setVisibleComponents] = useState([0]) // Track which components to show
  const [startTime, setStartTime] = useState(Date.now())
  const [adaptiveInsights, setAdaptiveInsights] = useState([])
  const [componentCompletionStatus, setComponentCompletionStatus] = useState({}) // Track which components are completed
  const [moduleId, setModuleId] = useState(null)
  const [nextLesson, setNextLesson] = useState(null)
  const [isGeneratingComponents, setIsGeneratingComponents] = useState(false)
  const [canComplete, setCanComplete] = useState(false)
  const [evaluation, setEvaluation] = useState(null)
  const [showInsightsPanel, setShowInsightsPanel] = useState(true)
  const [allInsights, setAllInsights] = useState([]) // Store all insights from evaluation

  useEffect(() => {
    // Clear all lesson-specific state when switching lessons
    setAllInsights([])
    setLesson(null)
    setCurrentComponentIndex(0)
    setVisibleComponents([0])
    setCanComplete(false)
    setEvaluation(null)
    setNextLesson(null)
    setModuleId(null)
    setComponentCompletionStatus({})
    fetchLesson()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lessonId])

  useEffect(() => {
    setStartTime(Date.now())
  }, [currentComponentIndex])

  const fetchLesson = async () => {
    try {
      const response = await api.get(`/lesson/${lessonId}`)
      console.log('Lesson data:', response.data)
      setLesson(response.data)
      
      // Store module_id and next_lesson info if available
      if (response.data.module_id) {
        setModuleId(response.data.module_id)
      }
      if (response.data.next_lesson) {
        setNextLesson(response.data.next_lesson)
      }
      
      // Fetch user insights from dashboard to display in panel
      try {
        const dashboardResponse = await api.get('/lesson/dashboard')
        if (dashboardResponse.data.insights && dashboardResponse.data.insights.length > 0) {
          const userInsights = dashboardResponse.data.insights.map(insight => ({
            type: insight.type || 'general',
            content: insight.text,
            timestamp: Date.now()
          }))
          setAllInsights(prev => {
            // Avoid duplicates
            const existingContents = new Set(prev.map(i => i.content))
            const newInsights = userInsights.filter(i => !existingContents.has(i.content))
            return [...newInsights, ...prev]
          })
        }
      } catch (err) {
        console.error('Error fetching insights:', err)
      }
      
      // If lesson is completed, show all components for review
      if (response.data.progress.completed) {
        console.log('Lesson is completed - showing all components for review')
        setCurrentComponentIndex(response.data.components.length)
        setVisibleComponents(
          Array.from({ length: response.data.components.length }, (_, i) => i)
        )
        console.log('Visible components:', Array.from({ length: response.data.components.length }, (_, i) => i))
      } else {
        console.log('Lesson in progress')
        setCurrentComponentIndex(response.data.progress.current_component_index)
        setVisibleComponents(
          Array.from({ length: response.data.progress.current_component_index + 1 }, (_, i) => i)
        )
      }
      
      // Start lesson if no components yet
      if (!response.data.components || response.data.components.length === 0) {
        if (isGeneratingComponents) {
          console.log('⚠️ Already generating components, skipping...')
          return
        }
        
        console.log('No components found - generating...')
        setIsGeneratingComponents(true)
        
        try {
          await api.post(`/lesson/${lessonId}/start`)
          // Refetch to get generated components
          const updatedResponse = await api.get(`/lesson/${lessonId}`)
          setLesson(updatedResponse.data)
        } finally {
          setIsGeneratingComponents(false)
        }
      }
    } catch (error) {
      console.error('Error fetching lesson:', error)
    } finally {
      setLoading(false)
    }
  }

  const trackTelemetry = async (eventType, eventData) => {
    try {
      await api.post('/telemetry/track', {
        lesson_id: Number.parseInt(lessonId),
        component_id: lesson.components[currentComponentIndex]?.id,
        event_type: eventType,
        event_data: eventData
      })
    } catch (error) {
      console.error('Error tracking telemetry:', error)
    }
  }

  const markComponentComplete = (componentIndex) => {
    setComponentCompletionStatus({
      ...componentCompletionStatus,
      [componentIndex]: true
    })
  }

  const isCurrentComponentComplete = () => {
    const currentComponent = lesson?.components[currentComponentIndex]
    if (!currentComponent) return false
    
    // Info cards are always considered complete (just need to read)
    if (currentComponent.type === 'info_card') return true
    
    // Check if component has been marked complete
    return componentCompletionStatus[currentComponentIndex] === true
  }

  const handleNext = async () => {
    // Track time spent on current component
    const timeSpent = (Date.now() - startTime) / 1000
    await trackTelemetry('time_spent', {
      component_type: lesson.components[currentComponentIndex]?.type,
      time_seconds: timeSpent
    })

    // Move to next component
    const nextIndex = currentComponentIndex + 1
    setCurrentComponentIndex(nextIndex)
    
    // Add next component to visible list
    if (!visibleComponents.includes(nextIndex)) {
      setVisibleComponents([...visibleComponents, nextIndex])
    }

    // Update progress
    const response = await api.post(`/lesson/${lessonId}/next-component`, {
      current_index: currentComponentIndex
    })
    
    // Check if we can complete the lesson
    if (response.data.can_complete) {
      setCanComplete(true)
      setEvaluation(response.data.evaluation)
    }
    
    // Add evaluation insights to the insights panel
    if (response.data.evaluation) {
      const evalData = response.data.evaluation
      const newInsights = []
      
      // Add performance summary
      if (evalData.evaluation?.performance_summary) {
        newInsights.push({
          type: 'performance',
          content: evalData.evaluation.performance_summary,
          timestamp: Date.now()
        })
      }
      
      // Add understood concepts
      if (evalData.evaluation?.understood_concepts?.length > 0) {
        evalData.evaluation.understood_concepts.forEach(concept => {
          newInsights.push({
            type: 'strength',
            content: concept,
            timestamp: Date.now()
          })
        })
      }
      
      // Add weak areas
      if (evalData.evaluation?.weak_areas?.length > 0) {
        evalData.evaluation.weak_areas.forEach(area => {
          newInsights.push({
            type: 'weakness',
            content: area,
            timestamp: Date.now()
          })
        })
      }
      
      // Add focus area from recommendation
      if (evalData.recommendation?.focus_area) {
        newInsights.push({
          type: 'focus',
          content: `Focus: ${evalData.recommendation.focus_area}`,
          timestamp: Date.now()
        })
      }
      
      // Add recommendation reason
      if (evalData.recommendation?.reason) {
        newInsights.push({
          type: 'recommendation',
          content: evalData.recommendation.reason,
          timestamp: Date.now()
        })
      }
      
      // Add learning style detected
      if (evalData.evaluation?.learning_style_detected) {
        newInsights.push({
          type: 'learning_style',
          content: `Your learning style: ${evalData.evaluation.learning_style_detected}`,
          timestamp: Date.now()
        })
      }
      
      // Add adaptive phase improvement if present
      if (evalData.evaluation?.adaptive_phase_improvement && evalData.evaluation.adaptive_phase_improvement !== 'none') {
        newInsights.push({
          type: 'improvement',
          content: `Adaptive phase improvement: ${evalData.evaluation.adaptive_phase_improvement}`,
          timestamp: Date.now()
        })
      }
      
      if (newInsights.length > 0) {
        setAllInsights(prev => [...prev, ...newInsights])
      }
    }
    
    // Check if an adaptive component was generated - only show message once
    if (response.data.adaptive_component_generated && response.data.adaptive_reason) {
      // Add to insights panel instead of toast
      setAllInsights(prev => [...prev, {
        type: 'personalization',
        content: response.data.adaptive_reason,
        timestamp: Date.now()
      }])
    }

    // Refetch lesson to get any new components generated
    await fetchLesson()
    
    // Scroll to new component
    setTimeout(() => {
      const element = document.getElementById(`component-${nextIndex}`)
      element?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }, 100)
  }

  const renderComponent = (component, componentIndex) => {
    if (!component) return null
    
    const isCurrentComp = componentIndex === currentComponentIndex

    switch (component.type) {
      case 'info_card':
        return (
          <InfoCard 
            data={component.data}
            onView={(data) => trackTelemetry('info_card_view', data)}
          />
        )
      case 'flashcard':
        return (
          <FlashCard 
            data={component.data} 
            onFlip={() => trackTelemetry('card_flip', {})}
            onComplete={() => isCurrentComp && markComponentComplete(componentIndex)}
          />
        )
      case 'quiz':
        return (
          <Quiz 
            data={component.data}
            onAnswer={(isCorrect, timeToAnswer) => {
              trackTelemetry('quiz_answer', { 
                correct: isCorrect, 
                time_seconds: timeToAnswer,
                question: component.data.question
              })
            }}
            onComplete={() => isCurrentComp && markComponentComplete(componentIndex)}
          />
        )
      case 'mindmap':
        return (
          <MindMap 
            data={component.data}
            onInteract={() => {
              trackTelemetry('mindmap_interact', {})
              if (isCurrentComp) markComponentComplete(componentIndex)
            }}
          />
        )
      case 'practice_exercise':
        return (
          <PracticeExercise
            data={component.data}
            componentId={component.id}
            onComplete={() => isCurrentComp && markComponentComplete(componentIndex)}
            onInteract={(eventData) => trackTelemetry('practice_interaction', eventData)}
          />
        )
      case 'custom':
        return (
          <CustomComponent
            data={component.data}
            onComplete={() => isCurrentComp && markComponentComplete(componentIndex)}
            onTrackEvent={(eventType, eventData) => trackTelemetry(eventType, eventData)}
          />
        )
      default:
        return (
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <p>Component type: {component.type}</p>
              <pre className="text-xs overflow-auto">{JSON.stringify(component.data, null, 2)}</pre>
            </div>
          </div>
        )
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    )
  }

  if (!lesson) {
    return <div className="min-h-screen flex items-center justify-center">
      <p>Lesson not found</p>
    </div>
  }

  // Check if we have components
  if (!lesson.components || lesson.components.length === 0) {
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
        <div className="container mx-auto p-8 max-w-4xl">
          <div className="text-center">
            <span className="loading loading-spinner loading-lg"></span>
            <p className="mt-4">Generating lesson components...</p>
          </div>
        </div>
      </div>
    )
  }

  const isReviewMode = lesson.progress.completed
  const currentComponent = lesson.components[currentComponentIndex]
  const isLastComponent = currentComponentIndex >= lesson.components.length - 1

  return (
    <div className="min-h-screen bg-base-200">
      <div className="navbar bg-base-100 sticky top-0 z-50 shadow-md">
        <div className="flex-1">
          <Link to="/dashboard" className="btn btn-ghost text-xl">🎓 AI Tutor</Link>
        </div>
        <div className="flex-none">
          <Link to="/modules" className="btn btn-ghost">Modules</Link>
          <Link to="/dashboard" className="btn btn-ghost">Dashboard</Link>
          <button onClick={onLogout} className="btn btn-ghost">Logout</button>
        </div>
      </div>

      <div className="flex h-[calc(100vh-4rem)]">
        {/* Insights Panel - Collapsible and Fixed */}
        <div className={`bg-base-100 shadow-xl transition-all duration-300 ${showInsightsPanel ? 'w-80' : 'w-12'} flex-shrink-0 overflow-hidden sticky top-16 h-full`}>
          {/* Toggle Button */}
          <button
            onClick={() => setShowInsightsPanel(!showInsightsPanel)}
            className="btn btn-ghost btn-sm w-full justify-start p-3 sticky top-0 bg-base-100 z-10"
          >
            {showInsightsPanel ? '◀' : '▶'} {showInsightsPanel && 'AI Insights'}
          </button>
          
          {/* Insights Content */}
          {showInsightsPanel && (
            <div className="p-4 overflow-y-auto h-[calc(100%-3rem)]">
              <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                🤖 Learning Insights
              </h3>
              
              {allInsights.length === 0 ? (
                <div className="text-sm text-gray-500 text-center py-8">
                  <p>Complete components to receive personalized insights from the AI.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {[...allInsights].reverse().map((insight, idx) => (
                    <div
                      key={idx}
                      className={`p-3 rounded-lg text-sm ${
                        insight.type === 'strength' ? 'bg-success bg-opacity-10 border-l-4 border-success' :
                        insight.type === 'weakness' ? 'bg-warning bg-opacity-10 border-l-4 border-warning' :
                        insight.type === 'focus' ? 'bg-accent bg-opacity-10 border-l-4 border-accent' :
                        insight.type === 'recommendation' ? 'bg-info bg-opacity-10 border-l-4 border-info' :
                        insight.type === 'personalization' ? 'bg-primary bg-opacity-10 border-l-4 border-primary' :
                        insight.type === 'learning_style' ? 'bg-secondary bg-opacity-10 border-l-4 border-secondary' :
                        insight.type === 'improvement' ? 'bg-success bg-opacity-20 border-l-4 border-success' :
                        insight.type === 'performance' ? 'bg-base-300 border-l-4 border-base-content' :
                        'bg-base-200 border-l-4 border-base-300'
                      }`}
                    >
                      <div className="font-semibold mb-1 flex items-center gap-1">
                        {insight.type === 'strength' && '✅ Understood'}
                        {insight.type === 'weakness' && '⚠️ Needs Work'}
                        {insight.type === 'focus' && '🎯 Focus Area'}
                        {insight.type === 'recommendation' && '💡 Next Steps'}
                        {insight.type === 'personalization' && '🤖 AI Personalization'}
                        {insight.type === 'performance' && '📊 Performance'}
                        {insight.type === 'learning_style' && '🎨 Learning Style'}
                        {insight.type === 'improvement' && '📈 Progress'}
                        {insight.type === 'preference' && '👤 Preference'}
                        {!['strength', 'weakness', 'focus', 'recommendation', 'personalization', 'performance', 'learning_style', 'improvement', 'preference'].includes(insight.type) && '💬 Insight'}
                      </div>
                      <p className="text-xs opacity-90">{insight.content}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-y-auto">
          <div className="container mx-auto p-8 max-w-4xl">
            {/* Review Mode Banner */}
            {lesson.progress.completed && (
          <div className="alert alert-info mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-current shrink-0 w-6 h-6">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <div>
              <h3 className="font-bold">Review Mode</h3>
              <div className="text-sm">
                You've already completed this lesson. All components are shown below for your review.
              </div>
            </div>
          </div>
        )}
        
        {/* Lesson Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <h1 className="text-4xl font-bold">{lesson.title}</h1>
            {lesson.progress.completed && (
              <div className="badge badge-success gap-1 badge-lg">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                </svg>
                Completed
              </div>
            )}
          </div>
          
          {/* Progress Bar - only show if not completed */}
          {!lesson.progress.completed && (
            <>
              <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
                <div 
                  className="bg-primary h-2.5 rounded-full transition-all" 
                  style={{ width: `${lesson.progress.percentage}%` }}
                ></div>
              </div>
              <p className="text-sm text-gray-500">
                {Math.round(lesson.progress.percentage)}% Complete • 
                Component {currentComponentIndex + 1} of {lesson.components.length}
              </p>
            </>
          )}

          {/* Objectives */}
          <div className="mt-6">
            <h2 className="text-xl font-semibold mb-3">Learning Objectives</h2>
            <ul className="space-y-2">
              {lesson.objectives.map((obj) => (
                <li key={obj.id} className="flex items-start">
                  <span className={`mr-2 ${obj.completed ? 'text-success' : 'text-gray-400'}`}>
                    {obj.completed ? '✅' : '⬜'}
                  </span>
                  <span className={obj.completed ? 'line-through text-gray-500' : ''}>
                    {obj.text}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Component Display - Show all visible components stacked */}
        <div className="space-y-6 mb-8">
          {visibleComponents.length > 0 ? visibleComponents.map((index) => {
            const component = lesson.components[index]
            if (!component) {
              console.log(`Component at index ${index} is undefined`)
              return null
            }
            
            const isCurrentComponent = isReviewMode ? false : (index === currentComponentIndex)
            
            return (
              <div 
                key={index}
                id={`component-${index}`}
                className={`transition-all ${isCurrentComponent ? '' : isReviewMode ? '' : 'opacity-75'}`}
              >
                <div className="mb-2 text-sm font-medium text-gray-500">
                  Component {index + 1} of {lesson.components.length}
                </div>
                {renderComponent(component, index)}
              </div>
            )
          }) : (
            <div className="text-center text-gray-500">
              <p>No components to display</p>
            </div>
          )}
          
          {/* Completion Screen - Only show when canComplete is true */}
          {currentComponentIndex >= lesson.components.length && canComplete && (
            <div className="card bg-base-100 shadow-xl">
              <div className="card-body text-center">
                <h2 className="card-title justify-center">
                  🎉 Learning Objectives Mastered!
                </h2>
                <p>
                  Great job! You've successfully mastered all the learning objectives for this lesson.
                </p>
                
                {/* Show evaluation summary if available */}
                {evaluation && (
                  <div className="mt-4 text-left bg-base-200 p-4 rounded-lg">
                    <h3 className="font-bold mb-2">📊 Your Performance:</h3>
                    <p className="text-sm mb-2">{evaluation.evaluation?.performance_summary}</p>
                    {evaluation.evaluation?.understood_concepts && evaluation.evaluation.understood_concepts.length > 0 && (
                      <div className="mb-2">
                        <span className="font-semibold">✅ Mastered:</span>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {evaluation.evaluation.understood_concepts.map((concept, idx) => (
                            <span key={idx} className="badge badge-success whitespace-normal text-left h-auto py-2">{concept}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    <p className="text-sm mt-2">
                      <span className="font-semibold">🎯 Learning Style:</span> {evaluation.evaluation?.learning_style_detected || 'Mixed'}
                    </p>
                  </div>
                )}
                
                <div className="card-actions justify-center mt-4 gap-3">
                  <Link to={moduleId ? `/modules/${moduleId}` : '/modules'} className="btn btn-outline">
                    ← Back to Lessons
                  </Link>
                  {nextLesson && (
                    <Link to={`/lesson/${nextLesson.id}`} className="btn btn-primary">
                      Next Lesson: {nextLesson.title} →
                    </Link>
                  )}
                  {!nextLesson && (
                    <Link to={moduleId ? `/modules/${moduleId}` : '/modules'} className="btn btn-primary">
                      Continue Learning →
                    </Link>
                  )}
                </div>
              </div>
            </div>
          )}
          
          {/* Still Learning Message - Show when at end but objectives not met */}
          {currentComponentIndex >= lesson.components.length && !canComplete && !isReviewMode && (
            <div className="card bg-base-100 shadow-xl border-2 border-warning">
              <div className="card-body text-center">
                <h2 className="card-title justify-center">
                  🎯 Personalized Learning in Progress
                </h2>
                <p>
                  The AI is evaluating your progress and generating a batch of personalized components to help you master the material.
                </p>
                <div className="mt-2 text-sm text-gray-600">
                  <p>📚 This batch will include both teaching and testing components</p>
                  <p>✅ Designed specifically for your learning needs</p>
                </div>
                <div className="mt-4">
                  <span className="loading loading-spinner loading-lg"></span>
                  <p className="text-sm mt-2 text-gray-500">Analyzing your learning patterns...</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Navigation - Hide in review mode */}
        {!isReviewMode && currentComponentIndex < lesson.components.length && (
          <div className="flex justify-between sticky bottom-4 bg-base-100 p-4 rounded-lg shadow-xl">
            <Link to={moduleId ? `/modules/${moduleId}` : '/modules'} className="btn btn-outline">
              ← Back to Lessons
            </Link>
            <button 
              onClick={handleNext} 
              className="btn btn-primary"
              disabled={!isCurrentComponentComplete()}
            >
              {currentComponentIndex >= lesson.components.length - 1 ? 'Continue →' : 'Next →'}
            </button>
            {!isCurrentComponentComplete() && (
              <div className="text-sm text-gray-500 absolute -top-8 right-4">
                Complete the current component to continue
              </div>
            )}
          </div>
        )}
        
        {/* Back button for review mode */}
        {isReviewMode && (
          <div className="flex justify-center sticky bottom-4 bg-base-100 p-4 rounded-lg shadow-xl">
            <Link to={moduleId ? `/modules/${moduleId}` : '/modules'} className="btn btn-primary">
              ← Back to Lessons
            </Link>
          </div>
        )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Lesson
