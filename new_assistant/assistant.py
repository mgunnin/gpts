import os
import time

import aiosqlite
import openai
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

LOL_COACH_ASSISTANT_ID = assistant_id = os.getenv("LOL_COACH_ASSISTANT_ID")

# Create an OpenAI assistant
# assistant = client.beta.assistants.create(
#     name="LoL Coach Assistant",
#     instructions="You are a coach providing advice to a League of Legends player based on their match performance.",
#     model="gpt-4-1106-preview",
# )


# Create a thread and submit a message
def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )


# Get the response from the assistant
def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")


def create_thread_and_run(user_input):
    thread = client.beta.threads.create()
    run = submit_message(LOL_COACH_ASSISTANT_ID, thread, user_input)
    return thread, run


# Emulating concurrent user requests
thread1, run1 = create_thread_and_run(
    "I need help with improving my League of Legends gameplay. Can you analyze my match history and provide some advice?"
)
thread2, run2 = create_thread_and_run("How can I be a better team player?")
thread3, run3 = create_thread_and_run(
    "What are some advanced strategies for playing League of Legends?"
)


# Pretty printing helper
def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
    print()


# Waiting in a loop
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


# Wait for Run 1
run1 = wait_on_run(run1, thread1)
pretty_print(get_response(thread1))

# Wait for Run 2
run2 = wait_on_run(run2, thread2)
pretty_print(get_response(thread2))

# Wait for Run 3
run3 = wait_on_run(run3, thread3)
pretty_print(get_response(thread3))

# Thank our assistant on Thread 3 :)
run4 = submit_message(LOL_COACH_ASSISTANT_ID, thread3, "Thank you!")
run4 = wait_on_run(run4, thread3)
pretty_print(get_response(thread3))


# Analyze match history and provide advice to the player
async def analyze_and_provide_advice(puuid: str):
    async with aiosqlite.connect("lol_summoner.db") as db:
        cursor = await db.execute(
            "SELECT kills, deaths, assists FROM match_history WHERE puuid = ?",
            (puuid,),
        )
        matches = await cursor.fetchall()
        if matches:
            matches = list(matches)
            avg_kills = sum(match[0] for match in matches) / len(matches)
            avg_deaths = sum(match[1] for match in matches) / len(matches)
            avg_assists = sum(match[2] for match in matches) / len(matches)

            # Create a summary of the match performance
            summary = f"The player had an average of {avg_kills} kills, {avg_deaths} deaths, and {avg_assists} assists per match."

            # Use OpenAI's ChatGPT 4 and Assistants API for generating advice
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a coach providing advice to a League of Legends player based on their match performance.",
                    },
                    {
                        "role": "user",
                        "content": summary
                        + "\nWhat advice would you give to the player?",
                    },
                ],
                temperature=0.5,
                max_tokens=100,
            )
            return response.choices[0].message.content

        return "No matches found to analyze."
