import asyncio
import os
import sys

import aiohttp
from dotenv import load_dotenv
from loguru import logger
from pipecat.frames.frames import TextFrame
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.services.openai import OpenAILLMService
from pipecat.transports.services.daily import DailyParams, DailyTransport
from pipecat.vad.silero import SileroVADAnalyzer

from runner import configure
from services.tts_service import elevenlabs_tts, openai_tts
from services.weather_service import fetch_current_weather_from_api, fetch_forecast_weather_from_api
from utils.llm_context import llm_context
from utils.user_message import greet_user
from utils.task_pipeline import task_pipeline
from prompts.prompts import weather_bot_prompt

load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")

TTS_SERVICE = os.getenv("TTS_SERVICE", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

# These would need to be handled on a data level in a real-world application
username = None
location = None


async def start_fetch_weather(llm):
    global username
    await llm.push_frame(
        TextFrame(f"Let me think {username}, I'm fetching the weather for you.")
    )


async def main(room_url: str, token):
    async with aiohttp.ClientSession() as session:

        # Create the LLM Context (system prompt + tools)
        prompt = weather_bot_prompt()
        system_context = await llm_context(prompt=prompt)

        # Set LLM provider & function call
        if LLM_PROVIDER == 'openai':
            llm = OpenAILLMService(api_key=OPENAI_API_KEY, model="gpt-4o")
        else:
            raise NotImplementedError("LLM Provider not implemented")

        llm.register_function(
            "get_current_weather",
            fetch_current_weather_from_api,
            start_callback=start_fetch_weather,
        )
        llm.register_function(
            "get_forecast_weather",
            fetch_forecast_weather_from_api,
            start_callback=start_fetch_weather,
        )

        # Create the audio transport connection and set up the pipeline

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

        # Choose the TTS service for Assistant
        if TTS_SERVICE == "elevenlabs":
            tts = elevenlabs_tts(session)
        else:
            # Defaults to OpenAI TTS
            tts = openai_tts(session)

        # Create the task pipeline
        pipeline = await task_pipeline(system_context, llm, transport, tts)
        task = PipelineTask(pipeline)

        @transport.event_handler("on_first_participant_joined")
        async def on_first_participant_joined(transport, participant):
            """Greet the user when they join the call"""
            transport.capture_participant_transcription(participant["id"])
            global username
            username = await greet_user(participant=participant, llm=llm, tts=tts)

        # Start the in/out audio transport pipeline with updated context
        runner = PipelineRunner()
        await runner.run(task)


if __name__ == "__main__":
    (url, token) = configure()
    asyncio.run(main(url, token))
