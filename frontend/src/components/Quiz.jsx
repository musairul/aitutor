import { useState, useEffect } from 'react'

function Quiz({ data, onAnswer, onComplete }) {
  const [selectedAnswer, setSelectedAnswer] = useState(null)
  const [showResult, setShowResult] = useState(false)
  const [startTime] = useState(Date.now())

  // Validate data
  if (!data || !data.options || !Array.isArray(data.options)) {
    return (
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <div className="alert alert-error">
            <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 className="font-bold">Invalid Quiz Data</h3>
              <div className="text-sm">This quiz is missing options or question data.</div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const handleAnswer = (index) => {
    if (showResult) return
    
    setSelectedAnswer(index)
    setShowResult(true)
    
    const isCorrect = index === data.correct
    const timeToAnswer = (Date.now() - startTime) / 1000
    
    if (onAnswer) {
      onAnswer(isCorrect, timeToAnswer)
    }
    
    // Mark as complete after answering
    if (onComplete) {
      onComplete()
    }
  }

  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <h2 className="card-title text-2xl mb-6">{data.question}</h2>
        
        <div className="space-y-3">
          {data.options.map((option, index) => (
            <button
              key={index}
              onClick={() => handleAnswer(index)}
              disabled={showResult}
              className={`btn btn-outline w-full justify-start text-left h-auto py-4 ${
                showResult
                  ? index === data.correct
                    ? 'btn-success'
                    : selectedAnswer === index
                    ? 'btn-error'
                    : ''
                  : ''
              }`}
            >
              <span className="mr-2 font-bold">{String.fromCharCode(65 + index)}.</span>
              {option}
            </button>
          ))}
        </div>

        {showResult && (
          <div className={`alert mt-6 ${selectedAnswer === data.correct ? 'alert-success' : 'alert-error'}`}>
            <div className="w-full">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">
                  {selectedAnswer === data.correct ? '✓' : '✗'}
                </span>
                <span className="font-bold text-lg">
                  {selectedAnswer === data.correct ? 'Correct!' : 'Incorrect'}
                </span>
              </div>
              
              {/* Show correct answer if user was wrong */}
              {selectedAnswer !== data.correct && (
                <div className="mb-2">
                  <span className="font-semibold">Correct answer: </span>
                  <span>{data.options[data.correct]}</span>
                </div>
              )}
              
              {/* Always show explanation */}
              {data.explanation && (
                <div className="mt-2 p-3 bg-base-100 bg-opacity-20 rounded">
                  <span className="font-semibold">Explanation: </span>
                  <span>{data.explanation}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Quiz
