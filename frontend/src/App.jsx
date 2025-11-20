import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'
import Modules from './pages/Modules'
import ModuleDetail from './pages/ModuleDetail'
import Lesson from './pages/Lesson'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      setIsAuthenticated(true)
    }
    setLoading(false)
  }, [])

  const login = (token) => {
    console.log('Login called with token:', token)
    localStorage.setItem('token', token)
    setIsAuthenticated(true)
  }

  const logout = () => {
    localStorage.removeItem('token')
    setIsAuthenticated(false)
  }

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">
      <span className="loading loading-spinner loading-lg"></span>
    </div>
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Landing />} />
        <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Login onLogin={login} />} />
        <Route path="/signup" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Signup onLogin={login} />} />
        <Route path="/dashboard" element={isAuthenticated ? <Dashboard onLogout={logout} /> : <Navigate to="/" />} />
        <Route path="/modules" element={isAuthenticated ? <Modules onLogout={logout} /> : <Navigate to="/" />} />
        <Route path="/modules/:moduleId" element={isAuthenticated ? <ModuleDetail onLogout={logout} /> : <Navigate to="/" />} />
        <Route path="/lesson/:lessonId" element={isAuthenticated ? <Lesson onLogout={logout} /> : <Navigate to="/" />} />
      </Routes>
    </Router>
  )
}

export default App
