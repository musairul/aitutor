from models import Telemetry, Insight, db
import json
from datetime import datetime, timedelta
from collections import defaultdict

class TelemetryService:
    
    def track_event(self, user_id, lesson_id, event_type, event_data):
        """Track a telemetry event"""
        try:
            telemetry = Telemetry(
                user_id=user_id,
                lesson_id=lesson_id,
                event_type=event_type,
                event_data=json.dumps(event_data) if event_data else None,
                timestamp=datetime.now()
            )
            db.session.add(telemetry)
            db.session.commit()
            return True
        except Exception as e:
            print(f"Error tracking telemetry event: {e}")
            db.session.rollback()
            return False
    
    def get_recent_telemetry(self, user_id, lesson_id, limit=50):
        """Get recent telemetry events for a user in a lesson"""
        telemetry = Telemetry.query.filter_by(
            user_id=user_id,
            lesson_id=lesson_id
        ).order_by(Telemetry.timestamp.desc()).limit(limit).all()
        
        return [{
            'event_type': t.event_type,
            'event_data': json.loads(t.event_data) if t.event_data else {},
            'timestamp': t.timestamp.isoformat()
        } for t in telemetry]
    
    def get_user_insights(self, user_id):
        """Get active insights for a user"""
        insights = Insight.query.filter_by(
            user_id=user_id,
            is_active=True
        ).order_by(Insight.created_at.desc()).all()
        
        return [{
            'text': i.insight_text,
            'type': i.insight_type,
            'confidence': i.confidence_score
        } for i in insights]
    
    def analyze_telemetry(self, user_id, lesson_id, recent_telemetry):
        """Analyze telemetry and generate insights"""
        if not recent_telemetry:
            return []
        
        # Get all user telemetry for pattern analysis
        all_telemetry = Telemetry.query.filter_by(user_id=user_id).all()
        
        insights = []
        
        # Analyze quiz performance
        quiz_events = [t for t in all_telemetry if t.event_type == 'quiz_answer']
        if len(quiz_events) >= 5:
            correct_count = sum(1 for t in quiz_events if json.loads(t.event_data).get('correct', False))
            accuracy = correct_count / len(quiz_events)
            
            if accuracy < 0.5:
                insight = Insight(
                    user_id=user_id,
                    insight_text="User may need more foundational review before advancing",
                    insight_type="performance",
                    confidence_score=0.7
                )
                insights.append(insight)
        
        # Analyze component preferences
        component_interactions = defaultdict(int)
        component_time = defaultdict(float)
        
        for t in all_telemetry:
            if t.event_type == 'time_spent':
                data = json.loads(t.event_data) if t.event_data else {}
                comp_type = data.get('component_type')
                time_spent = data.get('time_seconds', 0)
                if comp_type:
                    component_interactions[comp_type] += 1
                    component_time[comp_type] += time_spent
        
        # Find preferred component types
        if component_interactions:
            most_engaged = max(component_interactions, key=component_interactions.get)
            avg_time = component_time[most_engaged] / component_interactions[most_engaged]
            
            if avg_time > 60:  # More than 1 minute average
                insight = Insight(
                    user_id=user_id,
                    insight_text=f"User learns best with {most_engaged} components",
                    insight_type="learning_style",
                    confidence_score=0.8
                )
                insights.append(insight)
        
        # Analyze visual vs text preference
        visual_components = ['mindmap', 'interactive_diagram', 'flashcard']
        text_components = ['info_card', 'video_summary']
        
        visual_time = sum(component_time.get(c, 0) for c in visual_components)
        text_time = sum(component_time.get(c, 0) for c in text_components)
        
        if visual_time > text_time * 1.5:
            insight = Insight(
                user_id=user_id,
                insight_text="User prefers visual representations over text-heavy content",
                insight_type="preference",
                confidence_score=0.75
            )
            insights.append(insight)
        elif text_time > visual_time * 1.5:
            insight = Insight(
                user_id=user_id,
                insight_text="User engages more with text-based explanations",
                insight_type="preference",
                confidence_score=0.75
            )
            insights.append(insight)
        
        # Save insights to database
        for insight in insights:
            db.session.add(insight)
        
        db.session.commit()
        
        return [{
            'text': i.insight_text,
            'type': i.insight_type,
            'confidence': i.confidence_score
        } for i in insights]
