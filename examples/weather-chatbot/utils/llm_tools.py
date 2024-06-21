from openai.types.chat import ChatCompletionToolParam

current_weather = ChatCompletionToolParam(
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
forecast_weather = ChatCompletionToolParam(
    type="function",
    function={
        "name": "get_forecast_weather",
        "description": "Get the forecast weather",
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
