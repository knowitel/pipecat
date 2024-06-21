from pipecat.frames.frames import TextFrame
from .user_profile import get_user_profile


async def greet_user(participant, tts, llm):
    username = participant.get("info").get("userName")
    user = get_user_profile(username)
    if user:
        location = user.location
        await llm.push_frame(
            TextFrame(
                f"Welcome back {username}! Do you need a weather update for {location} or anywhere else?"
            )
        )
    else:
        await tts.say(f"Hi {username}! Ask me about the weather anywhere in the world.")
    return username
