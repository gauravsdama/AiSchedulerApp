# AI Daily Planner

The **AI Daily Planner** is a Flask-based scheduling application that uses OpenAI's GPT model to generate personalized daily schedules. The app offers two scheduling modes—one that plans from the current time for "Today" and another that generates a full-day schedule for "Tomorrow". All generated schedules are stored in a local SQLite database and displayed using a modern Bootstrap-based UI.

## Features

- **Dynamic Scheduling:**  
  Choose between generating a schedule starting from the current time ("Today") or a full schedule for the next day ("Tomorrow").

- **AI-Powered Plan Generation:**  
  Uses OpenAI's GPT-3.5-turbo model to create a structured and personalized schedule based on your input.

- **Local Persistence:**  
  Schedules are saved in a SQLite database and displayed as cards on the web interface.

- **Modern UI:**  
  Built with Bootstrap 5 for a clean and responsive design.

## Prerequisites

- Python 3.8+
- [Flask](https://flask.palletsprojects.com/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [OpenAI Python package](https://pypi.org/project/openai/)

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
