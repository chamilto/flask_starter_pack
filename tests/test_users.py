from functools import partial
import json
import mock

from flask import url_for

from app import db
from app.models.users import User
from common import BaseTest


class TestUsersApi(BaseTest):
    """
    Users API Functional Tests.
    """
    username = 'testuser'
    password = 'password'
    email = 'testuser@test.com'
    first_name = 'test'
    last_name = 'user'

    def setUp(self):
        self.register = partial(self.client.post,
                                url_for('users.register_user', _external=True),
                                headers=self.headers)

    def tearDown(self):
        User.query.delete()
        db.session.commit()

    def _create_user(self):
        user = User(self.username, self.password, self.email)
        db.session.add(user)
        db.session.commit()

        return user

    def test_registration_missing_username(self):
        """
        Asserts that missing username responds with 400.
        """
        data = json.dumps({
            'password': self.password,
        })
        resp = self.register(data=data)
        self.assertEquals(resp.status_code, 400)

    def test_registration_missing_password(self):
        """
        Assert that missing password responds with 400.
        """
        data = json.dumps({
            'username': self.username,
        })
        resp = self.register(data=data)
        self.assertEquals(resp.status_code, 400)

    def test_user_already_exists(self):
        """
        Assert that trying to register with a username that already exists
        responds with 409.
        """
        user = self._create_user()
        db.session.add(user)
        db.session.commit()
        data = json.dumps({
            'username': self.username,
            'password': self.password,
            'email': self.email,
        })
        resp = self.register(data=data)
        self.assertEquals(resp.status_code, 409)

    @mock.patch('app.api.users.users.send_email')
    def test_registration_success(self, send_email):
        """
        Happy path user registration.
        """
        send_email.return_value = mock.MagicMock()
        user = User(self.username, self.password, self.email)
        data = json.dumps({
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'firstName': self.first_name,
            'lastName': self.last_name
        })
        resp = self.register(data=data)
        self.assertEquals(resp.status_code, 200)
        expected_return_obj = user.serialize
        expected_return_obj['uri'] = url_for('users.get_user',
                                             username=self.username,
                                             _external=True)
        self.assertEquals(resp.json['username'],
                          expected_return_obj['username'])
        self.assertEquals(resp.json['firstName'],
                          expected_return_obj['firstName'])
        self.assertEquals(resp.json['lastName'],
                          expected_return_obj['lastName'])
        self.assertEquals(resp.json['uri'], expected_return_obj['uri'])

    def test_confirm_registration_success(self):
        """Happy Path user registration confirmation."""
        user = self._create_user()
        registration_code = user.registration_code
        data = json.dumps({
            'registrationCode': registration_code
        })

        resp = self.client.post(
            url_for('users.confirm_registration', username=self.username,
                    _external=True),
            headers=self._headers_with_username_password(
                username=self.username,
                password=self.password), data=data
        )

        self.assertEquals(resp.status_code, 200)

    def test_confirm_registration_wrong_auth(self):
        """Test that incorrect authentication for confirm registration
           responds with 401."""
        user = self._create_user()
        registration_code = user.registration_code
        data = json.dumps({
            'registrationCode': registration_code
        })

        resp = self.client.post(
            url_for('users.confirm_registration',
                    username=self.username,
                    _external=True),
            headers=self._headers_with_username_password(
                username=self.username,
                password='incorrect'), data=data
        )

        self.assertEquals(resp.status_code, 401)

    def test_confirm_registration_wrong_registration_code(self):
        """Confirm that providing the wrong registration code
            responds with 400."""
        self._create_user()
        data = json.dumps({
            'registrationCode': 1
        })

        resp = self.client.post(
            url_for('users.confirm_registration',
                    username=self.username,
                    _external=True),
            headers=self._headers_with_username_password(
                username=self.username,
                password=self.password), data=data
        )

        self.assertEquals(resp.status_code, 400)

    def test_get_auth_token_and_get_user(self):
        self._create_user()
        resp = self.client.get(
            url_for('users.get_auth_token', _external=True),
            headers=self._headers_with_username_password(
                self.username, self.password)
        )
        self.assertEquals(resp.status_code, 200)

        token = resp.json['token']
        resp = self.client.get(
            url_for('users.get_user',
                    username=self.username,
                    _external=True),
            headers=self._headers_with_auth_token(token=token))
        self.assertEquals(resp.status_code, 200)

    def test_get_user_bad_auth(self):
        resp = self.client.get(
            url_for('users.get_user',
                    username=self.username,
                    _external=True),
            headers=self._headers_with_auth_token(token='bad_token'))
        self.assertEquals(resp.status_code, 401)

    def test_get_token_bad_password(self):
        resp = self.client.get(
            url_for('users.get_auth_token', _external=True),
            headers=self._headers_with_username_password(
                self.username, 'bad_password')
        )
        self.assertEquals(resp.status_code, 401)
