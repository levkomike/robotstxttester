from datetime import datetime
from main import db

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    batch_name = db.Column(db.String(255), nullable=True)
    
    # Relationship with results
    results = db.relationship('AnalysisResult', backref='analysis', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Analysis {self.id} - {self.created_at}>'

class AnalysisResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analysis.id', ondelete='CASCADE'), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    robots_url = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=False)
    google_disallowed = db.Column(db.Boolean, default=False)
    robots_content = db.Column(db.Text, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with disallow rules
    disallow_rules = db.relationship('DisallowRule', backref='result', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<AnalysisResult {self.id} - {self.url}>'
    
    def to_dict(self):
        """Convert the result to a dictionary format (similar to the original structure)"""
        return {
            'url': self.url,
            'robots_url': self.robots_url,
            'status': self.status,
            'google_disallowed': self.google_disallowed,
            'robots_content': self.robots_content,
            'error_message': self.error_message,
            'disallow_rules': [rule.to_dict() for rule in self.disallow_rules]
        }

class DisallowRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('analysis_result.id', ondelete='CASCADE'), nullable=False)
    agent = db.Column(db.String(100), nullable=False)
    rule = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f'<DisallowRule {self.id} - {self.agent}: {self.rule}>'
    
    def to_dict(self):
        """Convert the rule to a dictionary format"""
        return {
            'agent': self.agent,
            'rule': self.rule
        }
