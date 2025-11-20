from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Module, File, Lesson, db
from werkzeug.utils import secure_filename
import os
import zipfile
import json
import threading
from services.llm_service import LLMService
from services.vector_service import VectorService

modules_bp = Blueprint('modules', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'ppt', 'pptx', 'doc', 'docx', 'mp4', 'mp3', 'txt', 'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@modules_bp.route('/', methods=['GET'])
@jwt_required()
def get_modules():
    user_id = int(get_jwt_identity())
    modules = Module.query.filter_by(user_id=user_id).all()
    
    result = []
    for module in modules:
        result.append({
            'id': module.id,
            'name': module.name,
            'emoji': module.emoji,
            'created_at': module.created_at.isoformat(),
            'processing_status': module.processing_status,
            'file_count': len(module.files),
            'lesson_count': len(module.lessons)
        })
    
    return jsonify(result), 200

@modules_bp.route('/<int:module_id>', methods=['GET'])
@jwt_required()
def get_module(module_id):
    user_id = int(get_jwt_identity())
    module = Module.query.filter_by(id=module_id, user_id=user_id).first()
    
    if not module:
        return jsonify({'error': 'Module not found'}), 404
    
    lessons_data = []
    for lesson in module.lessons:
        objectives = [obj.objective_text for obj in lesson.objectives]
        
        # Get lesson progress for this user
        from models import LessonProgress
        progress = LessonProgress.query.filter_by(
            lesson_id=lesson.id,
            user_id=user_id
        ).first()
        
        lessons_data.append({
            'id': lesson.id,
            'title': lesson.title,
            'lesson_number': lesson.lesson_number,
            'objectives': objectives,
            'completed': progress.completed if progress else False,
            'progress_percentage': progress.progress_percentage if progress else 0.0,
            'last_accessed': progress.last_accessed.isoformat() if progress and progress.last_accessed else None
        })
    
    return jsonify({
        'id': module.id,
        'name': module.name,
        'emoji': module.emoji,
        'processing_status': module.processing_status,
        'processing_step': module.processing_step,
        'processing_progress': module.processing_progress,
        'lessons': lessons_data
    }), 200

@modules_bp.route('/<int:module_id>/status', methods=['GET'])
@jwt_required()
def get_module_status(module_id):
    user_id = int(get_jwt_identity())
    module = Module.query.filter_by(id=module_id, user_id=user_id).first()
    
    if not module:
        return jsonify({'error': 'Module not found'}), 404
    
    return jsonify({
        'processing_status': module.processing_status,
        'processing_step': module.processing_step or 'Waiting to start...',
        'processing_progress': module.processing_progress or 0
    }), 200

@modules_bp.route('/', methods=['POST'])
@jwt_required()
def create_module():
    print("=== CREATE MODULE CALLED ===")
    user_id = int(get_jwt_identity())
    print(f"User ID: {user_id}")
    
    name = request.form.get('name')
    emoji = request.form.get('emoji', '📚')
    
    if not name:
        return jsonify({'error': 'Module name required'}), 400
    
    module = Module(name=name, emoji=emoji, user_id=user_id)
    db.session.add(module)
    db.session.commit()
    
    # Handle file uploads
    if 'files' in request.files:
        files = request.files.getlist('files')
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(module.id))
        os.makedirs(upload_folder, exist_ok=True)
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                
                # Extract zip files
                if filename.endswith('.zip'):
                    extract_folder = os.path.join(upload_folder, 'extracted')
                    os.makedirs(extract_folder, exist_ok=True)
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_folder)
                    
                    # Process extracted files
                    for root, dirs, files_in_zip in os.walk(extract_folder):
                        for file_in_zip in files_in_zip:
                            if allowed_file(file_in_zip) and not file_in_zip.endswith('.zip'):
                                extracted_path = os.path.join(root, file_in_zip)
                                file_type = file_in_zip.rsplit('.', 1)[1].lower()
                                file_obj = File(
                                    filename=file_in_zip,
                                    file_path=extracted_path,
                                    file_type=file_type,
                                    module_id=module.id
                                )
                                db.session.add(file_obj)
                else:
                    file_type = filename.rsplit('.', 1)[1].lower()
                    file_obj = File(
                        filename=filename,
                        file_path=file_path,
                        file_type=file_type,
                        module_id=module.id
                    )
                    db.session.add(file_obj)
        
        db.session.commit()
        
        # Start processing in background thread
        if files:
            module.processing_status = 'processing'
            module.processing_step = 'Queued for processing...'
            module.processing_progress = 0
            db.session.commit()
            
            # Run processing in background thread
            thread = threading.Thread(target=process_module_background, args=(current_app._get_current_object(), module.id))
            thread.daemon = True
            thread.start()
            print(f"Started background processing for module {module.id}")
    
    return jsonify({
        'id': module.id,
        'name': module.name,
        'emoji': module.emoji,
        'processing_status': module.processing_status
    }), 201

