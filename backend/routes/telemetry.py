from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Telemetry, db
import json

telemetry_bp = Blueprint('telemetry', __name__)

@telemetry_bp.route('/track', methods=['POST'])
@jwt_required()
def track_event():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    lesson_id = data.get('lesson_id')
    component_id = data.get('component_id')
    event_type = data.get('event_type')
    event_data = data.get('event_data', {})
    
    if not lesson_id or not event_type:
        return jsonify({'error': 'lesson_id and event_type required'}), 400
    
    telemetry = Telemetry(
        user_id=user_id,
        lesson_id=lesson_id,
        component_id=component_id,
        event_type=event_type,
        event_data=json.dumps(event_data)
    )
    
    db.session.add(telemetry)
    db.session.commit()
    
    return jsonify({'message': 'Event tracked'}), 201
