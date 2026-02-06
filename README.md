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

### Windows (VS Code + PowerShell)

From the repo root:

```powershell
# Create + activate a virtual environment
python -m venv venv

# If activation is blocked, run this once per terminal session:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

./venv/Scripts/Activate.ps1

# Install dependencies
python -m pip install -r requirements.txt

# Create a local .env (optional, but recommended for DEBUG=True)
Set-Content -Path ./yamb_scores/.env -Value "DEBUG=True`nSECRET_KEY=dev-secret-key"

# Run the app
cd yamb_scores
python manage.py migrate
python manage.py runserver
```

Then open http://127.0.0.1:8000/

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt

# Optional but recommended
printf "DEBUG=True\nSECRET_KEY=dev-secret-key\n" > yamb_scores/.env

cd yamb_scores
python manage.py migrate
python manage.py runserver
```
