from datetime import datetime
import requests

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_city_weather(city):
    url = f"https://wttr.in/{city}?format=3"
    response = requests.get(url, timeout=10)
    return response.text

def get_user_city():
    return "Bengaluru"

#TOOLS = [{}, {}, {}]
TOOLS = [
    {
        "type" : "function",
        "function" : {
            "name" : "get_current_time",
            "description": (
    "Gets the actual current local date and time from the computer clock. "
    "Use for questions asking what time or date it is now."
),
            "parameters" : {
                "type" : "object",
                "properties" : {}
            },
        },
    },
    {
        "type" : "function",
        "function" : {
            "name" : "get_user_city",
            "description" : (
                "Returns the configured demo city, Bengaluru. This is a fixed "
                "test value, not the user's actual location. Use it only to "
                "demonstrate chained tool calls when the user asks about "
                "weather where they live without naming a city."
            ),
            "parameters" : {
                "type" : "object",
                "properties" : {}
            }
        },
    },
    {
        "type" : "function",
        "function" : {
            "name" : "get_city_weather",
            "description" : "Returns the current weather for a given city.",
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "city" : {
                        "type" : "string",
                        "description" : "City to get the weather for."
                    }
                },
                "required" : ["city"]
            }
        },
    }
]

FUNCTION_NAME_TO_FUNCTION_MAP = {
    "get_current_time" : get_current_time,
    "get_user_city" : get_user_city,
    "get_city_weather" : get_city_weather,
}