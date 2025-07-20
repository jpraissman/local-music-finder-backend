import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()

def test_health(client):
    response = client.get('/health')
    print(response)
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}
