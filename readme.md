
# Two-Player Trivia Duel

A solution for trivia game, two users can connect to game and select among the quiz categories to compete.

## Table of Contents

- [Features](#features)  
- [Requirements](#requirements)  
- [Installation and Setup](#installation-and-setup)  
- [Running the Application](#running-the-application)  
  - [With Docker Compose](#with-docker-compose)  
  - [Running Locally Without Docker](#running-locally-without-docker)  
- [API Endpoints](#api-endpoints)  
- [Testing](#testing)  
- [Contributing](#contributing)  
- [License](#license)  

---

## Features

- **Two-player real-time trivia duel** with matchmaking  
- **5 rounds**, alternating which player chooses the category  
- **Category selection**: chooser picks from 3 random unused categories  
- **Timed questions**: 5 questions per round, 10 seconds each  
- **Round and match summary** with per-round and total scores  
- **Admin interface** for managing categories, questions, and choices  
- **Seed command** to bootstrap 6 categories × 5 dummy questions each  
- **User authentication** (sign up, log in/out) via Django auth  

---

## Requirements

- Python 3.10+  
- Django 4.x  
- SQLite (default) or PostgreSQL/MySQL (optional)  
- Git 

---

## Installation and Setup

1. **Clone the repository**  
   ```bash
   git clone https://github.com/Amirreza-Jabbari/trivia-duel.git
   cd trivia-duel
   ```

2. **Create & activate a virtual environment**  
   ```bash
   python -m venv venv
   source venv/bin/activate      # Linux/macOS
   venv\Scripts\activate         # Windows PowerShell
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations & seed data**  
   ```bash
   python manage.py migrate
   python manage.py seed_questions
   ```

---

## Running the Application

### Running Locally Without Docker

```bash
python manage.py runserver
```

Then open your browser to `http://127.0.0.1:8000/`.

---

## API Endpoints

This app uses Django’s view-based URLs—no REST API by default. Available endpoints:

| URL                                            | View                      | Description                          |
|------------------------------------------------|---------------------------|--------------------------------------|
| `/`                                            | `HomeView`                | Landing page                         |
| `/signup/`                                     | `signup`                  | User registration                   |
| `/accounts/login/`                             | Django auth login         | User login                          |
| `/play/`                                       | `join_match`              | Join or create a match              |
| `/status/`                                     | `match_status`            | Waiting or redirect to match start  |
| `/match/<match_id>/start/`                     | `start_round`             | Category pick or redirect to play   |
| `/round/<round_id>/<user_phase>/play/`         | `play_round`              | Answer questions (`self` or `opponent`) |
| `/round/<round_id>/<phase>/waiting/`           | `waiting_phase`           | Polling screen while waiting        |
| `/round/<round_id>/complete/`                  | `round_complete`          | Round results                       |
| `/match/<match_id>/complete/`                  | `match_complete`          | Final match summary                 |

---

## Testing

Run Django’s test suite:

```bash
python manage.py test
```

---

## Contributing

Contributions are welcome! Please submit pull requests or open issues on GitHub. Make sure to update tests and documentation accordingly.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
