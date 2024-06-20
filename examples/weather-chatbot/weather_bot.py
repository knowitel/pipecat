import asyncio
import os
import sys

import aiohttp
from dotenv import load_dotenv
from loguru import logger
from pipecat.frames.frames import TextFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.processors.aggregators.llm_response import (
    LLMAssistantContextAggregator,
    LLMUserContextAggregator,
)
from pipecat.processors.logger import FrameLogger
from pipecat.services.openai import OpenAILLMContext, OpenAILLMService
from pipecat.transports.services.daily import DailyParams, DailyTransport
from pipecat.vad.silero import SileroVADAnalyzer

from runner import configure
from services.tts_service import elevenlabs_tts, openai_tts
from services.weather_service import fetch_weather_from_api
from utils.llm_context import llm_context
from utils.user_profile import get_user_profile

load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")

TTS_SERVICE = os.getenv("TTS_SERVICE", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

username = None
location = None


async def start_fetch_weather(llm):
    global username
    await llm.push_frame(
        TextFrame(f"Let me think {username}, I'm fetching the weather for you.")
    )


async def main(room_url: str, token):
    async with aiohttp.ClientSession() as session:
        transport = DailyTransport(
            room_url,
            token,
            "Respond bot",
            DailyParams(
                audio_out_enabled=True,
                transcription_enabled=True,
                vad_enabled=True,
                vad_analyzer=SileroVADAnalyzer(),
            ),
        )
        if TTS_SERVICE == "elevenlabs":
            tts = elevenlabs_tts(session)
        else:
            tts = openai_tts(session)

        llm = OpenAILLMService(api_key=OPENAI_API_KEY, model="gpt-4o")
        llm.register_function(
            "get_current_weather",
            fetch_weather_from_api,
            start_callback=start_fetch_weather,
        )

        fl_in = FrameLogger("Inner")
        fl_out = FrameLogger("Outer")

        context = await llm_context()
        tma_in = LLMUserContextAggregator(context)
        tma_out = LLMAssistantContextAggregator(context)
        pipeline = Pipeline(
            [
                fl_in,
                transport.input(),
                tma_in,
                llm,
                fl_out,
                tts,
                transport.output(),
                tma_out,
            ]
        )

        task = PipelineTask(pipeline)

        @transport.event_handler("on_first_participant_joined")
        async def on_first_participant_joined(transport, participant):
            transport.capture_participant_transcription(participant["id"])
            global username
            global location
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
                await tts.say(
                    f"Hi {username}! Ask me about the weather anywhere in the world."
                )

        runner = PipelineRunner()

        await runner.run(task)


if __name__ == "__main__":
    (url, token) = configure()
    asyncio.run(main(url, token))
