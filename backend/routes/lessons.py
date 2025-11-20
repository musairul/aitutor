from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Lesson, LessonProgress, LessonComponent, LearningObjective, Module, Insight, db
from services.llm_service import LLMService
from services.telemetry_service import TelemetryService
import json

lessons_bp = Blueprint('lessons', __name__)

@lessons_bp.route('/<int:lesson_id>', methods=['GET'])
@jwt_required()
def get_lesson(lesson_id):
    user_id = int(get_jwt_identity())
    lesson = Lesson.query.get(lesson_id)
    
    print(f"=== GET LESSON {lesson_id} ===")
    print(f"User ID: {user_id}")
    print(f"Lesson found: {lesson is not None}")
    
    if not lesson:
        print(f"❌ Lesson {lesson_id} not found")
        return jsonify({'error': 'Lesson not found'}), 404
    
    # Check if user owns this lesson's module
    module = Module.query.get(lesson.module_id)
    print(f"Module found: {module is not None}, module_id: {lesson.module_id}")
    
    if not module:
        print(f"❌ Module {lesson.module_id} not found for lesson {lesson_id}")
        return jsonify({'error': 'Module not found'}), 404
    
    if module.user_id != user_id:
        print(f"❌ Unauthorized: module.user_id={module.user_id}, user_id={user_id}")
        return jsonify({'error': 'Unauthorized'}), 403
    
    print(f"✓ Authorization passed")
    
    # Get or create progress
    progress = LessonProgress.query.filter_by(
        lesson_id=lesson_id,
        user_id=user_id
    ).first()
    
    if not progress:
        progress = LessonProgress(
            lesson_id=lesson_id,
            user_id=user_id,
            progress_percentage=0.0,
            current_component_index=0
        )
        db.session.add(progress)
        db.session.commit()
    
    # Get objectives
    objectives = LearningObjective.query.filter_by(lesson_id=lesson_id).order_by(LearningObjective.order).all()
    objectives_data = [{'id': obj.id, 'text': obj.objective_text, 'completed': obj.completed} for obj in objectives]
    
    # Get components
    components = LessonComponent.query.filter_by(lesson_id=lesson_id).order_by(LessonComponent.order).all()
    components_data = []
    for comp in components:
        components_data.append({
            'id': comp.id,
            'type': comp.component_type,
            'data': json.loads(comp.component_data),
            'order': comp.order
        })
    
    # Get module_id and next lesson info
    module_id = lesson.module_id
    
    # Find next lesson in the same module
    next_lesson_info = None
    next_lesson = Lesson.query.filter_by(module_id=lesson.module_id).filter(
        Lesson.lesson_number > lesson.lesson_number
    ).order_by(Lesson.lesson_number).first()
    
    if next_lesson:
        next_lesson_info = {
            'id': next_lesson.id,
            'title': next_lesson.title
        }
    
    return jsonify({
        'id': lesson.id,
        'title': lesson.title,
        'plan': lesson.plan,
        'objectives': objectives_data,
        'progress': {
            'percentage': progress.progress_percentage,
            'current_component_index': progress.current_component_index,
            'completed': progress.completed
        },
        'components': components_data,
        'module_id': module_id,
        'next_lesson': next_lesson_info
    }), 200

@lessons_bp.route('/<int:lesson_id>/start', methods=['POST'])
@jwt_required()
def start_lesson(lesson_id):
    user_id = int(get_jwt_identity())
    lesson = Lesson.query.get(lesson_id)
    
    if not lesson:
        return jsonify({'error': 'Lesson not found'}), 404
    
    # Check if components already generated
    existing_components = LessonComponent.query.filter_by(lesson_id=lesson_id).count()
    
    if existing_components == 0:
        # Generate initial components
        llm_service = LLMService()
        telemetry_service = TelemetryService()
        
        # Get user insights
        insights = telemetry_service.get_user_insights(user_id)
        
        # Generate components based on lesson plan, objectives, and insights
        components_data = llm_service.generate_lesson_components(
            lesson_id=lesson_id,
            insights=insights
        )
        
        for comp_data in components_data:
            # Validate component before saving
            is_valid, error_msg = llm_service._validate_component(comp_data)
            if not is_valid:
                print(f"⚠️ Skipping invalid component: {error_msg}")
                print(f"   Component type: {comp_data.get('type', 'unknown')}")
                continue
            
            component = LessonComponent(
                lesson_id=lesson_id,
                component_type=comp_data['type'],
                component_data=json.dumps(comp_data['data']),
                order=comp_data['order']
            )
            db.session.add(component)
        
        db.session.commit()
    
    return jsonify({'message': 'Lesson started'}), 200

