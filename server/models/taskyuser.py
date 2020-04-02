from server import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class TaskyUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    tasks = db.relationship('TaskyTask', backref='assignedTo', lazy='dynamic')

    def __repr__(self):
        return '<TaskyUser {}>'.format(self.username)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
