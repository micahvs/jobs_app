from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from application.models.swipe import Swipe
from application import db

bp = Blueprint('swipes', __name__, url_prefix='/api/swipes')

def validate_swipe_data(data):
    required_fields = ['job_id', 'liked']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return {'error': f'Missing required fields: {", ".join(missing_fields)}'}, 400
    return None

@bp.route('/', methods=['POST'])
@jwt_required()
def create_swipe():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    # Validate data
    validation_error = validate_swipe_data(data)
    if validation_error:
        return validation_error

    try:
        # Check if swipe already exists
        existing_swipe = Swipe.query.filter_by(
            user_id=current_user_id,
            job_id=data['job_id']
        ).first()

        if existing_swipe:
            return jsonify({'error': 'Already swiped on this job'}), 400

        # Create new swipe
        swipe = Swipe(
            user_id=current_user_id,
            job_id=data['job_id'],
            liked=data['liked']
        )
        
        db.session.add(swipe)
        db.session.commit()
        
        return jsonify(swipe.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_swipe_stats():
    """Get swipe statistics for the current user"""
    current_user_id = get_jwt_identity()
    
    total_swipes = Swipe.query.filter_by(user_id=current_user_id).count()
    liked_jobs = Swipe.query.filter_by(
        user_id=current_user_id,
        liked=True
    ).count()
    
    return jsonify({
        'total_swipes': total_swipes,
        'liked_jobs': liked_jobs
    })