from flask_migrate import Migrate, MigrateCommand
from flask_script import Command, Manager

from app import init_app
from app.models import db

app = init_app()
# $ flask db --help
migrate = Migrate(app, db)
manager = Manager(app)


class InitDB(Command):
    def run(self):
        db.create_all()
        db.session.commit()


manager.add_command('db', MigrateCommand)
manager.add_command('initdb', InitDB())

if __name__ == '__main__':
    manager.run()