@lessons_bp.route('/<int:lesson_id>/next-component', methods=['POST'])
@jwt_required()
def get_next_component(lesson_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    current_index = data.get('current_index', 0)
    
    # Get current total components count BEFORE updating
    total_components_before = LessonComponent.query.filter_by(lesson_id=lesson_id).count()
    
    # Update progress
    progress = LessonProgress.query.filter_by(
        lesson_id=lesson_id,
        user_id=user_id
    ).first()
    
    if progress:
        progress.current_component_index = current_index + 1
        db.session.commit()
    
    # Get telemetry and insights
    llm_service = LLMService()
    telemetry_service = TelemetryService()
    recent_telemetry = telemetry_service.get_recent_telemetry(user_id, lesson_id)
    insights = telemetry_service.analyze_telemetry(user_id, lesson_id, recent_telemetry)
    
    adaptive_component_generated = False
    adaptive_reason = None
    evaluation_result = None
    objectives_met = False
    can_complete = False
    
    # Check if we've finished the structured lesson components
    if current_index + 1 >= total_components_before:
        print("📊 End of structured components reached. Evaluating learning objectives...")
        
        # Evaluate if learning objectives are met
        objectives_met, evaluation_data, should_continue = llm_service.evaluate_learning_objectives(
            lesson_id=lesson_id,
            user_id=user_id
        )
        
        evaluation_result = evaluation_data
        
        print("✓ Evaluation complete:")
        print(f"  - Objectives met: {objectives_met}")
        print(f"  - Should continue: {should_continue}")
        print(f"  - Confidence: {evaluation_data.get('confidence', 0)}%")
        
        if should_continue:
            # Generate adaptive component based on evaluation
            recommendation = evaluation_data.get('recommendation', {})
            weak_areas = evaluation_data.get('evaluation', {}).get('weak_areas', [])
            
            # Create adaptive reason based on evaluation
            if weak_areas:
                adaptive_reason = f"Let's reinforce your understanding of: {', '.join(weak_areas)}"
            else:
                adaptive_reason = recommendation.get('reason', 'Let me help you master this material')
            
            print(f"🎯 Generating adaptive component batch for: {adaptive_reason}")
            
            # Generate a BATCH of components (teaching + testing)
            new_components_data = llm_service.generate_adaptive_batch(
                lesson_id=lesson_id,
                insights=insights,
                recent_telemetry=recent_telemetry,
                evaluation_data=evaluation_data
            )
            
            if new_components_data and isinstance(new_components_data, list):
                # Validate and add each component in the batch
                components_added = 0
                for comp_data in new_components_data:
                    is_valid, error_msg = llm_service._validate_component(comp_data)
                    if not is_valid:
                        print(f"⚠️ Invalid component in batch: {error_msg}")
                        continue
                    
                    # Get current count for order
                    current_order = LessonComponent.query.filter_by(lesson_id=lesson_id).count()
                    
                    component = LessonComponent(
                        lesson_id=lesson_id,
                        component_type=comp_data['type'],
                        component_data=json.dumps(comp_data['data']),
                        order=current_order
                    )
                    db.session.add(component)
                    components_added += 1
                
                if components_added > 0:
                    db.session.commit()
                    adaptive_component_generated = True
                    print(f"✓ Added {components_added} adaptive components in batch")
                else:
                    can_complete = True
                    print("⚠️ No valid components in batch - allowing completion")
            else:
                # No components generated means objectives are met
                can_complete = True
                adaptive_reason = "Great work! You've mastered all the learning objectives."
                print("✓ No adaptive components needed - objectives met")
        else:
            # Evaluation says objectives are met and we can finish
            can_complete = True
            adaptive_reason = "Excellent! You've successfully mastered all learning objectives for this lesson."
            print("✓ Objectives met - lesson can be completed")
    
    # Recalculate progress with final component count
    if progress:
        total_components_after = LessonComponent.query.filter_by(lesson_id=lesson_id).count()
        
        if total_components_after > 0:
            progress.progress_percentage = (current_index + 1) / total_components_after * 100
            
            # Only mark as completed if we can complete (objectives met)
            if can_complete:
                progress.completed = True
                progress.progress_percentage = 100
        
        db.session.commit()
    
    return jsonify({
        'message': 'Progress updated',
        'adaptive_component_generated': adaptive_component_generated,
        'adaptive_reason': adaptive_reason,
        'can_complete': can_complete,
        'evaluation': evaluation_result if evaluation_result else None
    }), 200

@lessons_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    print("=== DASHBOARD ENDPOINT CALLED ===")
    user_id = int(get_jwt_identity())
    print(f"User ID from token: {user_id}")
    
    # Get latest lesson with progress
    latest_progress = LessonProgress.query.filter_by(
        user_id=user_id,
        completed=False
    ).order_by(LessonProgress.last_accessed.desc()).first()
    
    latest_lesson = None
    if latest_progress:
        lesson = Lesson.query.get(latest_progress.lesson_id)
        module = Module.query.get(lesson.module_id)
        
        latest_lesson = {
            'lesson_id': lesson.id,
            'lesson_title': lesson.title,
            'module_name': module.name,
            'module_emoji': module.emoji,
            'lesson_number': lesson.lesson_number,
            'progress_percentage': latest_progress.progress_percentage
        }
    
    # Get total modules count
    modules_count = Module.query.filter_by(user_id=user_id).count()
    
    # Get insights
    from models import Insight
    insights = Insight.query.filter_by(user_id=user_id, is_active=True).order_by(
        Insight.created_at.desc()
    ).limit(5).all()
    
    insights_data = [{
        'text': insight.insight_text,
        'type': insight.insight_type,
        'confidence': insight.confidence_score
    } for insight in insights]
    
    return jsonify({
        'latest_lesson': latest_lesson,
        'modules_count': modules_count,
        'insights': insights_data
    }), 200

@lessons_bp.route('/components/<int:component_id>/grade', methods=['POST'])
@jwt_required()
def grade_component(component_id):
    """Grade a practice exercise component"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Get the component
    component = LessonComponent.query.get(component_id)
    if not component:
        return jsonify({'error': 'Component not found'}), 404
    
    # Verify user has access to this component
    lesson = Lesson.query.get(component.lesson_id)
    module = Module.query.get(lesson.module_id)
    if module.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Only grade practice_exercise components
    if component.component_type != 'practice_exercise':
        return jsonify({'error': 'This component type cannot be graded'}), 400
    
    user_answers = data.get('answers', {})
    if not user_answers:
        return jsonify({'error': 'No answers provided'}), 400
    
    # Get component data
    component_data = json.loads(component.component_data)
    
    # Get lesson context for better grading
    lesson_context = f"This exercise is part of the lesson '{lesson.title}' with plan: {lesson.plan}"
    
    # Grade using LLM
    llm_service = LLMService()
    grading_result = llm_service.grade_practice_exercise(
        component_data=component_data,
        user_answers=user_answers,
        lesson_context=lesson_context
    )
    
    # Track grading in telemetry
    telemetry_service = TelemetryService()
    telemetry_service.track_event(
        user_id=user_id,
        lesson_id=component.lesson_id,
        event_type='practice_exercise_graded',
        event_data={
            'component_id': component_id,
            'overall_score': grading_result.get('overall_score'),
            'overall_grade': grading_result.get('overall_grade'),
            'question_count': len(grading_result.get('question_results', [])),
            'scores': [q['score'] for q in grading_result.get('question_results', [])]
        }
    )
    
    return jsonify(grading_result), 200

