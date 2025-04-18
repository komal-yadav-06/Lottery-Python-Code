import os
import time
import random
import re
from datetime import datetime, timedelta

# Constants
REGISTRATION_DURATION = 3600  # 1 hour in seconds
EXTENSION_DURATION = 1800     # 30 minutes in seconds
MIN_USERS = 5
LOG_FILE = "lottery_log.txt"
TIMER_FILE = "timer_state.txt"
AUTOSAVE_INTERVAL = 2       # 2 seconds

# Global variables
registered_users = set()
start_time = datetime.now()
last_autosave_time = start_time

# Load end_time from file if available
if os.path.exists(TIMER_FILE):
    with open(TIMER_FILE, "r") as f:
        saved_time = f.read().strip()
        try:
            end_time = datetime.fromisoformat(saved_time)
        except ValueError:
            end_time = start_time + timedelta(seconds=REGISTRATION_DURATION)
else:
    end_time = start_time + timedelta(seconds=REGISTRATION_DURATION)

# Load previously registered users
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r") as file:
        for line in file:
            if line.strip() and not line.startswith("Winner:"):
                registered_users.add(line.strip())

def save_end_time():
    with open(TIMER_FILE, "w") as f:
        f.write(end_time.isoformat())

def is_valid_username(username):
    username = username.strip()
    return bool(username) and bool(re.match(r"^[a-zA-Z ]+$", username))

def autosave_users():
    global last_autosave_time
    with open(LOG_FILE, "w") as file:
        for user in registered_users:
            file.write(f"{user}\n")
    last_autosave_time = datetime.now()

def display_status():
    remaining_time = (end_time - datetime.now()).total_seconds()
    if remaining_time > 0:
        print(f"\nRemaining registration time: {int(remaining_time // 60)} minutes {int(remaining_time % 60)} seconds")
    print(f"Registered users: {len(registered_users)}")

def register_user():
    global end_time
    while datetime.now() < end_time:
        username = input("Enter full name (Alphanumeric): ").strip()
        formatted_username = " ".join(word.capitalize() for word in username.split())
        
        if not username:
            print("Name cannot be empty. Please try again.")
        elif not is_valid_username(username):
            print("Name can only contain letters and spaces. Please try again.")
        elif formatted_username in registered_users:
            print("This name is already registered. Please try again.")
        else:
            registered_users.add(formatted_username)
            print(f"User '{formatted_username}' registered successfully.")
            if (datetime.now() - last_autosave_time).total_seconds() >= AUTOSAVE_INTERVAL:
                autosave_users()
            save_end_time()
            break

def pick_winner():
    global end_time
    if len(registered_users) >= MIN_USERS:
        winner = random.choice(list(registered_users))
        print(f"\n🎉 The winner is: {winner} 🎉")
        print(f"Total participants: {len(registered_users)}")
        with open(LOG_FILE, "a") as file:
            file.write(f"Winner: {winner}\n")
        if os.path.exists(TIMER_FILE):
            os.remove(TIMER_FILE)
    else:
        print("\nNot enough users registered. Extending registration by 30 minutes.")
        end_time += timedelta(seconds=EXTENSION_DURATION)
        save_end_time()
        while datetime.now() < end_time:
            display_status()
            register_user()
        if len(registered_users) >= MIN_USERS:
            pick_winner()
        else:
            print("\nStill not enough users registered. Exiting the program.")
            with open(LOG_FILE, "a") as file:
                file.write("No winner selected due to insufficient participants.\n")

# Main program
try:
    print("Welcome to the Lottery Registration System!")
    print(f"Registration ends at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    while datetime.now() < end_time:
        display_status()
        register_user()
    pick_winner()
except KeyboardInterrupt:
    print("\nProgram interrupted. Autosaving current registrations and time...")
    autosave_users()
    save_end_time()
    print("Exiting the program.")
