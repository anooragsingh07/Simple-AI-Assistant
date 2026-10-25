from openai import OpenAI
from dotenv import load_dotenv
from tools import TOOLS, FUNCTION_NAME_TO_FUNCTION_MAP
import json
import os

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

messages = [
    {
        "role": "system",
        "content": (
            "Act like a very humble agent and always respond in under 20 words. "
            "The get_user_city tool returns a fixed Bengaluru demo value, not "
            "the user's actual location."
        )
    }
]

MAX_TOOL_ROUNDS = 5

while True:
    user_input = input("\nAnoorag: ")
    if user_input.lower().strip() in ["exit", "bye", "goodbye", "quit"]:
        print("Assistant: Goodbye, Anoorag!")
        break

    messages.append({
        "role": "user",
        "content": user_input
    })

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            break

        messages.append(msg)

        for tool_call in msg.tool_calls:
            func_name = tool_call.function.name
            try:
                func_args = json.loads(tool_call.function.arguments or "{}")
                if not isinstance(func_args, dict):
                    raise ValueError("Tool arguments must be a JSON object.")

                fn = FUNCTION_NAME_TO_FUNCTION_MAP[func_name]
                result = fn(**func_args)
            except Exception as error:
                result = f"Error while running {func_name}: {error}"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })
    else:
        answer = (
            "Sorry, I couldn't complete this request within "
            f"{MAX_TOOL_ROUNDS} tool-calling rounds."
        )
        messages.append({
            "role": "assistant",
            "content": answer
        })
        print("Assistant:", answer)
        continue

    answer = msg.content or ""

    messages.append({
        "role": "assistant",
        "content": answer
    })

    print("Assistant:", answer)
