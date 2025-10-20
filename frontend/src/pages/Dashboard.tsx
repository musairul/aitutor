import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary-600">AI Tutor</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">
                {user?.full_name || user?.email}
              </span>
              <button
                onClick={handleLogout}
                className="bg-primary-600 text-white hover:bg-primary-700 px-4 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Welcome Section */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Welcome back, {user?.full_name || 'Student'}!
          </h2>
          <p className="text-gray-600">
            Ready to continue your learning journey? Let's make today productive!
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Total Sessions</p>
                <p className="text-3xl font-bold text-primary-600">0</p>
              </div>
              <div className="text-4xl">📚</div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Learning Hours</p>
                <p className="text-3xl font-bold text-primary-600">0</p>
              </div>
              <div className="text-4xl">⏱️</div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Topics Covered</p>
                <p className="text-3xl font-bold text-primary-600">0</p>
              </div>
              <div className="text-4xl">✨</div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-md p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button className="p-6 border-2 border-primary-200 rounded-lg hover:bg-primary-50 text-left transition">
              <div className="text-3xl mb-2">🚀</div>
              <h4 className="text-lg font-semibold text-gray-900 mb-1">Start New Session</h4>
              <p className="text-sm text-gray-600">Begin a new AI tutoring session</p>
            </button>
            
            <button className="p-6 border-2 border-primary-200 rounded-lg hover:bg-primary-50 text-left transition">
              <div className="text-3xl mb-2">📖</div>
              <h4 className="text-lg font-semibold text-gray-900 mb-1">Review Progress</h4>
              <p className="text-sm text-gray-600">Check your learning progress and history</p>
            </button>
            
            <button className="p-6 border-2 border-primary-200 rounded-lg hover:bg-primary-50 text-left transition">
              <div className="text-3xl mb-2">🎯</div>
              <h4 className="text-lg font-semibold text-gray-900 mb-1">Set Goals</h4>
              <p className="text-sm text-gray-600">Define your learning objectives</p>
            </button>
            
            <button className="p-6 border-2 border-primary-200 rounded-lg hover:bg-primary-50 text-left transition">
              <div className="text-3xl mb-2">⚙️</div>
              <h4 className="text-lg font-semibold text-gray-900 mb-1">Settings</h4>
              <p className="text-sm text-gray-600">Customize your learning experience</p>
            </button>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">Recent Activity</h3>
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📝</div>
            <p className="text-gray-600">No recent activity yet</p>
            <p className="text-sm text-gray-500 mt-2">
              Start your first session to see your activity here
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
