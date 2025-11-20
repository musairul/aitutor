import { useState } from 'react'

function FlashCard({ data, onFlip, onComplete }) {
  const [isFlipped, setIsFlipped] = useState(false)
  const [hasFlipped, setHasFlipped] = useState(false)

  // Validate data
  if (!data || !data.front || !data.back) {
    return (
      <div className="card bg-base-100 shadow-xl">
        <div className="card-body">
          <div className="alert alert-error">
            <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 className="font-bold">Invalid Flashcard Data</h3>
              <div className="text-sm">This flashcard is missing front or back content.</div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const handleFlip = () => {
    setIsFlipped(!isFlipped)
    if (onFlip) onFlip()
    
    // Mark as complete after first flip to see answer
    if (!hasFlipped && !isFlipped) {
      setHasFlipped(true)
      if (onComplete) {
        setTimeout(() => onComplete(), 500) // Small delay to ensure user sees the answer
      }
    }
  }

  return (
    <div className="card bg-base-100 shadow-xl cursor-pointer" onClick={handleFlip}>
      <div className="card-body items-center text-center min-h-[300px] flex justify-center">
        {!isFlipped ? (
          <div>
            <h2 className="card-title text-2xl mb-4">Question</h2>
            <p className="text-xl">{data.front}</p>
            <p className="text-sm text-gray-500 mt-8">Click to flip</p>
          </div>
        ) : (
          <div>
            <h2 className="card-title text-2xl mb-4 text-success">Answer</h2>
            <p className="text-xl">{data.back}</p>
            <p className="text-sm text-gray-500 mt-8">Click to flip back</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default FlashCard
