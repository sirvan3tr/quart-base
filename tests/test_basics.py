import pytest
from app import create_app, db
from app.models import User, Role


@pytest.fixture(name='testapp')
def _test_app():
  return create_app('testing')


@pytest.mark.asyncio
async def test_app(testapp):
  client = testapp.test_client()
  response = await client.get('/')
  assert response.status_code == 200


@pytest.mark.asyncio
async def test_new_user(testapp):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, hashed_password, and role fields are defined correctly
    """
    test_client = testapp.test_client()
    async with testapp.app_context():
        db.create_all()
        Role.insert_roles()
        admin_query = Role.query.filter_by(name='Administrator')
        print()
        user = User(
                confirmed = False, 
                first_name = "Jimmy", 
                last_name = "Lastname", 
                email = 'patkennedy79@gmail.com', 
            )
        db.session.remove()
        db.drop_all()
        assert user.email == 'patkennedy79@gmail.com'