from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List


class Appointment(BaseModel):
    date: datetime
    description: str


class UserCalendar(BaseModel):
    username: str
    appointments: List[Appointment]


class UserProfile(BaseModel):
    username: str
    location: str
    calendar: UserCalendar


def get_user_profile(username: str) -> UserProfile:
    # TODO: Implement storing and fetching of user profile and user-data.

    # fmt: off
    appointments = [
        Appointment(date=datetime.now() + timedelta(days=0, hours=5), description="Doctor's appointment"),
        Appointment(date=datetime.now() + timedelta(days=1, hours=5), description="Lunch with friends"),
        Appointment(date=datetime.now() + timedelta(days=2, hours=5), description="Project deadline"),
        Appointment(date=datetime.now() + timedelta(days=3, hours=5), description="Gym session"),
        Appointment(date=datetime.now() + timedelta(days=4, hours=5), description="Dinner date"),
    ]
    # fmt: off

    user_calendar = UserCalendar(username=username, appointments=appointments)

    users = {"Edwin": UserProfile(username="Edwin", location="Phuket", calendar=user_calendar)}

    user = users.get(username, None)
    if not user:
        # 1. Create new user in DB (SQLAlchemy + SQLIte or just JSON?)
        # 2. Return user profile information
        # 3. Return a flag indicating that this is a first time user
        pass

    return user
