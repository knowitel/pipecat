from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from .llm_tools import *


async def llm_context(prompt: str):
    tools = [
        current_weather,
        forecast_weather,
    ]
    messages = [
        {
            "role": "system",
            "content": prompt,
        }
    ]
    return OpenAILLMContext(messages, tools)
