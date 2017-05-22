from time import sleep

from flask import (abort,
                   Blueprint,
                   g,
                   jsonify,
                   request,
                   url_for,
                   current_app as app)
from requests import HTTPError
from sqlalchemy.exc import SQLAlchemyError

from app import auth, cache, db
from app.api.urls import URLS
from app.api.users.schemas import (
    confirm_registration_schema,
    register_user_schema
)
from app.lib.email import send_email
from app.lib.validation import validate_schema
from app.models.users import User


users = Blueprint('users', __name__, url_prefix='/users')
urls = URLS['users']


@users.route(urls['token'], methods=['GET'])
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()

    return jsonify({'token': token.decode('ascii')})


@users.route(urls['get'], methods=['GET'])
@auth.login_required
def get_user(username):
    user = User.query.filter_by(username=str(username)).first()

    if user is None:
        app.logger.info('User {0} not found.'.format(username))
        abort(404)

    return jsonify(user.serialize)


@users.route(urls['register'], methods=["POST"])
@validate_schema(register_user_schema)
def register_user():
    sleep(1)  # try to avoid email enumeration attacks
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')

    if User.query.filter_by(username=username).first() is not None:
        app.logger.info('Username {0} already exists.'.format(username))
        abort(409)

    if User.query.filter_by(email=email).first() is not None:
        app.logger.info('Email {0} already exists.'.format(email))
        abort(409)

    user = User(username, password, email)
    try:
        db.session.add(user)
        db.session.commit()
        app.logger.info("User {0} commited to DB.".format(username))
    except SQLAlchemyError as ex:
        app.logger.error("Could not add user {0}: {1}".format(username, ex))
        abort(500)

    try:
        resp = send_email(
            to=user.email,
            subject='Thank you for registering!',
            body='Registration code: {registration_code}'.format(
                registration_code=user.registration_code)
        )
        resp.raise_for_status()
    except HTTPError as ex:
        message = 'Failed to email registration code to '
        '{email}: {ex}'.format(email=user.email, ex=ex)
        app.logger.error(message)
        error_resp = jsonify({
            'errorMsg': message.split(':')[0],
        })
        error_resp.status_code = 500

        return error_resp

    return_obj = user.serialize
    return_obj['uri'] = url_for('users.get_user',
                                username=username,
                                _external=True)

    return jsonify(return_obj)


@users.route(urls['confirm'], methods=['POST'])
@auth.login_required
@validate_schema(confirm_registration_schema)
def confirm_registration(username):
    user = User.query.filter_by(username=username).first()
    secret_code = request.json.get('registrationCode')

    if user is None:
        abort(400)

    if int(secret_code) == int(user.registration_code):
        try:
            user.registration_confirmed = True
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError as ex:
            app.logger.info(
                'Could not commit user to database: {0}'.format(ex)
            )
            abort(500)

        return jsonify(user.serialize)
    else:
        app.logger.info(
            'User {0}: Secret code did not match.'.format(user.username)
        )
        abort(400)


@users.route('/this_is_cached', methods=['GET'])
@cache.cached(timeout=300)
def example_cached_handler():
    from datetime import datetime
    return jsonify({
        'time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    })
