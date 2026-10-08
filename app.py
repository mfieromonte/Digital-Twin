from openai import OpenAI
from context import TWIN_SYSTEM_PROMPT
from tools import handle_tool_calls, tools
from styles import CSS, EXAMPLES, JS
from dotenv import load_dotenv
import gradio as gr

load_dotenv(override=True)

MODEL_NAME = "gpt-5.4-mini"

openai = OpenAI()
system = [{"role": "system", "content": TWIN_SYSTEM_PROMPT}]


def chat(message, history):
    messages = system + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=tools,
    )

    while response.choices[0].finish_reason == "tool_calls":
        assistant_message = response.choices[0].message
        messages.append(assistant_message)
        messages.extend(handle_tool_calls(assistant_message.tool_calls))

        response = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools,
        )

    return response.choices[0].message.content


if __name__ == "__main__":
    gr.ChatInterface(
        chat,
        examples=EXAMPLES,
        title="Martina Fieromonte Digital Twin",
        description="Ask my AI twin about my CV, experience, projects and skills.",
        chatbot=gr.Chatbot(show_label=False),
    ).launch(css=CSS, js=JS, theme=gr.themes.Base())
