# AI Tutor - Intelligent Adaptive Learning Platform

An AI-powered tutoring system that creates personalized learning experiences using RAG (Retrieval Augmented Generation), telemetry tracking, and adaptive content delivery.

## Features

- 🎓 **Personalized Learning**: AI-generated lessons tailored to your learning style
- 📚 **Module Management**: Upload course materials (PDF, PPTX, DOCX, MP4, MP3, ZIP)
- 🤖 **Smart Content Generation**: 12-week curriculum automatically structured from your files
- 📊 **Learning Analytics**: Real-time telemetry tracks your progress and learning patterns
- 🧠 **Adaptive Components**: Interactive flashcards, quizzes, mind maps, and custom visualizations
- 💡 **Intelligent Insights**: AI analyzes your performance to optimize learning

## Tech Stack

### Backend
- Python 3.12
- Flask (REST API)
- SQLAlchemy (SQLite database)
- Google Gemini API (LLM)
- ChromaDB (Vector database for RAG)
- JWT Authentication

### Frontend
- React 18
- Vite
- Tailwind CSS
- DaisyUI components
- React Router
- Axios

## Project Structure

```
test/
├── backend/
│   ├── app.py                 # Flask application
│   ├── models.py              # Database models
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment variables
│   ├── routes/
│   │   ├── auth.py           # Authentication routes
│   │   ├── modules.py        # Module management
│   │   ├── lessons.py        # Lesson endpoints
│   │   └── telemetry.py      # Telemetry tracking
│   └── services/
│       ├── llm_service.py    # Gemini API integration
│       ├── vector_service.py # ChromaDB RAG
│       └── telemetry_service.py # Analytics
├── frontend/
│   ├── src/
│   │   ├── pages/           # React pages
│   │   ├── components/      # UI components
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.12+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```powershell
cd backend
```

2. Create a virtual environment:
```powershell
python -m venv venv
```

3. Activate the virtual environment:
```powershell
.\venv\Scripts\Activate.ps1
```

4. Install dependencies:
```powershell
pip install -r requirements.txt
```

5. The `.env` file is already created with the Gemini API key. If you need to change it, edit `backend/.env`.

6. Run the Flask server:
```powershell
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
```powershell
cd frontend
```

2. Install dependencies:
```powershell
npm install
```

3. Run the development server:
```powershell
npm run dev
```

The frontend will run on `http://localhost:3000`

## Usage

### 1. Create an Account
- Visit `http://localhost:3000`
- Click "Sign Up" and create an account
- Login with your credentials

### 2. Create a Module
- Go to "Modules" page
- Click "Create Module"
- Enter a name and emoji
- Upload your course files (PDF, PPTX, DOCX, MP4, MP3, or ZIP containing these files)
- The AI will process your files and generate a 12-week curriculum

### 3. Start Learning
- Click on your module to view generated lessons
- Click on a lesson to start learning
- Complete interactive components (flashcards, quizzes, mind maps)
- The AI adapts content based on your performance

### 4. Track Progress
- View your dashboard for insights
- See learning analytics and personalized recommendations
- Continue lessons from where you left off

## How It Works

### Module Processing Pipeline

1. **File Upload**: User uploads course materials
2. **Vector Database**: Files are chunked and stored in ChromaDB
3. **Week Generation**: LLM analyzes content and creates 12-week structure
4. **Objective Creation**: SMART learning objectives generated for each week
5. **Lesson Planning**: Objectives split into 10-20 minute lessons

### Adaptive Learning

1. **Telemetry Collection**: Tracks time spent, quiz answers, component interactions
2. **Insight Generation**: Analyzes patterns (visual vs text preference, quiz performance)
3. **Dynamic Components**: Next component chosen based on real-time telemetry
4. **Continuous Optimization**: Learning style refined throughout the course

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Modules
- `GET /api/modules/` - List all modules
- `GET /api/modules/<id>` - Get module details
- `POST /api/modules/` - Create module (with file upload)
- `PUT /api/modules/<id>` - Update module
- `DELETE /api/modules/<id>` - Delete module

### Lessons
- `GET /api/lessons/<id>` - Get lesson details
- `POST /api/lessons/<id>/start` - Generate initial components
- `POST /api/lessons/<id>/next-component` - Update progress
- `GET /api/lessons/dashboard` - Get dashboard data

### Telemetry
- `POST /api/telemetry/track` - Track learning event

## Database Schema

- **User**: Authentication and user data
- **Module**: Course modules with files
- **File**: Uploaded course materials
- **Week**: 12-week curriculum structure
- **Lesson**: Individual lesson plans
- **LearningObjective**: SMART objectives per lesson
- **LessonProgress**: User progress tracking
- **LessonComponent**: Dynamic learning components
- **Telemetry**: Interaction tracking
- **Insight**: AI-generated learning insights

## AI Features

### LLM Integration (Gemini)
- Structured JSON output for weeks, objectives, and lessons
- Automatic fallback on rate limits/errors
- Context-aware component generation
- Real-time adaptation based on telemetry

### RAG (Retrieval Augmented Generation)
- ChromaDB vector database
- File content extraction (PDF, DOCX, PPTX)
- Semantic search for relevant content
- Context injection for LLM prompts

### Telemetry & Analytics
- Time spent per component
- Quiz performance tracking
- Component preference analysis
- Learning style detection
- Confidence scoring for insights

## Component Types

- **Info Card**: Text-based information display
- **Flashcard**: Interactive flip cards for memorization
- **Quiz**: Multiple choice with explanations
- **Mind Map**: Visual concept relationships
- **Interactive Diagram**: Custom visualizations
- **Video Summary**: Key points extraction
- **Practice Exercise**: Hands-on problem solving

## Future Enhancements

- [ ] Local LLM fallback (Ollama integration)
- [ ] Background processing with Celery
- [ ] Video/audio transcription
- [ ] Collaborative learning features
- [ ] Export progress reports
- [ ] Mobile app
- [ ] More component types
- [ ] Spaced repetition algorithms
- [ ] Social learning features

## Troubleshooting

### Backend Issues
- **Import errors**: Make sure virtual environment is activated
- **Database errors**: Delete `ai_tutor.db` and restart to recreate
- **Gemini API errors**: Check API key in `.env` file

### Frontend Issues
- **Module not found**: Run `npm install` in frontend directory
- **Proxy errors**: Ensure backend is running on port 5000
- **Build errors**: Delete `node_modules` and run `npm install` again

## License

This project is for educational purposes.

## Credits

Built with:
- Google Gemini API
- Flask & React ecosystems
- Tailwind CSS & DaisyUI
- ChromaDB for vector search
