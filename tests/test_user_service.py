


# from db.dummy_db import DummyDB
# from services.user_service import UserService


# @pytest.fixture
# def user_service():
#     db = DummyDB()
#     db.reset()  # Clean state for each test
#     return UserService()

# def test_user_registration(user_service):
#     # Test registration logic
#     user_data = {
#         "username": "testuser",
#         "email": "test@example.com",
#         "pin": "1234"
#     }
    
#     user = user_service.register_user(user_data)
    
#     assert user.id is not None
#     assert user.username == "testuser"