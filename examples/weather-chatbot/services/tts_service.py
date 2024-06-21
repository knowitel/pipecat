import os
from pipecat.services.elevenlabs import ElevenLabsTTSService
import aiohttp

from typing import AsyncGenerator

from pipecat.frames.frames import AudioRawFrame, Frame, ErrorFrame
from openai import OpenAI
from loguru import logger

from pipecat.services.ai_services import TTSService


def elevenlabs_tts(session):
    return ElevenLabsTTSService(
        aiohttp_session=session,
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        voice_id=os.getenv("ELEVENLABS_VOICE_ID"),
    )


class OpenAITTSService(TTSService):
    def __init__(
        self, *, aiohttp_session: aiohttp.ClientSession, api_key: str, **kwargs
    ):
        super().__init__(**kwargs)
        self._api_key = api_key
        self._aiohttp_session = aiohttp_session

    def can_generate_metrics(self) -> bool:
        return True

    async def run_tts(self, text: str) -> AsyncGenerator[Frame, None]:
        logger.debug(f"Generating TTS: [{text}]")
        client = OpenAI()
        with client.audio.speech.with_streaming_response.create(
            model="tts-1", voice="fable", input=text, response_format="pcm", speed=1.5
        ) as response:
            if response.status_code != 200:
                text = await response.text()
                logger.error(
                    f"{self} error getting audio (status: {response.status}, error: {text})"
                )
                yield ErrorFrame(
                    f"Error getting audio (status: {response.status}, error: {text})"
                )
                return
            for chunk in response.iter_bytes(chunk_size=2048):
                if len(chunk) > 0:
                    frame = AudioRawFrame(chunk, 24000, 2)
                    yield frame


def openai_tts(session):
    return OpenAITTSService(
        aiohttp_session=session,
        api_key=os.getenv("OPENAI_API_KEY"),
    )
