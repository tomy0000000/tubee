"""APShedulerJobs Model"""
from .. import db

class APShedulerJobs(db.Model):
    """A Dummy Model for Flask Migrate"""
    __tablename__ = "apscheduler_jobs"
    id = db.Column(db.String(32), nullable=False, primary_key=True)
    next_run_time = db.Column(db.Float(64), index=True)
    job_state = db.Column(db.LargeBinary, nullable=False)
