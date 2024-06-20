from pydantic import BaseModel


class UserProfile(BaseModel):
    username: str
    location: str


def get_user_profile(username: str) -> UserProfile:
    # TODO: Implement storing and fetching of user profile and user-data.

    users = {
        'Edwin': UserProfile(username='Edwin', location="Phuket")
    }

    user = users.get(username, None)
    if not user:
        # 1. Create new user in DB (SQLAlchemy + SQLIte or just JSON?)
        # 2. Return user profile information
        # 3. Return a flag indicating that this is a first time user
        pass

    return user
