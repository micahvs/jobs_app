from application import db
from datetime import datetime

class Swipe(db.Model):
    __tablename__ = 'swipes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    liked = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('swipes', lazy=True))
    job = db.relationship('Job', backref=db.backref('swipes', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'liked': self.liked,
            'created_at': self.created_at.isoformat()
        }