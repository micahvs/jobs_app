from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.profile import Profile
import os

bp = Blueprint('profiles', __name__, url_prefix='/api/profiles')

@bp.route('/', methods=['POST'])
@jwt_required()
def create_profile():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Check if profile already exists
    if Profile.query.filter_by(user_id=current_user_id).first():
        return jsonify({'error': 'Profile already exists'}), 400
    
    try:
        profile = Profile(
            user_id=current_user_id,
            full_name=data['full_name'],
            bio=data.get('bio'),
            title=data.get('title'),
            years_of_experience=data.get('years_of_experience'),
            skills=data.get('skills', []),
            preferred_role_types=data.get('preferred_role_types', []),
            preferred_locations=data.get('preferred_locations', []),
            remote_preference=data.get('remote_preference'),
            salary_expectation_min=data.get('salary_expectation_min'),
            salary_expectation_max=data.get('salary_expectation_max')
        )
        
        db.session.add(profile)
        db.session.commit()
        
        return jsonify(profile.to_dict()), 201
        
    except KeyError as e:
        return jsonify({'error': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    profile = Profile.query.filter_by(user_id=current_user_id).first()
    
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
        
    return jsonify(profile.to_dict())

@bp.route('/', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    profile = Profile.query.filter_by(user_id=current_user_id).first()
    
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
        
    data = request.get_json()
    
    try:
        for key, value in data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
                
        db.session.commit()
        return jsonify(profile.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/upload/resume', methods=['POST'])
@jwt_required()
def upload_resume():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    # Ensure uploads directory exists
    if not os.path.exists('uploads/resumes'):
        os.makedirs('uploads/resumes')
        
    # Save file
    try:
        filename = f"resume_{get_jwt_identity()}_{file.filename}"
        file_path = os.path.join('uploads/resumes', filename)
        file.save(file_path)
        
        # Update profile
        profile = Profile.query.filter_by(user_id=get_jwt_identity()).first()
        if profile:
            profile.resume_path = file_path
            db.session.commit()
            
        return jsonify({'message': 'Resume uploaded successfully', 'path': file_path})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500