import datetime
import os
import uuid
from contextlib import closing

import pytest
from server import main
from server.database import Log, Role, User, db, user_datastore
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url

ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Adminn3tje"


@pytest.fixture(scope="session")
def database(db_uri):
    """Create and drop test database for a pytest worker."""
    url = make_url(db_uri)
    db_to_create = url.database

    # database to connect to for creating `db_to_create`.
    url.database = "postgres"
    engine = create_engine(str(url))

    with closing(engine.connect()) as conn:
        print(f"Drop and create {db_to_create}")
        # Can't drop or create a database from within a transaction; end transaction by committing.
        conn.execute("COMMIT;")
        conn.execute(f'DROP DATABASE IF EXISTS "{db_to_create}";')
        conn.execute("COMMIT;")
        conn.execute(f'CREATE DATABASE "{db_to_create}";')
        print(f"Drop and create done for {db_to_create}")
    yield database


@pytest.fixture(scope="session")
def db_uri(worker_id):
    """Ensure that every py.test workerthread uses a own DB, when running the test suite with xdist and `-n auto`."""
    database_uri = "postgresql://logger:logger@localhost/logger-test"
    if os.getenv("DB_USER"):
        print("Running with TRAVIS!")
        database_uri = "postgresql://postgres:@localhost/logger-test"
    if worker_id == "master":
        # pytest is being run without any workers
        print(f"USING DB CONN: {database_uri}")
        return database_uri
    # using xdist setup
    url = make_url(database_uri)
    url.database = f"{url.database}-{worker_id}"
    print(f"USING DB CONN: {url}")
    return str(url)


@pytest.fixture(scope="function")
def app(database):
    """
    Create a Flask app context for the tests.
    """
    from main import app

    with app.app_context():
        db.init_app(app)
        db.create_all()
        # migrate = Migrate(app, db)
        # api.init_app(app)

    yield app

    with app.app_context():
        # clean up : revert DB to a clean state
        db.session.remove()
        db.session.commit()
        db.session.close_all()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def user_roles():
    roles = ["member", "shop", "admin"]
    [db.session.add(Role(id=str(uuid.uuid4()), name=role)) for role in roles]
    db.session.commit()


@pytest.fixture
def admin(user_roles):
    user = user_datastore.create_user(
        username="admin", password=ADMIN_PASSWORD, email=ADMIN_EMAIL
    )
    user_datastore.add_role_to_user(user, "admin")
    user.confirmed_at = datetime.datetime.utcnow()
    db.session.commit()
    return user


@pytest.fixture
def admin_logged_in(admin):
    user = User.query.filter(User.email == ADMIN_EMAIL).first()
    # Todo: actually login/handle cookie
    db.session.commit()
    return user
