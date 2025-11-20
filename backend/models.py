from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    modules = db.relationship('Module', backref='user', lazy=True, cascade='all, delete-orphan')
    telemetry = db.relationship('Telemetry', backref='user', lazy=True, cascade='all, delete-orphan')
    insights = db.relationship('Insight', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    emoji = db.Column(db.String(10), default='📚')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processing_status = db.Column(db.String(50), default='pending')  # pending, processing, completed, error
    processing_step = db.Column(db.String(200))  # Current processing step description
    processing_progress = db.Column(db.Integer, default=0)  # 0-100 percentage
    
    files = db.relationship('File', backref='module', lazy=True, cascade='all, delete-orphan')
    lessons = db.relationship('Lesson', backref='module', lazy=True, cascade='all, delete-orphan')

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(500), nullable=False)
    file_path = db.Column(db.String(1000), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    vector_id = db.Column(db.String(200))  # ChromaDB collection ID

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    lesson_number = db.Column(db.Integer, nullable=False)
    plan = db.Column(db.Text)  # High-level plan
    file_ids = db.Column(db.Text)  # JSON string of file IDs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    objectives = db.relationship('LearningObjective', backref='lesson', lazy=True, cascade='all, delete-orphan')
    progress = db.relationship('LessonProgress', backref='lesson', lazy=True, cascade='all, delete-orphan')
    components = db.relationship('LessonComponent', backref='lesson', lazy=True, cascade='all, delete-orphan')

class LearningObjective(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    objective_text = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)

class LessonProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    progress_percentage = db.Column(db.Float, default=0.0)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    current_component_index = db.Column(db.Integer, default=0)

class LessonComponent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    component_type = db.Column(db.String(100), nullable=False)  # info_card, flashcard, quiz, mindmap, custom
    component_data = db.Column(db.Text, nullable=False)  # JSON data for the component
    order = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Telemetry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    component_id = db.Column(db.Integer, db.ForeignKey('lesson_component.id'))
    event_type = db.Column(db.String(100), nullable=False)  # time_spent, quiz_answer, card_flip, etc.
    event_data = db.Column(db.Text)  # JSON data
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Insight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    insight_text = db.Column(db.Text, nullable=False)
    insight_type = db.Column(db.String(100))  # learning_style, performance, preference
    confidence_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
