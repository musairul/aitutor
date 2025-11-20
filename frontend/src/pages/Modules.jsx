import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api'
import ProcessingModal from '../components/ProcessingModal'
import EmojiPicker from '../components/EmojiPicker'

function Modules({ onLogout }) {
  const [modules, setModules] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingModule, setEditingModule] = useState(null)
  const [formData, setFormData] = useState({ name: '', emoji: '📚' })
  const [files, setFiles] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [processingModuleId, setProcessingModuleId] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    fetchModules()
  }, [])

  const fetchModules = async () => {
    try {
      const response = await api.get('/modules/')
      setModules(response.data)
    } catch (error) {
      console.error('Error fetching modules:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateModule = async (e) => {
    e.preventDefault()
    setUploading(true)

    try {
      const formDataToSend = new FormData()
      formDataToSend.append('name', formData.name)
      formDataToSend.append('emoji', formData.emoji)
      
      if (files) {
        for (const file of files) {
          formDataToSend.append('files', file)
        }
      }

      const response = await api.post('/modules/', formDataToSend, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      setShowModal(false)
      setFormData({ name: '', emoji: '📚' })
      setFiles(null)
      
      // Show processing modal if files were uploaded
      if (files && files.length > 0) {
        setProcessingModuleId(response.data.id)
      } else {
        fetchModules()
      }
    } catch (error) {
      console.error('Error creating module:', error)
      alert('Error creating module: ' + (error.response?.data?.error || error.message))
    } finally {
      setUploading(false)
    }
  }

  const handleProcessingComplete = () => {
    setProcessingModuleId(null)
    fetchModules()
  }

  const handleEditModule = async (e) => {
    e.preventDefault()
    setUploading(true)

    try {
      await api.put(`/modules/${editingModule}`, {
        name: formData.name,
        emoji: formData.emoji
      })

      setShowModal(false)
      setEditingModule(null)
      setFormData({ name: '', emoji: '📚' })
      fetchModules()
    } catch (error) {
      console.error('Error updating module:', error)
      alert('Error updating module')
    } finally {
      setUploading(false)
    }
  }

  const handleDeleteModule = async (moduleId) => {
    if (!confirm('Are you sure you want to delete this module?')) return

    try {
      await api.delete(`/modules/${moduleId}`)
      fetchModules()
    } catch (error) {
      console.error('Error deleting module:', error)
      alert('Error deleting module')
    }
  }

  const openCreateModal = () => {
    setEditingModule(null)
    setFormData({ name: '', emoji: '📚' })
    setShowModal(true)
  }

  const openEditModal = (module) => {
    setEditingModule(module.id)
    setFormData({ name: module.name, emoji: module.emoji })
    setShowModal(true)
  }

  const handleModuleClick = (moduleId) => {
    navigate(`/modules/${moduleId}`)
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
          <Link to="/dashboard" className="btn btn-ghost">Dashboard</Link>
          <button onClick={onLogout} className="btn btn-ghost">Logout</button>
        </div>
      </div>

      <div className="container mx-auto p-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold">My Modules</h1>
          <button onClick={openCreateModal} className="btn btn-primary">
            + Create Module
          </button>
        </div>

        {modules.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-xl text-gray-500 mb-4">No modules yet</p>
            <button onClick={openCreateModal} className="btn btn-primary">
              Create Your First Module
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {modules.map((module) => (
              <div key={module.id} className="card bg-base-100 shadow-xl hover:shadow-2xl transition-shadow">
                <div className="card-body">
                  <div className="text-5xl mb-2">{module.emoji}</div>
                  <h2 className="card-title">{module.name}</h2>
                  <div className="text-sm text-gray-500">
                    <p>{module.file_count} files</p>
                  </div>
                  <div className="card-actions justify-end mt-4">
                    <button 
                      onClick={() => handleModuleClick(module.id)}
                      className="btn btn-primary btn-sm"
                      disabled={module.processing_status !== 'completed'}
                    >
                      View
                    </button>
                    <button onClick={() => openEditModal(module)} className="btn btn-secondary btn-sm">
                      Edit
                    </button>
                    <button onClick={() => handleDeleteModule(module.id)} className="btn btn-error btn-sm">
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="modal modal-open">
          <div className="modal-box">
            <h3 className="font-bold text-lg mb-4">
              {editingModule ? 'Edit Module' : 'Create New Module'}
            </h3>
            
            <form onSubmit={editingModule ? handleEditModule : handleCreateModule}>
              <div className="form-control">
                <label className="label">
                  <span className="label-text">Module Name</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g., Introduction to Physics"
                  className="input input-bordered"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>

              <div className="form-control mt-4">
                <EmojiPicker
                  value={formData.emoji}
                  onChange={(emoji) => setFormData({ ...formData, emoji })}
                />
              </div>

              {!editingModule && (
                <div className="form-control mt-4">
                  <label className="label">
                    <span className="label-text">Upload Files (ZIP or individual files)</span>
                  </label>
                  <input
                    type="file"
                    className="file-input file-input-bordered"
                    multiple
                    onChange={(e) => setFiles(e.target.files)}
                  />
                  <label className="label">
                    <span className="label-text-alt">Supported: PDF, DOCX, PPTX, MP4, MP3, TXT, ZIP</span>
                  </label>
                </div>
              )}

              <div className="modal-action">
                <button
                  type="button"
                  className="btn"
                  onClick={() => {
                    setShowModal(false)
                    setEditingModule(null)
                  }}
                  disabled={uploading}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={uploading}>
                  {uploading ? <span className="loading loading-spinner"></span> : (editingModule ? 'Update' : 'Create')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Processing Modal */}
      {processingModuleId && (
        <ProcessingModal
          moduleId={processingModuleId}
          onComplete={handleProcessingComplete}
        />
      )}
    </div>
  )
}

export default Modules
