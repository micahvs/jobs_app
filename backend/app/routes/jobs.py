from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import cross_origin
from application import db
from application.models.job import Job
from datetime import datetime, timedelta

bp = Blueprint('jobs', __name__, url_prefix='/api/jobs')

@bp.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def validate_job_data(data, required_fields=None):
    if required_fields is None:
        required_fields = ['title', 'description', 'role_type', 'company_name']
    
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return {'error': f'Missing required fields: {", ".join(missing_fields)}'}, 400
    
    # Validate salary range if provided
    if 'salary_min' in data and 'salary_max' in data:
        if data['salary_min'] > data['salary_max']:
            return {'error': 'Minimum salary cannot be greater than maximum salary'}, 400
    
    return None

@bp.route('/', methods=['OPTIONS'])
@cross_origin()
def handle_options():
    return '', 200

@bp.route('/', methods=['POST'])
@jwt_required()
def create_job():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    validation_error = validate_job_data(data)
    if validation_error:
        return validation_error
    
    try:
        # Convert skills lists to comma-separated strings
        required_skills = ','.join(data.get('required_skills', []))
        preferred_skills = ','.join(data.get('preferred_skills', []))
        
        # Set expiration date (default 30 days)
        expires_at = datetime.utcnow() + timedelta(days=data.get('duration_days', 30))
        
        job = Job(
            employer_id=current_user_id,
            title=data['title'],
            description=data['description'],
            role_type=data['role_type'],
            experience_level=data.get('experience_level'),
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            location=data.get('location'),
            remote_type=data.get('remote_type'),
            salary_min=data.get('salary_min'),
            salary_max=data.get('salary_max'),
            equity_offered=data.get('equity_offered', False),
            company_name=data['company_name'],
            company_description=data.get('company_description'),
            company_size=data.get('company_size'),
            company_funding=data.get('company_funding'),
            expires_at=expires_at
        )
        
        db.session.add(job)
        db.session.commit()
        
        return jsonify(job.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['GET'])
@jwt_required()
def get_jobs():
    current_user_id = get_jwt_identity()
    
    # Get query parameters
    is_active = request.args.get('active', 'true').lower() == 'true'
    
    jobs = Job.query.filter_by(
        employer_id=current_user_id,
        is_active=is_active
    ).order_by(Job.created_at.desc()).all()
    
    return jsonify([job.to_dict() for job in jobs])

@bp.route('/<int:job_id>', methods=['GET'])
@jwt_required()
def get_job(job_id):
    job = Job.query.get_or_404(job_id)
    return jsonify(job.to_dict())

@bp.route('/<int:job_id>', methods=['PUT'])
@jwt_required()
def update_job(job_id):
    current_user_id = get_jwt_identity()
    job = Job.query.get_or_404(job_id)
    
    if job.employer_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    
    # Validate updates
    validation_error = validate_job_data(data, required_fields=[])
    if validation_error:
        return validation_error
    
    try:
        # Update skills if provided
        if 'required_skills' in data:
            data['required_skills'] = ','.join(data['required_skills'])
        if 'preferred_skills' in data:
            data['preferred_skills'] = ','.join(data['preferred_skills'])
            
        for key, value in data.items():
            if hasattr(job, key) and key != 'id':  # Prevent updating id
                setattr(job, key, value)
                
        db.session.commit()
        return jsonify(job.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:job_id>/deactivate', methods=['POST'])
@jwt_required()
def deactivate_job(job_id):
    current_user_id = get_jwt_identity()
    job = Job.query.get_or_404(job_id)
    
    if job.employer_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    job.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Job deactivated successfully'})

@bp.route('/feed', methods=['GET'])
@jwt_required()
def get_job_feed():
    """Get jobs for candidate feed"""
    current_user_id = get_jwt_identity()
    
    # Get jobs that:
    # 1. Are active
    # 2. Haven't expired
    # 3. Haven't been swiped on by this user
    jobs = Job.query.filter(
        Job.is_active == True,
        Job.expires_at > datetime.utcnow()
    ).order_by(Job.created_at.desc()).all()
    
    return jsonify([job.to_dict() for job in jobs])

@bp.route('/search', methods=['GET'])
@jwt_required()
def search_jobs():
    """Search jobs with filters"""
    # Get search parameters
    role_type = request.args.get('role_type')
    location = request.args.get('location')
    remote_type = request.args.get('remote_type')
    min_salary = request.args.get('min_salary', type=int)
    
    # Build query
    query = Job.query.filter(
        Job.is_active == True,
        Job.expires_at > datetime.utcnow()
    )
    
    if role_type:
        query = query.filter(Job.role_type == role_type)
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    if remote_type:
        query = query.filter(Job.remote_type == remote_type)
    if min_salary:
        query = query.filter(Job.salary_max >= min_salary)
    
    jobs = query.order_by(Job.created_at.desc()).all()
    return jsonify([job.to_dict() for job in jobs])