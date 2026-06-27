import json
import os
import urllib.parse
import urllib.request
from urllib.error import URLError

from flask import Flask, jsonify, request

app = Flask(__name__)


def get_city_from_dialogflow(data):
    query_result = data.get("queryResult", {})
    parameters = query_result.get("parameters", {})

    city = parameters.get("city") or parameters.get("geo-city")
    if city:
        return city

    query_text = query_result.get("queryText", "")
    if query_text:
        return query_text.strip()

    return None


def get_weather_summary(city):
    try:
        geocode_url = (
            "https://geocoding-api.open-meteo.com/v1/search?"
            f"name={urllib.parse.quote(city)}&count=1&language=en&format=json"
        )
        with urllib.request.urlopen(geocode_url, timeout=10) as response:
            geocode_data = json.load(response)

        if not geocode_data.get("results"):
            return f"I could not find weather information for {city}."

        result = geocode_data["results"][0]
        lat = result["latitude"]
        lon = result["longitude"]
        location_name = result.get("name", city)

        forecast_url = (
            "https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current=temperature_2m,weather_code&timezone=auto"
        )
        with urllib.request.urlopen(forecast_url, timeout=10) as response:
            weather_data = json.load(response)

        current = weather_data.get("current", {})
        temp = current.get("temperature_2m")
        weather_code = current.get("weather_code")
        weather_desc = describe_weather_code(weather_code)

        if temp is None:
            return f"I found {location_name}, but I could not read the current weather right now."

        return (
            f"The current weather in {location_name} is {weather_desc} "
            f"with a temperature of {temp}°C."
        )
    except URLError:
        return f"I could not reach the weather service right now, but I can still help with {city}."
    except Exception:
        return f"I had trouble getting the weather for {city}."


def describe_weather_code(code):
    weather_map = {
        0: "clear sky",
        1: "mainly clear",
        2: "partly cloudy",
        3: "overcast",
        45: "foggy",
        48: "depositing rime fog",
        51: "light drizzle",
        53: "moderate drizzle",
        55: "dense drizzle",
        61: "slight rain",
        63: "moderate rain",
        65: "heavy rain",
        71: "slight snow",
        73: "moderate snow",
        75: "heavy snow",
        95: "thunderstorm",
        96: "thunderstorm with hail",
        99: "heavy thunderstorm with hail",
    }
    return weather_map.get(code, "unknown weather")


@app.route("/webhook", methods=["GET","POST"])

def webhook():
    if request.method == "GET":
        return "webhook is live"
def index():
    data = request.get_json(silent=True) or {}
    city = get_city_from_dialogflow(data)

    if city:
        response_text = get_weather_summary(city)
    else:
        response_text = "Please tell me the city name so I can check the weather."

    return jsonify({"fulfillmentText": response_text})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)