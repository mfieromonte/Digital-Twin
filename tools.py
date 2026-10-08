import json
import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

###to send message
pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")

pushover_url = "https://api.pushover.net/1/messages.json"

def push(text):
    requests.post(
        pushover_url,
        data={
            "token": pushover_token,
            "user": pushover_user,
            "message": text,
        },
    )


###to record emails
def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording interest from {name} with email {email} and notes {notes}")

###to save unrelated questions
def record_unknown_question(question):
    push(f"Recording {question} asked that I couldn't answer")
    return "OK"

###create tools
record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The email address of this user"},
            "name": {"type": "string", "description": "The user's name, if they provided it"},
            "notes": {
                "type": "string",
                "description": "Any additional info about the conversation that's worth recording to give context",
            },
        },
        "required": ["email"],
        "additionalProperties": False,
    },
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The question that couldn't be answered"},
        },
        "required": ["question"],
        "additionalProperties": False,
    },
}

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
]

tool_map = {
    "record_user_details": record_user_details,
    "record_unknown_question": record_unknown_question,
}


###manage tools
def handle_tool_calls(tool_calls):
    # Collect the outputs that must be sent back to the LLM after each tool call.
    results = []

    for tool_call in tool_calls:
        # The model tells us which tool it wants to call.
        tool_name = tool_call.function.name

        # Tool arguments arrive as a JSON string, so convert them to a Python dict.
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool called: {tool_name}", flush=True)

        # Look up the matching Python function and call it with the model's arguments.
        tool = tool_map.get(tool_name)
        result = tool(**arguments) if tool else "Unknown tool: " + tool_name

        # Return the result in OpenAI's expected tool-message format.
        results.append(
            {"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id}
        )

    return results
