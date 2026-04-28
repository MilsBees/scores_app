A Django web application for recording and tracking scores from multiple games. Track Yamb dice game sessions and Squash match results with player statistics, leaderboards, and detailed performance analytics.

## Features

### Yamb (Dice Game)
- **Record Games**: Log Yamb games with any number of players and automatic score calculations
- **Scoresheet Tracking**: Comprehensive scoresheets with automatic row and column totals
- **Player Leaderboard**: View player statistics sorted by Best Score, Average Score, or Games Played
- **High/Low Scores**: Top 10 and Bottom 10 individual scores ever recorded
- **Game History**: Browse recent games with detailed score breakdowns

### Squash (Racquet Sport)
- **Match Recording**: Log matches between two players with set-by-set results
- **Session Management**: Group multiple matches from a single play session
- **Player Leaderboard**: Relative and absolute player rankings with match/set/point statistics
- **Head-to-Head Analysis**: View detailed records between specific player pairings
- **Performance Analysis**: Historical performance trends with customizable date ranges and visualizations
- **Player Management**: Add and manage squash players

### General
- **Unified Dashboard**: Home page with links to all available sports/games
- **Mobile Friendly**: Responsive design that works on desktop and mobile devices
- **Admin Interface**: Django admin panel for managing all data
- **Consistent UI**: Shared template structure across all applications

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

## Way of Working

- See the backlog folder for a list of open work items
- If you have other ideas, feel free to add them to the backlog
- Create a merge request for whatever you have added
- If you notice something missing in this file to get it working locally, please update the readme accordingly!