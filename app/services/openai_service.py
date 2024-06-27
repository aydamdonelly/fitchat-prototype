# from openai import OpenAI
from langfuse.openai import OpenAI
import shelve
from dotenv import load_dotenv
from flask import current_app
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langfuse.callback import CallbackHandler
from app.models import DailyProgress
import os
import time
import logging
load_dotenv()


langfuse_handler = CallbackHandler()

#openai client configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
client = OpenAI(api_key=OPENAI_API_KEY)
model = ChatOpenAI(api_key=OPENAI_API_KEY)

#parser and prompt template setup
output_parser = PydanticOutputParser(pydantic_object=DailyProgress)

prompt = PromptTemplate(
    template="Extract the metrics based on these instructions: \n{format_instructions}\n Those are the given information: {query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": output_parser.get_format_instructions()},
)

chain = prompt | model | output_parser

def upload_file():
    # Upload a file with an "assistants" purpose
    file = client.files.create(
        file=open("../../data/diet.pdf", "rb"), purpose="assistants"
    )
    return file


def create_assistant(file):
    """
    You currently cannot set the temperature for Assistant via the API.
    """
    assistant = client.beta.assistants.create(
        name="FitChat",
        instructions="You're a helpful WhatsApp assistant that assists users in their mission to lose weight and to keep track of their calories and steps throughout the day. Use your knowledge base to best respond to customer queries. If you don't know the answer, say simply that you cannot help with question and advice to make research. Be friendly and funny.",
        tools=[{"type": "retrieval"}],
        model="gpt-4-1106-preview",
        file_ids=[file.id],
    )
    return assistant

def classify_message(message):
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are an intelligent assistant. You can only answer with one of the two following words: 'daily' and 'individual', nothing else."},
        {"role": "user", "content": f'You are an intelligent assistant. You can only answer with one of the two following words: "daily" and "individual", nothing else. Your task is to identify whether the given message is a response to a regular activity prompt or a dynamic query.\n            If it\'s a response which provides information about fitness and health metrics of the user like steps or calories (something like \'I have consumed 2144 calories today and walked 12.000 steps\'), respond with "daily".\n If it\'s a dynamic query (something which doesn\'t provide information like mentioned in the regular case, such as a question about a topic related to health), simply respond with "individual".\n\n            MessageI have consumed 2144 calories today and walked 12.000 steps <-- daily. Here is the message you have to classify: {message}'}
    ],
    max_tokens=10,
    temperature=0.9)
    generated_prompt = response.choices[0].message.content.strip()
    return generated_prompt

def progress_rating(message):
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are an intelligent assistant. You greet the user and give him an evaluation of their progress in the last days. Don't list it, comment it and tell him how he is doing. Point out what he is doing well and what he is not doing well."},
        {"role": "user", "content": f'You are an intelligent assistant. You greet the user and give him an evaluation of their progress in the last days Do not just list it, comment it and tell him how he is doing. Point out what he is doing well and what he is not doing well.: Here is a dataset of the progress of the user in the last days, give him an evaluation of their progress and comment on what they are doing well and what they are not doing well: {message}'}
    ],
    max_tokens=200,
    temperature=0.9)
    generated_prompt = response.choices[0].message.content.strip()
    return generated_prompt

def make_statistics(message):
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are an intelligent assistant. You greet the user and give him an evaluation of their progress in the last days by taking average values and commenting on them"},
        {"role": "user", "content": f'You are an intelligent assistant. You greet the user and give him an evaluation of their progress in the last days by taking average values and commenting on them: Here is a dataset of the average progress of the user in the last days, give him an evaluation of their progress and comment on what they are doing well and what they are not doing well: {message}'}
    ],
    max_tokens=200,
    temperature=0.9)
    generated_prompt = response.choices[0].message.content.strip()
    return generated_prompt

# Use context manager to ensure the shelf file is closed properly
def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)

def parse_message(message):
    parsed_message = chain.invoke({"query": message}, config={"callbacks": [langfuse_handler]})
    return parsed_message

def store_thread(wa_id, thread_id):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id


def run_assistant(thread, name):
    # Retrieve the Assistant
    assistant = client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        # instructions=f"You are having a conversation with {name}",
    )

    # Wait for completion
    # https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps#:~:text=under%20failed_at.-,Polling%20for%20updates,-In%20order%20to
    while run.status != "completed":
        # Be nice to the API
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Retrieve the Messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value
    logging.info(f"Generated message: {new_message}")
    return new_message


def generate_response(message_body, wa_id, name):
    # Check if there is already a thread_id for the wa_id
    thread_id = check_if_thread_exists(wa_id)

    # If a thread doesn't exist, create one and store it
    if thread_id is None:
        logging.info(f"Creating new thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.create()
        store_thread(wa_id, thread.id)
        thread_id = thread.id

    # Otherwise, retrieve the existing thread
    else:
        logging.info(f"Retrieving existing thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.retrieve(thread_id)

    # Add message to thread
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_body,
    )

    # Run the assistant and get the new message
    new_message = run_assistant(thread, name)

    return new_message