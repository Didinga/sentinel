# Sentinel

A Python-based security camera system with motion detection, face detection, and Telegram alerts.

## Features

- Motion detection using background subtraction (MOG2)
- Face detection using Haar cascade classifier
- State machine logic: IDLE → INVESTIGATE → ALERT
- Automatic snapshot saved on alert
- Telegram notification with photo
- Audio alarm on alert
- Credentials loaded securely from `.env`

## How It Works
IDLE → motion detected → INVESTIGATE → face detected → ALERT
↓                              ↓
no motion for 3s              no face for 5s
↓                              ↓
IDLE                          IDLE

## Requirements

- Python 3.x
- Webcam
- Linux (for audio alarm via `aplay`)
- Telegram bot ([create one via BotFather](https://t.me/BotFather))

## Installation

```bash
git clone https://github.com/Didinga/sentinel.git
cd sentinel
pip install opencv-python python-telegram-bot python-dotenv
```

## Configuration

1. Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

2. Fill in your credentials:

```bash
TELEGRAM_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

## Usage

```bash
python sentinel.py
```

Press `q` to quit.

## Project Structure
sentinel/
├── sentinel.py
├── .env.example
├── .gitignore
├── screenshots/
│   └── demo.png
└── snapshots/        # auto-created, gitignored

## Screenshot

![Sentinel in action](screenshots/demo.png)

## Notes

- Snapshots are saved to the `snapshots/` folder and excluded from Git
- Alert cooldown is set to 5 seconds to avoid spam
- Tested on Linux; audio alarm may not work on Windows/macOS without modification
