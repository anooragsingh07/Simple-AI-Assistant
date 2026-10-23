from openai import OpenAI
from dotenv import load_dotenv
from tools import TOOLS, FUNCTION_NAME_TO_FUNCTION_MAP
import json
import os
import re

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

messages = [
    {
        "role": "system",
        "content": "Act like a very humble agent and always respond in under 20 words."
    }
]

while True:
    user_input = input("\nAnoorag: ")
    normalized_input = user_input.lower().strip()

    if normalized_input in ["exit", "bye", "goodbye", "quit"]:
        print("Assistant: Goodbye, Anoorag!")
        break

    messages.append({
        "role": "user",
        "content": user_input
    })

    mentions_datetime = re.search(
        r"\b(?:time|date|day|clock)\b",
        normalized_input
    )
    asks_comparison = re.search(
        r"\b(?:different|difference|compare|comparison|versus|vs|between)\b",
        normalized_input
    )
    asks_for_datetime = (
        mentions_datetime
        and not asks_comparison
        and (
            normalized_input in {"time", "date", "day"}
            or re.search(
                r"\b(?:current|currently|right now|now|today|what|tell|give|show)\b",
                normalized_input
            )
        )
    )
    asks_for_weather = re.search(
        r"\b(?:weather|forecast|temperature|rain|snow)\b",
        normalized_input
    )

    if asks_for_datetime:
        result = FUNCTION_NAME_TO_FUNCTION_MAP["get_current_time"]()
        request_messages = messages + [{
            "role": "system",
            "content": (
                "The get_current_time tool returned this exact local date and time: "
                f"{result}. Draft a concise answer using this value exactly. "
                "Do not guess, recalculate, or substitute another date or time."
            )
        }]
        response = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=request_messages
        )
        answer = response.choices[0].message.content or ""
        if result not in answer:
            answer = f"The current date and time is {result}."
    elif asks_for_weather:
        response = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages,
            tools=TOOLS,
            tool_choice={
                "type": "function",
                "function": {"name": "get_city_weather"}
            }
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            raise RuntimeError("Ollama did not return the required weather tool call.")

        messages.append(msg)
        weather_result = None

        for tool_call in msg.tool_calls:
            func_name = tool_call.function.name
            if func_name != "get_city_weather":
                raise ValueError(f"Unexpected tool call: {func_name}")

            func_args = json.loads(tool_call.function.arguments or "{}")
            if not isinstance(func_args, dict) or not isinstance(func_args.get("city"), str):
                raise ValueError("Weather tool call must include a city string.")

            weather_result = FUNCTION_NAME_TO_FUNCTION_MAP[func_name](**func_args)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(weather_result)
            })

        response = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages
        )
        answer = response.choices[0].message.content or ""
        if weather_result and weather_result not in answer:
            answer = f"Current weather: {weather_result}"
    else:
        response = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages
        )
        answer = response.choices[0].message.content or ""

    messages.append({
        "role": "assistant",
        "content": answer
    })

    print("Assistant:", answer)
