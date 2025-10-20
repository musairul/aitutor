# AI Tutor Web Application

A full-stack web application for an AI tutoring platform with authentication, built using FastAPI, Supabase, React, and Tailwind CSS.

## 🚀 Features

- **Landing Page**: Attractive landing page showcasing the AI tutor platform
- **Authentication System**: Complete login and registration functionality using Supabase
- **Protected Dashboard**: User dashboard accessible only when logged in
- **Modern UI**: Built with React and styled with Tailwind CSS
- **Type Safety**: TypeScript for better development experience
- **RESTful API**: FastAPI backend with proper authentication middleware

## 📁 Project Structure

```
AITutor/
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── config/        # Configuration files
│   │   ├── middleware/    # Authentication middleware
│   │   ├── models/        # Pydantic models
│   │   └── routes/        # API routes
│   ├── main.py           # FastAPI application entry point
│   ├── requirements.txt  # Python dependencies
│   └── .env.example     # Environment variables template
│
└── frontend/             # React frontend
    ├── src/
    │   ├── components/   # React components
    │   ├── context/      # React context (Auth)
    │   ├── pages/        # Page components
    │   ├── services/     # API services
    │   └── types/        # TypeScript types
    ├── package.json
    └── .env.example     # Environment variables template
```

## 🛠️ Prerequisites

- Python 3.8+
- Node.js 18+
- Supabase account (for authentication and database)

## 📦 Installation

### Backend Setup

1. Navigate to the backend directory:
   ```powershell
   cd backend
   ```

2. Create a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

4. Create a `.env` file from the example:
   ```powershell
   copy .env.example .env
   ```

5. Configure your `.env` file with Supabase credentials:
   ```
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   SUPABASE_JWT_SECRET=your_supabase_jwt_secret
   ```

   To get these values:
   - Go to your Supabase project dashboard
   - Navigate to Settings > API
   - Copy the URL, anon/public key, and JWT secret

6. Run the backend server:
   ```powershell
   python main.py
   ```
   
   Or use uvicorn directly:
   ```powershell
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```powershell
   cd frontend
   ```

2. Install dependencies:
   ```powershell
   npm install
   ```

3. Create a `.env` file from the example:
   ```powershell
   copy .env.example .env
   ```

4. Configure your `.env` file (optional, defaults to localhost:8000):
   ```
   VITE_API_URL=http://localhost:8000
   ```

5. Run the development server:
   ```powershell
   npm run dev
   ```

   The application will be available at `http://localhost:5173`

## 🔐 Supabase Setup

1. Create a new project at [https://supabase.com](https://supabase.com)

2. The authentication system will work automatically with Supabase Auth - no additional tables needed!

3. (Optional) Enable email confirmation:
   - Go to Authentication > Settings
   - Configure email templates and confirmation settings

## 🎯 Usage

1. **Start the Backend**:
   ```powershell
   cd backend
   .\venv\Scripts\activate
   python main.py
   ```

2. **Start the Frontend** (in a new terminal):
   ```powershell
   cd frontend
   npm run dev
   ```

3. **Access the Application**:
   - Open your browser to `http://localhost:5173`
   - Register a new account
   - Login and access the dashboard

## 📚 API Endpoints

### Authentication

- `POST /api/auth/register` - Register a new user
  ```json
  {
    "email": "user@example.com",
    "password": "password123",
    "full_name": "John Doe"
  }
  ```

- `POST /api/auth/login` - Login user
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```

- `POST /api/auth/logout` - Logout user (requires authentication)

- `GET /api/auth/me` - Get current user info (requires authentication)

### Health Check

- `GET /` - API welcome message
- `GET /health` - Health check endpoint

## 🏗️ Built With

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Supabase** - Backend as a Service for authentication and database
- **Pydantic** - Data validation using Python type annotations
- **python-jose** - JWT token handling
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client
- **Vite** - Build tool and dev server

## 🔒 Security Features

- JWT-based authentication
- Protected routes with middleware
- HTTP-only token storage (localStorage for demo, consider httpOnly cookies for production)
- CORS configuration
- Password hashing handled by Supabase
- Input validation with Pydantic

## 🚧 Future Enhancements

- Actual AI tutoring functionality
- Session management
- Progress tracking
- Real-time chat interface
- File uploads for assignments
- Admin dashboard
- Password reset functionality
- Email verification
- OAuth providers (Google, GitHub)

## 📄 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Feel free to fork this project and submit pull requests for any improvements.

## 📞 Support

For issues or questions, please open an issue in the repository.

---

**Note**: This is a demo application. For production use, consider implementing additional security measures such as:
- Rate limiting
- CSRF protection
- Helmet for security headers
- Environment-specific configurations
- Proper error logging
- Database migrations
- Testing suite
- CI/CD pipeline
