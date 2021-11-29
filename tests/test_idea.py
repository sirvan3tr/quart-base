import pytest
from app import create_app


@pytest.fixture(name='testapp')
def _test_app():
  return create_app('development')


@pytest.mark.asyncio
async def test_app(testapp):
  client = testapp.test_client()
  response = await client.get('/idea')
  print("------------------", response.__dict__)
  assert response.status_code == 200
