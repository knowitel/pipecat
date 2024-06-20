from openai.types.chat import ChatCompletionToolParam
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext

prompt = """
You are a helpful LLM participating in a WebRTC call. 
Your primary goal is to demonstrate your capabilities concisely. 
Since your responses will be converted to audio, avoid using special characters. 
Respond to user queries in a creative and helpful manner. 
For weather-related questions, provide the temperature, current conditions, and recommended actions. 
If the user's query is not about the weather, politely prompt them to ask a weather-related question instead.
"""


async def llm_context():
    tools = [
        ChatCompletionToolParam(
            type="function",
            function={
                "name": "get_current_weather",
                "description": "Get the current weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city e.g. 'London, UK' or 'Paris, France'. State or country information is omitted",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The temperature unit to use. Infer this from the users location.",
                        },
                    },
                    "required": ["location", "format"],
                },
            },
        )
    ]
    messages = [
        {
            "role": "system",
            "content": prompt,
        }
    ]
    return OpenAILLMContext(messages, tools)
