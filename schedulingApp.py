import os
from datetime import datetime
import logging

from flask import Flask, request, render_template_string, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

load_dotenv()

app = Flask(__name__)
# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///schedules.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Set OpenAI API key

# Define a Schedule model to store past schedules
class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

# Create the database tables if they don't exist
with app.app_context():
    db.create_all()

# Modern HTML template using Bootstrap 5 for styling and new scheduling switch
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI Daily Planner</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa; }
        .container { margin-top: 2em; }
        .card { margin-bottom: 1em; }
        .header { text-align: center; margin-bottom: 2em; }
        textarea { resize: vertical; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Daily Planner</h1>
            <p class="lead">Describe your tasks, constraints, or desired schedule below and get a structured daily plan.</p>
        </div>
        <div class="row">
            <div class="col-md-6">
                <form method="post" action="{{ url_for('daily_planner') }}">
                    <div class="mb-3">
                        <label for="input_text" class="form-label">Enter your planning details:</label>
                        <textarea class="form-control" name="input_text" id="input_text" placeholder="E.g., I work from 9 to 5, have a gym session at 7pm..." required maxlength="1000"></textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Schedule Date:</label><br>
                        <div class="form-check form-check-inline">
                            <input class="form-check-input" type="radio" name="schedule_date" id="today" value="today" checked>
                            <label class="form-check-label" for="today">Today</label>
                        </div>
                        <div class="form-check form-check-inline">
                            <input class="form-check-input" type="radio" name="schedule_date" id="tomorrow" value="tomorrow">
                            <label class="form-check-label" for="tomorrow">Tomorrow</label>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary">Get My Plan</button>
                </form>
                {% if response %}
                <div class="alert alert-info mt-3" role="alert">
                    <h4 class="alert-heading">Your AI-Powered Plan:</h4>
                    <p style="white-space: pre-wrap;">{{ response }}</p>
                </div>
                {% endif %}
            </div>
            <div class="col-md-6">
                <h2>Past Schedules</h2>
                {% if schedules %}
                    {% for sched in schedules %}
                    <div class="card">
                        <div class="card-header">
                            {{ sched.created_at.strftime('%Y-%m-%d %H:%M:%S') }}
                        </div>
                        <div class="card-body">
                            <p class="card-text" style="white-space: pre-wrap;">{{ sched.content }}</p>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <p>No schedules saved yet.</p>
                {% endif %}
            </div>
        </div>
    </div>
    <!-- Bootstrap JS Bundle -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def daily_planner():
    response_text = None
    if request.method == "POST":
        user_input = request.form.get("input_text", "")
        schedule_date = request.form.get("schedule_date", "today")

        # Customize instructions based on whether the schedule is for today or tomorrow.
        if schedule_date == "today":
            # Get the current local time in a readable format.
            current_time = datetime.now().strftime("%I:%M %p")
            schedule_instructions = (f"Today is the scheduled day and the current time is {current_time}. "
                                     "Please plan a daily schedule starting from now, considering the remaining hours of the day.")
        else:
            schedule_instructions = ("The schedule is for tomorrow. Please plan a daily schedule starting from the morning (e.g., around 9:00 AM) until the evening.")

        try:
            # Generate a structured daily schedule using the new OpenAI ChatCompletion interface
            system_message = ("You are an AI daily planner. " + schedule_instructions +
                              " Provide a structured daily schedule given the user's constraints.")
            api_response = client.chat.completions.create(model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ],
            max_tokens=1000,
            temperature=0.7)
            response_text = api_response.choices[0].message.content
            # Save the generated schedule to the database
            new_schedule = Schedule(content=response_text)
            db.session.add(new_schedule)
            db.session.commit()
        except Exception as e:
            logging.error(f"Error calling OpenAI API: {e}")
            response_text = "An error occurred while generating your schedule. Please try again later."

    # Retrieve all schedules in reverse chronological order
    schedules = Schedule.query.order_by(Schedule.created_at.desc()).all()
    return render_template_string(HTML_TEMPLATE, response=response_text, schedules=schedules)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
