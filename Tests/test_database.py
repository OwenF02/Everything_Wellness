from Models.database import register_user

def test_register_user():
    assert register_user("testuser", "password") == True