@modules_bp.route('/<int:module_id>', methods=['PUT'])
@jwt_required()
def update_module(module_id):
    user_id = int(get_jwt_identity())
    module = Module.query.filter_by(id=module_id, user_id=user_id).first()
    
    if not module:
        return jsonify({'error': 'Module not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        module.name = data['name']
    if 'emoji' in data:
        module.emoji = data['emoji']
    
    db.session.commit()
    
    return jsonify({
        'id': module.id,
        'name': module.name,
        'emoji': module.emoji
    }), 200

@modules_bp.route('/<int:module_id>', methods=['DELETE'])
@jwt_required()
def delete_module(module_id):
    user_id = int(get_jwt_identity())
    module = Module.query.filter_by(id=module_id, user_id=user_id).first()
    
    if not module:
        return jsonify({'error': 'Module not found'}), 404
    
    try:
        # Import all models needed for cascade delete
        from models import (
            Lesson, LearningObjective, LessonComponent, 
            LessonProgress, Telemetry, Insight, File
        )
        
        # Delete in correct order to respect foreign key constraints
        
        # 1. Get all lessons for this module
        lessons = Lesson.query.filter_by(module_id=module_id).all()
        lesson_ids = [lesson.id for lesson in lessons]
        
        # 2. Delete telemetry for these lessons
        Telemetry.query.filter(Telemetry.lesson_id.in_(lesson_ids)).delete(synchronize_session=False)
        print(f"Deleted telemetry for {len(lesson_ids)} lessons")
        
        # 3. Delete lesson progress for these lessons
        LessonProgress.query.filter(LessonProgress.lesson_id.in_(lesson_ids)).delete(synchronize_session=False)
        print(f"Deleted progress for {len(lesson_ids)} lessons")
        
        # 4. Delete lesson components for these lessons
        LessonComponent.query.filter(LessonComponent.lesson_id.in_(lesson_ids)).delete(synchronize_session=False)
        print(f"Deleted components for {len(lesson_ids)} lessons")
        
        # 5. Delete learning objectives for these lessons
        LearningObjective.query.filter(LearningObjective.lesson_id.in_(lesson_ids)).delete(synchronize_session=False)
        print(f"Deleted objectives for {len(lesson_ids)} lessons")
        
        # 6. Delete lessons
        Lesson.query.filter_by(module_id=module_id).delete(synchronize_session=False)
        print(f"Deleted {len(lesson_ids)} lessons")
        
        # 7. Delete insights related to this module (optional - based on your data model)
        # If insights are module-specific, delete them. Otherwise skip this step.
        
        # 8. Delete files associated with this module
        files = File.query.filter_by(module_id=module_id).all()
        for file in files:
            # Delete file from vector database if it has a vector_id
            if file.vector_id:
                try:
                    from services.vector_service import VectorService
                    vector_service = VectorService()
                    # Delete from vector DB (implement this method if not exists)
                    print(f"Deleting vector data for file {file.filename}")
                except Exception as e:
                    print(f"Warning: Could not delete vector data: {e}")
        
        File.query.filter_by(module_id=module_id).delete(synchronize_session=False)
        print(f"Deleted {len(files)} files")
        
        # 11. Delete files from filesystem
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(module_id))
        if os.path.exists(upload_folder):
            import shutil
            shutil.rmtree(upload_folder)
            print(f"Deleted upload folder: {upload_folder}")
        
        # 12. Finally delete the module itself
        db.session.delete(module)
        
        # Commit all deletes
        db.session.commit()
        print(f"✓ Successfully deleted module {module_id} and all related data")
        
        return jsonify({'message': 'Module and all related data deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error deleting module: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to delete module: {str(e)}'}), 500

def process_module_background(app, module_id):
    """Background thread function to process module with app context"""
    with app.app_context():
        try:
            process_module(module_id)
        except Exception as e:
            print(f"Background processing error: {e}")
            import traceback
            traceback.print_exc()

def process_module(module_id):
    """Process module files and generate weeks, lessons, and objectives"""
    module = Module.query.get(module_id)
    module.processing_status = 'processing'
    module.processing_step = 'Initializing...'
    module.processing_progress = 0
    db.session.commit()
    
    try:
        llm_service = LLMService()
        vector_service = VectorService()
        
        # Calculate total steps for smooth progress
        files = File.query.filter_by(module_id=module_id).all()
        total_files = len(files)
        print(f"Found {total_files} files to process")
        
        if total_files == 0:
            module.processing_step = 'No files to process'
            module.processing_progress = 100
            module.processing_status = 'completed'
            db.session.commit()
            return
        
        # Progress allocation:
        # 0-30%: File processing and embedding
        # 30-50%: Curriculum generation
        # 50-100%: Objectives for each lesson (distributed across lessons)
        
        # Step 1: Store files in vector database (0-30%)
        module.processing_step = 'Processing and embedding files...'
        db.session.commit()
        
        for idx, file in enumerate(files):
            print(f"Processing file {idx + 1}/{total_files}: {file.filename}")
            vector_id = vector_service.add_file(file.file_path, file.id)
            file.vector_id = vector_id
            progress = int((idx + 1) / total_files * 30)
            module.processing_progress = progress
            module.processing_step = f'Processing files ({idx + 1}/{total_files})...'
            db.session.commit()
        
        print("File embedding complete, generating curriculum...")
        
        # Step 2: Generate lessons structure (30-50%)
        module.processing_step = 'Analyzing content and generating curriculum...'
        module.processing_progress = 30
        db.session.commit()
        
        lessons_data = llm_service.generate_curriculum(module_id, files)
        print(f"Generated {len(lessons_data)} lessons")
        
        if not lessons_data or len(lessons_data) == 0:
            print("WARNING: No lessons data generated, completing with empty state")
            module.processing_step = 'Completed (no lessons generated)'
            module.processing_progress = 100
            module.processing_status = 'completed'
            db.session.commit()
            return
        
        module.processing_progress = 50
        db.session.commit()
        
        # Step 3: Process each lesson with objectives (50-100%)
        total_lessons = len(lessons_data)
        progress_per_lesson = 50 / total_lessons  # 50% total divided by number of lessons
        
        for lesson_idx, lesson_info in enumerate(lessons_data):
            print(f"Processing lesson {lesson_idx + 1}/{total_lessons}: {lesson_info.get('title', 'Untitled')}")
            
            # Create lesson
            base_progress = 50 + (lesson_idx * progress_per_lesson)
            module.processing_step = f'Creating lesson {lesson_idx + 1} of {total_lessons}...'
            module.processing_progress = int(base_progress)
            db.session.commit()
            
            lesson = Lesson(
                title=lesson_info['title'],
                module_id=module_id,
                lesson_number=lesson_info['lesson_number'],
                plan=lesson_info.get('plan', ''),
                file_ids=json.dumps(lesson_info.get('file_ids', []))
            )
            db.session.add(lesson)
            db.session.commit()
            
            # Generate objectives for this lesson
            module.processing_step = f'Generating objectives for lesson {lesson_idx + 1}...'
            module.processing_progress = int(base_progress + progress_per_lesson * 0.5)
            db.session.commit()
            
            print(f"Calling generate_objectives for lesson {lesson.id} with file_ids: {lesson_info.get('file_ids', [])}")
            try:
                objectives = llm_service.generate_objectives(lesson.id, lesson_info.get('file_ids', []))
                print(f"Generated {len(objectives)} objectives for lesson {lesson_idx + 1}")
            except Exception as e:
                print(f"⚠️ Error generating objectives for lesson {lesson_idx + 1}: {e}")
                # Use fallback objectives
                objectives = [
                    f"Understand the key concepts in {lesson_info['title']}",
                    f"Apply knowledge from {lesson_info['title']}",
                    f"Practice skills related to {lesson_info['title']}"
                ]
                print(f"Using fallback objectives: {objectives}")
            
            # Add objectives to lesson
            from models import LearningObjective
            for idx, obj_text in enumerate(objectives):
                objective = LearningObjective(
                    lesson_id=lesson.id,
                    objective_text=obj_text,
                    order=idx
                )
                db.session.add(objective)
            
            db.session.commit()
            
            # Update progress at end of lesson
            module.processing_progress = int(base_progress + progress_per_lesson)
            db.session.commit()
        
        module.processing_step = 'Completed!'
        module.processing_progress = 100
        module.processing_status = 'completed'
        db.session.commit()
        
    except Exception as e:
        print(f"Error in process_module: {e}")
        import traceback
        traceback.print_exc()
        module.processing_status = 'error'
        module.processing_step = f'Error: {str(e)}'
        module.processing_progress = 0
        db.session.commit()
        raise
