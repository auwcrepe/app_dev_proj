from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# Store availability data (for demonstration purposes)
availability_data = {}

# Dummy user data (for demonstration purposes)
users = {}

#Dummy trainee data
trainees = {
    "trainee1@example.com": {
        "name": "John Doe",
        "tasks_completed": ["Python Training", "GUI Training"],
        "progress": "80%",
        "feedback": [],
    },
    "trainee2@example.com": {
        "name": "Jane Smith",
        "tasks_completed": ["Python Training"],
        "progress": "50%",
        "feedback": [],
    },
}

# AI-based scheduling logic
def generate_ai_schedule(day, start_time, end_time):
    # Convert input times to datetime objects for easier manipulation
    start_datetime = datetime.strptime(start_time, "%H:%M")
    end_datetime = datetime.strptime(end_time, "%H:%M")

    # Calculate the total available time
    total_time = end_datetime - start_datetime

    if total_time >= timedelta(hours=2): 
        # Generate major task schedules
        python_training_end = start_datetime + timedelta(hours=2)
        gui_training_start = python_training_end + timedelta(hours=1)  # 1-hour break
        gui_training_end = gui_training_start + timedelta(hours=2)

        # Ensure the second session does not exceed the end time
        if gui_training_end > end_datetime:
            gui_training_end = end_datetime

        # Format the sessions
        python_training = f"{day}, {start_time} - {python_training_end.strftime('%H:%M')}"
        gui_training = f"{day}, {gui_training_start.strftime('%H:%M')} - {gui_training_end.strftime('%H:%M')}"
    else:
        # If the total time is less than 2 hours, use the full time for one session
        python_training = f"{day}, {start_time} - {end_time}"
        gui_training = "No additional session (insufficient time)"

    return python_training, gui_training

def generate_minor_schedule(day):
    # Schedule minor tasks on a different day than major tasks
    if day.lower() == "monday":
        minor_day = "Wednesday"
    elif day.lower() == "tuesday":
        minor_day = "Thursday"
    elif day.lower() == "wednesday":
        minor_day = "Friday"
    elif day.lower() == "thursday":
        minor_day = "Monday"
    elif day.lower() == "friday":
        minor_day = "Tuesday"
    else:
        minor_day = "Saturday"  # Default to Saturday if no match

    # Get major task times (if available)
    major_tasks = availability_data.get("major_tasks", {})

    # Generate a random start time between 9:00 AM and 5:00 PM
    random_start_hour = random.randint(9, 16)  # 9 AM to 4 PM
    random_start_minute = random.choice([0, 30])  # Start at :00 or :30
    minor_start_time = datetime.strptime(f"{random_start_hour}:{random_start_minute}", "%H:%M")

    # Ensure the end time does not exceed 5:00 PM
    minor_end_time = minor_start_time + timedelta(hours=1)
    if minor_end_time > datetime.strptime("17:00", "%H:%M"):
        minor_end_time = datetime.strptime("17:00", "%H:%M")

    # Check for conflicts with major tasks
    conflict = False
    for task, (task_start, task_end) in major_tasks.items():
        if (minor_start_time < task_end and minor_end_time > task_start):
            conflict = True
            break

    # If there's a conflict, adjust the minor task times
    if conflict:
        # Move the minor task to a different time slot
        minor_start_time = task_end + timedelta(minutes=30)  # Add a 30-minute buffer
        minor_end_time = minor_start_time + timedelta(hours=1)

    # Format the minor task schedules
    leadership_training = f"{minor_day}, {minor_start_time.strftime('%H:%M')} - {minor_end_time.strftime('%H:%M')}"
    time_management_training = f"{minor_day}, {minor_end_time.strftime('%H:%M')} - {(minor_end_time + timedelta(hours=1)).strftime('%H:%M')}"

    return leadership_training, time_management_training

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if user exists (dummy check)
        if email in users and users[email] == password:
            return redirect(url_for("availability"))
        else:
            return "Invalid email or password. Please try again."

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        # Store user data (dummy storage)
        users[email] = password
        return redirect(url_for("availability"))  # Redirect to availability page

    return render_template("registration.html")

@app.route("/availability")
def availability():
    return render_template("availability.html")

@app.route("/submit-availability", methods=["POST"])
def submit_availability():
    # Get form data
    day = request.form.get("day")
    start_time = request.form.get("start-time")
    end_time = request.form.get("end-time")

    # Store availability data (you can use a database in a real application)
    availability_data["day"] = day
    availability_data["start_time"] = start_time
    availability_data["end_time"] = end_time

    print("Stored availability data:", availability_data)
    # Redirect to main tasks page
    return redirect(url_for("maintask"))

@app.route("/maintask")
def maintask():
    # Retrieve availability data
    day = availability_data.get("day", "Not specified")
    start_time = availability_data.get("start_time", "Not specified")
    end_time = availability_data.get("end_time", "Not specified")

    # Generate AI-based schedules
    python_training, gui_training = generate_ai_schedule(day, start_time, end_time)

    print("Generated Schedules:", python_training, gui_training)
    
    return render_template(
        "maintask.html",
        python_training=python_training,
        gui_training=gui_training,
    )

@app.route("/minortask")
def minortask():
    # Retrieve availability data
    day = availability_data.get("day", "Not specified")

    # Generate AI-based schedules for minor tasks
    leadership_training, time_management_training = generate_minor_schedule(day)

    # Debug: Print the generated schedules
    print("Generated Minor Task Schedules:", leadership_training, time_management_training)

    return render_template(
        "minortask.html",
        leadership_training=leadership_training,
        time_management_training=time_management_training,
    )

@app.route("/traineereports")
def traineereports():

    print("Rendering traineereports.html")  # Debugging output
    return render_template("traineereports.html", trainees=trainees)

@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    """
    Handle feedback submission for a specific trainee.
    """
    email = request.form.get("email")
    feedback = request.form.get("feedback")

    # Store feedback in the trainee's data
    if email in trainees:
        trainees[email]["feedback"].append(feedback)

    # Debug: Print the feedback
    print(f"Feedback for {email}: {feedback}")

    # Redirect back to the trainer's report page
    return redirect(url_for("traineereports"))

@app.route("/trainermenu")
def trainermenu():
    return render_template("trainermenu.html")


if __name__ == "__main__":
    app.run(debug=True)