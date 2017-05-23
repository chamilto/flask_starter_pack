# Flask Starter Pack
Small starter pack for a Flask JSON API.
* JWT Authentication
* Tests
* Database Migrations
* JSON Schema Validation
* Flask-Script
* Caching with Redis
* Email with Mailgun.

## Quick Start

1. Create and activate a virtualenv for your project.
2. Clone the repository.
3. ```pip install -r requirements.txt```
4. Edit the default.cfg file for local development, or use one of the .skel files to create your own.
    * If you choose to use another config file, you must remember to ```export APP_CONFIG=/path/to/your/config/file```
    * It would also be a good idea to add it to your project's .gitignore file! (local.cfg and prod.cfg are already ignored in this project's .gitignore.)
4. [Create your DB](#database)


## Database
I used MySQL for this starter pack, but you can easily use something else like postgres.
The [Flask-SQLAlchemy](http://flask.pocoo.org/docs/0.12/patterns/sqlalchemy/#flask-sqlalchemy-extension) docs are great.

```
$ python manage.py initdb
$ python manage.py db init
$ python manage.py db migrate
# more flask-migrate options
$ python manage.py db --help
```

## Caching
* If you do not want to use redis, you can use the default caching with [Flask-Cache](https://pythonhosted.org/Flask-Cache/) - just set ```CACHE_TYPE = 'simple'```
in your config file.
* Redis Flask-Cache config example in default.cfg

[Redis Quickstart](https://redis.io/topics/quickstart)
```
# without config
$ redis-server
```

## Running the tests

```$ nosetest -v tests```

## Email
To accompany the example registration and registration confirmation handlers, I included a simple function that calls the Mailgun API to send our emails.

If you choose to not rip out the email functionality, getting started with a free [Mailgun](https://www.mailgun.com/) account for development is really easy.
I mocked the calls out to the email lib function, so if you don't want to set up an account right away, the tests will still pass.

## Acknowledgements
Big thanks to [Miguel Grinberg](https://blog.miguelgrinberg.com/) for his awesome Flask tutorials.
