import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'
import axios from 'axios'

function PracticeExercise({ data, onComplete, onInteract, componentId }) {
  const [answers, setAnswers] = useState({})
  const [submitted, setSubmitted] = useState(false)
  const [grading, setGrading] = useState(false)
  const [gradingResults, setGradingResults] = useState(null)
  const [startTime] = useState(Date.now())

  // Validate data structure
  const hasAccounts = data.accounts && data.accounts.length > 0
  const hasQuestions = data.analysis_questions && data.analysis_questions.length > 0
  
  if (!hasAccounts || !hasQuestions) {
    return (
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <div className="alert alert-error">
            <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 className="font-bold">Incomplete Exercise</h3>
              <div className="text-sm">
                This exercise was not properly generated. 
                {!hasAccounts && <div>• Missing accounts/passages</div>}
                {!hasQuestions && <div>• Missing analysis questions</div>}
                <div className="mt-2">Please click Next to continue with the lesson.</div>
              </div>
            </div>
          </div>
          {onComplete && (
            <button onClick={onComplete} className="btn btn-primary mt-4">
              Continue to Next Component
            </button>
          )}
        </div>
      </div>
    )
  }

  useEffect(() => {
    // Track when component is viewed
    if (onInteract) {
      onInteract({ 
        action: 'view',
        questionCount: data.analysis_questions?.length || 0,
        accountCount: data.accounts?.length || 0
      })
    }
  }, [])

  const handleAnswerChange = (questionId, value) => {
    setAnswers({
      ...answers,
      [questionId]: value
    })
    
    // Track answer input
    if (onInteract) {
      onInteract({
        action: 'answer_input',
        questionId,
        answerLength: value.length
      })
    }
  }

  const handleSubmit = async () => {
    // Check if all questions have been answered
    const allAnswered = data.analysis_questions.every((q, idx) => 
      answers[idx] && answers[idx].trim().length > 0
    )
    
    if (!allAnswered) {
      alert('Please answer all questions before submitting')
      return
    }
    
    // Track submission with telemetry
    const timeSpent = (Date.now() - startTime) / 1000
    if (onInteract) {
      onInteract({
        action: 'submit',
        timeSpent,
        answerLengths: Object.values(answers).map(a => a.length),
        totalCharacters: Object.values(answers).reduce((sum, a) => sum + a.length, 0)
      })
    }
    
    setSubmitted(true)
    setGrading(true)
    
    // Submit for grading
    try {
      const token = localStorage.getItem('token')
      const response = await axios.post(
        `http://localhost:5000/api/lesson/components/${componentId}/grade`,
        { answers },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      
      setGradingResults(response.data)
      
      // Track grading results in telemetry
      if (onInteract) {
        onInteract({
          action: 'grading_received',
          overall_score: response.data.overall_score,
          overall_grade: response.data.overall_grade,
          question_scores: response.data.question_results.map(q => q.score)
        })
      }
    } catch (error) {
      console.error('Error grading answers:', error)
      alert('Failed to grade answers. Please try again.')
      setSubmitted(false)
    } finally {
      setGrading(false)
      if (onComplete) {
        onComplete()
      }
    }
  }

  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <h2 className="card-title text-2xl mb-4">{data.title}</h2>
        
        {/* Instructions */}
        <div className="alert alert-info mb-6">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-current shrink-0 w-6 h-6">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
              {data.instructions}
            </ReactMarkdown>
          </div>
        </div>

        {/* Accounts */}
        <div className="space-y-6 mb-8">
          {data.accounts && data.accounts.map((account) => (
            <div key={account.id} className="bg-base-200 p-6 rounded-lg">
              <h3 className="font-bold text-lg mb-3">{account.title}</h3>
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                  {account.text}
                </ReactMarkdown>
              </div>
            </div>
          ))}
        </div>

        {/* Analysis Questions */}
        <div className="space-y-6">
          <h3 className="font-bold text-xl mb-4">Analysis Questions</h3>
          {data.analysis_questions && data.analysis_questions.map((question, idx) => (
            <div key={idx} className="form-control">
              <label className="label">
                <span className="label-text font-semibold">
                  Question {idx + 1}:
                </span>
              </label>
              <div className="prose prose-sm max-w-none mb-2">
                <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                  {question.question}
                </ReactMarkdown>
              </div>
              <textarea
                className="textarea textarea-bordered h-32"
                placeholder="Type your answer here..."
                value={answers[idx] || ''}
                onChange={(e) => handleAnswerChange(idx, e.target.value)}
                disabled={submitted}
              />
            </div>
          ))}
        </div>

        {/* Submit Button */}
        {!submitted ? (
          <button 
            onClick={handleSubmit}
            className="btn btn-primary mt-6"
          >
            Submit Answers for Grading
          </button>
        ) : grading ? (
          <div className="alert mt-6">
            <span className="loading loading-spinner"></span>
            <span>Grading your answers...</span>
          </div>
        ) : gradingResults ? (
          <div className="mt-6 space-y-4">
            {/* Overall Results */}
            <div className={`alert ${
              gradingResults.overall_score >= 90 ? 'alert-success' :
              gradingResults.overall_score >= 70 ? 'alert-info' :
              gradingResults.overall_score >= 50 ? 'alert-warning' :
              'alert-error'
            }`}>
              <div className="flex flex-col w-full">
                <div className="flex items-center gap-3 mb-2">
                  <div className="text-3xl font-bold">{gradingResults.overall_grade}</div>
                  <div>
                    <div className="text-lg font-semibold">
                      Overall Score: {gradingResults.overall_score}%
                    </div>
                    <div className="text-sm opacity-90">
                      {gradingResults.overall_feedback}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Individual Question Results */}
            <div className="space-y-3">
              <h3 className="font-bold text-lg">Detailed Feedback</h3>
              {gradingResults.question_results.map((result, idx) => (
                <div key={idx} className="card bg-base-200">
                  <div className="card-body">
                    <div className="flex items-start justify-between">
                      <h4 className="font-semibold">Question {result.question_number}</h4>
                      <div className={`badge ${
                        result.score >= 90 ? 'badge-success' :
                        result.score >= 70 ? 'badge-info' :
                        result.score >= 50 ? 'badge-warning' :
                        'badge-error'
                      }`}>
                        {result.score}%
                      </div>
                    </div>
                    
                    <div className="text-sm space-y-2 mt-2">
                      {result.strengths && (
                        <div>
                          <span className="font-semibold text-success">✓ Strengths: </span>
                          <span>{result.strengths}</span>
                        </div>
                      )}
                      
                      {result.weaknesses && (
                        <div>
                          <span className="font-semibold text-warning">⚠ Areas for Improvement: </span>
                          <span>{result.weaknesses}</span>
                        </div>
                      )}
                      
                      {result.feedback && (
                        <div className="mt-2 p-3 bg-base-300 rounded">
                          <span className="font-semibold">💡 Feedback: </span>
                          <span>{result.feedback}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Next Steps */}
            {gradingResults.next_steps && (
              <div className="alert alert-info">
                <div>
                  <div className="font-semibold">📚 Next Steps:</div>
                  <div className="text-sm mt-1">{gradingResults.next_steps}</div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="alert alert-success mt-6">
            <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Your answers have been submitted.</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default PracticeExercise
