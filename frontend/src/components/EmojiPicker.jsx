import { useState } from 'react'

function EmojiPicker({ value, onChange }) {
  const [isOpen, setIsOpen] = useState(false)

  const emojis = [
    // Education
    '📚', '📖', '✏️', '📝', '🎓', '🏫', '👨‍🎓', '👩‍🎓', '🧑‍🏫',
    // Science
    '🔬', '🧪', '🧬', '⚗️', '🔭', '🌡️', '⚛️', '💉', '🩺',
    // Math
    '🔢', '➕', '➖', '✖️', '➗', '📐', '📏', '🧮', '📊',
    // Technology
    '💻', '⌨️', '🖥️', '🖱️', '💾', '💿', '📱', '🔌', '🖨️',
    // Languages
    '🗣️', '💬', '🗨️', '📢', '🌐', '🔤', '🔡', '🔠', 'Ⓜ️',
    // Arts
    '🎨', '🖼️', '🎭', '🎪', '🎬', '🎤', '🎧', '🎵', '🎸',
    // Sports
    '⚽', '🏀', '🏈', '⚾', '🎾', '🏐', '🏉', '🎱', '🏓',
    // Nature
    '🌱', '🌿', '🍀', '🌳', '🌲', '🌴', '🌵', '🌾', '🌻',
    // Space
    '🌍', '🌎', '🌏', '🌕', '🌙', '⭐', '🌟', '✨', '🚀',
    // Weather
    '☀️', '🌤️', '⛅', '🌥️', '☁️', '🌦️', '🌧️', '⛈️', '❄️',
    // Food
    '🍎', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🫐', '🍒',
    // Objects
    '💡', '🔦', '🕯️', '📖', '📚', '📓', '📔', '📒', '📕',
    // Symbols
    '❤️', '💙', '💚', '💛', '💜', '🧡', '💗', '💓', '✅',
    // Animals
    '🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨',
    // Other
    '🎯', '🎲', '🎰', '🎳', '🎮', '🕹️', '🎪', '🎢', '🎡'
  ]

  return (
    <div className="relative">
      <label className="label">
        <span className="label-text">Emoji</span>
      </label>
      <button
        type="button"
        className="btn btn-outline btn-lg text-4xl w-24 h-24"
        onClick={() => setIsOpen(!isOpen)}
      >
        {value || '📚'}
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          ></div>
          
          {/* Emoji Grid */}
          <div className="absolute z-50 mt-2 bg-base-100 rounded-lg shadow-2xl p-4 border border-base-300 max-h-80 overflow-y-auto w-full max-w-md">
            <div className="grid grid-cols-8 gap-2">
              {emojis.map((emoji, index) => (
                <button
                  key={index}
                  type="button"
                  className="btn btn-ghost btn-sm text-2xl hover:bg-primary hover:text-primary-content"
                  onClick={() => {
                    onChange(emoji)
                    setIsOpen(false)
                  }}
                >
                  {emoji}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default EmojiPicker
