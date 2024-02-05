import os
import time

import aiosqlite
import openai
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# Create an OpenAI assistant to provide advice to the player

assistant = client.beta.assistants.create(
    name="LoL Coach Assistant",
    instructions="You are a coach providing advice to a League of Legends player based on their match performance.",
    model="gpt-4-1106-preview",
)

LOL_COACH_ASSISTANT_ID = assistant.id


def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )


def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")


def create_thread_and_run(user_input):
    thread = client.beta.threads.create()
    run = submit_message(LOL_COACH_ASSISTANT_ID, thread, user_input)
    return thread, run


thread1, run1 = create_thread_and_run("Hello, I am a League of Legends coach.")


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
run2 = submit_message(LOL_COACH_ASSISTANT_ID, thread1, "What should I do?")
run2 = wait_on_run(run2, thread1)
pretty_print(get_response(thread1))


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
            return response["choices"][0]["message"]["content"]

        return "No matches found to analyze."
