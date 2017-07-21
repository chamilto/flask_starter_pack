from flask_testing import TestCase
from base64 import b64encode

from app import db, init_app


class BaseTest(TestCase):
    headers = {'Content-Type': 'application/json'}
    # We need an app obj on the class to use our setUpClass
    # and tearDownClass methods.
    _app = init_app(testing=True)

    @classmethod
    def setUpClass(cls):
        with cls._app.app_context():
            db.create_all()
            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        with cls._app.app_context():
            # You can choose to not truncate certain tables if you want to
            # persist data between runs:
            # if table.name == 'User':
            #     continue
            for table in db.metadata.sorted_tables:
                db.session.execute(table.delete())
            db.session.commit()
            db.session.remove()

    @classmethod
    def _headers_with_username_password(cls, username, password):
        auth_header = {
            'Authorization': 'Basic ' + b64encode("{0}:{1}".format(
                username, password))
        }
        headers = cls.headers.copy()
        headers.update(auth_header)

        return headers

    @classmethod
    def _headers_with_auth_token(cls, token):
        auth_header = {
            'Authorization': 'Basic ' + b64encode("{0}:unused".format(token))
        }
        headers = cls.headers.copy()
        headers.update(auth_header)

        return headers

    def create_app(self):
        return self._app
