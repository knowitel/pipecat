import os

import aiohttp
from utils.unit_conversion import convert_kelvin
from datetime import datetime


async def fetch_current_weather_from_api(llm, args):
    location = args.get("location")
    temp_format = args.get("format")

    api_url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"q={location}&appid={os.getenv('OPENWEATHERMAP_API_KEY')}"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            data = await resp.json()

    temperature_kelvin = data["main"]["temp"]

    temp = convert_kelvin(temp_format, temperature_kelvin)

    conditions = data["weather"][0]["description"]

    return {"conditions": conditions, "temperature": temp}


async def fetch_forecast_weather_from_api(llm, args):
    location = args.get("location")
    temp_format = args.get("format")

    api_url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"q={location}&appid={os.getenv('OPENWEATHERMAP_API_KEY')}"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            data = await resp.json()

    forecast = {}
    for item in data["list"]:
        date = datetime.utcfromtimestamp(item["dt"]).strftime("%d-%m-%Y")
        temperature_kelvin = item["main"]["temp"]
        temp = convert_kelvin(temp_format, temperature_kelvin)
        conditions = item["weather"][0]["description"]
        forecast[date] = {"conditions": conditions, "temperature": temp}

    return forecast
