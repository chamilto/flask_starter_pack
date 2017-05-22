from datetime import datetime
import random

from flask import g, current_app as app
from itsdangerous import (BadSignature,
                          SignatureExpired,
                          TimedJSONWebSignatureSerializer,)
from passlib.apps import custom_app_context

from app import auth, db


@auth.verify_password
def verify_password(username_or_token, password):
    user = User.verify_auth_token(username_or_token)
    if not user:
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


class User(db.Model):
    """User Model
    """
    __tablename__ = 'User'

    user_id = db.Column(db.Integer, primary_key=True)  # auto incrementing pk
    username = db.Column(db.String(128), unique=True)
    email = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128))
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))
    created = db.Column(db.DateTime())
    updated = db.Column(db.DateTime())
    registered = db.Column(db.DateTime)
    registration_code = db.Column(db.Integer)
    registration_confirmed = db.Column(db.Boolean)

    @staticmethod
    def hash_password(password):
        return custom_app_context.encrypt(password)

    def verify_password(self, password):
        return custom_app_context.verify(password, self.password)

    def generate_auth_token(self, expiration=600):
        signature = TimedJSONWebSignatureSerializer(
            app.config['SECRET_KEY'],
            expires_in=expiration
        )
        return signature.dumps({'userId': self.user_id})

    @staticmethod
    def verify_auth_token(token):
        signature = TimedJSONWebSignatureSerializer(app.config['SECRET_KEY'])
        try:
            data = signature.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None

        user = User.query.get(data['userId'])

        return user

    @property
    def serialize(self):
        return {
            'userId': self.user_id,
            'username': self.username,
            'firstName': self.first_name,
            'lastName': self.last_name,
        }

    def __init__(self, username, password, email):
        self.username = username
        self.password = User.hash_password(password)
        self.email = email
        self.created = datetime.now()
        self.registration_code = random.randint(10000, 99999)
        self.registration_confirmed = False
