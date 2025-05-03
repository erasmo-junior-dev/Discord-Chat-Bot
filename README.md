# Gemini Discord Bot 🤖✨

A Discord bot that integrates with **Google Gemini AI** to respond to user messages and stores chat history using **SQLAlchemy**.

---

⚠️ **Disclaimer:**  
All comments and explanatory texts were translated and formatted by an AI (ChatGPT), but the entire source code was written and developed by **Erasmo da Silva Sá Junior**.

---

## 🚀 Features

- Responds to mentions or replies in Discord.
- Integrates with Google Gemini for AI-based responses.
- Stores user and message history in a database.
- Automatically prunes older messages to keep the history clean.
- Ignores bot messages.
- Uses `.env` file for secure API key and DB config.

## 🧠 Tech Stack

- [Python](https://www.python.org/)
- [Discord.py](https://discordpy.readthedocs.io/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Google Gemini AI](https://ai.google.dev/)
- [dotenv](https://pypi.org/project/python-dotenv/)

## 📦 Requirements

Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

## ⚙️ Environment Setup

- Create a .env file in the root directory with the following variables:
```env
DISCORD_API_KEY=your_discord_bot_token
DATABASE_URL=sqlite:///gemini_bot.db  # Or use your own DB engine
GEMINI_API_KEY=your_google_gemini_key
```
## 🏁 How to Run

```bash
python app.py
```

- Make sure to replace main.py with your actual filename.

## 📜 License

- This project is licensed under the MIT License.

> Developed with dedication by Erasmo da Silva Sá Junior.
