from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import cross_origin
from application import db
from application.models.job import Job
from datetime import datetime, timedelta

bp = Blueprint('jobs', __name__, url_prefix='/api/jobs')

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

@bp.route('/', methods=['GET'])
@jwt_required()
@cross_origin(origins=['http://localhost:3000'], methods=['GET', 'OPTIONS'])
def get_jobs():
    print("GET /jobs endpoint called")
    try:
        current_user_id = get_jwt_identity()
        print(f"User ID from token: {current_user_id}")
        
        # Get query parameters
        is_active = request.args.get('active', 'true').lower() == 'true'
        print(f"Fetching jobs with is_active={is_active}")
        
        jobs = Job.query.filter_by(
            employer_id=current_user_id,
            is_active=is_active
        ).order_by(Job.created_at.desc()).all()
        
        result = [job.to_dict() for job in jobs]
        print(f"Found {len(result)} jobs")
        return jsonify(result)
    
    except Exception as e:
        print(f"Error in get_jobs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
@cross_origin(origins=['http://localhost:3000'], methods=['POST', 'OPTIONS'])
def create_job():
    print("POST /jobs endpoint called")
    current_user_id = get_jwt_identity()
    data = request.get_json()
    print(f"Received job data: {data}")
    
    # Validate required fields
    validation_error = validate_job_data(data)
    if validation_error:
        print(f"Validation error: {validation_error}")
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
        print(f"Created job with ID: {job.id}")
        
        return jsonify(job.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating job: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:job_id>', methods=['GET'])
@jwt_required()
@cross_origin(origins=['http://localhost:3000'], methods=['GET', 'OPTIONS'])
def get_job(job_id):
    print(f"GET /jobs/{job_id} endpoint called")
    job = Job.query.get_or_404(job_id)
    return jsonify(job.to_dict())

@bp.route('/<int:job_id>', methods=['PUT'])
@jwt_required()
@cross_origin(origins=['http://localhost:3000'], methods=['PUT', 'OPTIONS'])
def update_job(job_id):
    print(f"PUT /jobs/{job_id} endpoint called")
    current_user_id = get_jwt_identity()
    job = Job.query.get_or_404(job_id)
    
    if job.employer_id != current_user_id:
        print(f"Unauthorized update attempt by user {current_user_id}")
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    print(f"Update data: {data}")
    
    try:
        for key, value in data.items():
            if hasattr(job, key) and key != 'id':  # Prevent updating id
                setattr(job, key, value)
                
        db.session.commit()
        print(f"Successfully updated job {job_id}")
        return jsonify(job.to_dict())
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating job: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:job_id>/deactivate', methods=['POST'])
@jwt_required()
@cross_origin(origins=['http://localhost:3000'], methods=['POST', 'OPTIONS'])
def deactivate_job(job_id):
    print(f"POST /jobs/{job_id}/deactivate endpoint called")
    current_user_id = get_jwt_identity()
    job = Job.query.get_or_404(job_id)
    
    if job.employer_id != current_user_id:
        print(f"Unauthorized deactivation attempt by user {current_user_id}")
        return jsonify({'error': 'Unauthorized'}), 403
    
    job.is_active = False
    db.session.commit()
    print(f"Successfully deactivated job {job_id}")
    
    return jsonify({'message': 'Job deactivated successfully'})

@bp.route('/feed', methods=['GET'])
@jwt_required()
@cross_origin(origins=['http://localhost:3000'], methods=['GET', 'OPTIONS'])
def get_job_feed():
    print("GET /jobs/feed endpoint called")
    current_user_id = get_jwt_identity()
    
    jobs = Job.query.filter(
        Job.is_active == True,
        Job.expires_at > datetime.utcnow()
    ).order_by(Job.created_at.desc()).all()
    
    print(f"Found {len(jobs)} jobs for feed")
    return jsonify([job.to_dict() for job in jobs])