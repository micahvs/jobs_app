from application import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY

class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Job details
    role_type = db.Column(db.String(50), nullable=False)  # e.g., 'full-time', 'contract'
    experience_level = db.Column(db.String(50))  # e.g., 'entry', 'senior'
    required_skills = db.Column(db.String(500))  # Store as comma-separated string
    preferred_skills = db.Column(db.String(500))  # Store as comma-separated string
    
    # Location and work type
    location = db.Column(db.String(100))
    remote_type = db.Column(db.String(20))  # 'remote', 'hybrid', 'onsite'
    
    # Compensation
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    equity_offered = db.Column(db.Boolean, default=False)
    
    # Company info
    company_name = db.Column(db.String(100), nullable=False)
    company_description = db.Column(db.Text)
    company_size = db.Column(db.String(50))  # e.g., '1-10', '11-50'
    company_funding = db.Column(db.String(50))  # e.g., 'Seed', 'Series A'
    
    # Status and timestamps
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'employer_id': self.employer_id,
            'title': self.title,
            'description': self.description,
            'role_type': self.role_type,
            'experience_level': self.experience_level,
            'required_skills': self.required_skills.split(',') if self.required_skills else [],
            'preferred_skills': self.preferred_skills.split(',') if self.preferred_skills else [],
            'location': self.location,
            'remote_type': self.remote_type,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'equity_offered': self.equity_offered,
            'company_name': self.company_name,
            'company_description': self.company_description,
            'company_size': self.company_size,
            'company_funding': self.company_funding,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    