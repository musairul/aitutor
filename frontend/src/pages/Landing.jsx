import { Link } from 'react-router-dom'

function Landing() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-base-200">
      <div className="text-center">
        <h1 className="text-5xl font-bold mb-8">🎓 AI Tutor</h1>
        <p className="text-xl mb-8">Your personalized learning companion</p>
        <div className="space-x-4">
          <Link to="/login" className="btn btn-primary">Login</Link>
          <Link to="/signup" className="btn btn-secondary">Sign Up</Link>
        </div>
      </div>
    </div>
  )
}

export default Landing
