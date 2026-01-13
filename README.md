A Django web application for recording and tracking scores from games of Yamb (a dice game). Track individual game sessions with multiple players, view player statistics, and explore high and low score leaderboards.

## Features

- **Record Games**: Log games with any number of players and their scores
- **Player Leaderboard**: View player statistics sorted by Best Score, Average Score, or Games Played
- **High Scores**: Top 10 individual scores ever recorded
- **Low Scores**: Bottom 10 individual scores ever recorded
- **Mobile Friendly**: Responsive design that works on desktop and mobile devices
- **Admin Interface**: Django admin panel for managing games, players, and scores

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Running locally

python3 -m venv venv
source venv/bin/activate
cd yamb_scores
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
