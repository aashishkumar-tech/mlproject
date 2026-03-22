import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture
def flask_app():
    from app import app

    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(flask_app):
    return flask_app.test_client()
