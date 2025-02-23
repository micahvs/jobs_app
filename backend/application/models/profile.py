from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY

class Profile(db.Model):
    __tablename__ = 'profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    profile_picture_path = db.Column(db.String(255))
    resume_path = db.Column(db.String(255))
    
    # Professional details
    title = db.Column(db.String(100))
    years_of_experience = db.Column(db.Integer)
    skills = db.Column(ARRAY(db.String))
    
    # Preferences
    preferred_role_types = db.Column(ARRAY(db.String))
    preferred_locations = db.Column(ARRAY(db.String))
    remote_preference = db.Column(db.String(20))  # 'remote', 'hybrid', 'onsite'
    salary_expectation_min = db.Column(db.Integer)
    salary_expectation_max = db.Column(db.Integer)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'bio': self.bio,
            'title': self.title,
            'years_of_experience': self.years_of_experience,
            'skills': self.skills,
            'preferred_role_types': self.preferred_role_types,
            'preferred_locations': self.preferred_locations,
            'remote_preference': self.remote_preference,
            'salary_expectation_min': self.salary_expectation_min,
            'salary_expectation_max': self.salary_expectation_max,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }