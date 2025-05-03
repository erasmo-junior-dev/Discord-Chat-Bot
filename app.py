"""
This script implements a Discord bot integrated with Google Gemini AI and a database for storing user interactions.

Modules:
- discord: Used for interacting with the Discord API.
- os: Provides functions to interact with the operating system.
- dotenv: Loads environment variables from a .env file.
- sqlalchemy: ORM for database interaction.
- google.genai: Google Gemini AI client for generating responses.
- asyncio: Provides support for asynchronous programming.

Classes:
- User: Represents a user in the database.
- ChatHistory: Represents the chat history of a user in the database.

Functions:
- interact_message(message): Handles user messages, interacts with Google Gemini AI, and stores/retrieves chat history in the database.

Events:
- on_ready(): Triggered when the bot is ready and connected to Discord.
- on_message(message): Triggered when a message is sent in a Discord channel. Handles bot replies and interactions.

Environment Variables:
- DISCORD_API_KEY: API key for the Discord bot.
- DATABASE_URL: URL for the database connection.
- GEMINI_API_KEY: API key for Google Gemini AI.

Database:
- Users table: Stores user IDs and usernames.
- ChatHistory table: Stores user messages, bot replies, and associated metadata.

Features:
- Automatically creates database tables if they do not exist.
- Tracks user chat history and limits the number of stored messages per user.
- Integrates with Google Gemini AI to generate responses based on user input and chat history.
- Responds to messages that mention the bot or reply to the bot's messages.

Usage:
- Ensure the .env file is properly configured with the required API keys and database URL.
- Run the script to start the bot.
"""

import discord
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, ForeignKey, Text, exists, BigInteger
from sqlalchemy.orm import sessionmaker, declarative_base
from google import genai
from google.genai import types
import asyncio

# Default bot configuration
intents = discord.Intents.default()
intents.message_content = True

client_discord = discord.Client(intents=intents)

# Loading bot API key
load_dotenv()
BOT_API_KEY = os.getenv("DISCORD_API_KEY")

if BOT_API_KEY is None or BOT_API_KEY == "":
    raise ValueError("API key not found. Check if the .env file is configured correctly.")

# Defining the database model
Base = declarative_base()

class User(Base):  # Users table
    __tablename__ = 'users'

    id = Column("id", BigInteger, primary_key=True, autoincrement=False)
    username = Column("username", String(32))

    def __init__(self, id, username):
        self.id = id
        self.username = username
    
class ChatHistory(Base):  # Chat history table
    __tablename__ = 'chat_history'

    id = Column("id", BigInteger, primary_key=True, autoincrement=False)
    user_id = Column("user_id", ForeignKey("users.id"))
    channel_id = Column("channel_id", BigInteger)
    user_message = Column('user_message',Text)
    bot_reply = Column('bot_reply',Text)

    def __init__(self, id, user_id, channel_id, user_message, bot_reply):
        self.id = id
        self.user_id = user_id
        self.channel_id = channel_id
        self.user_message = user_message
        self.bot_reply = bot_reply

# Connecting to the database
DB_URL = os.getenv("DATABASE_URL")

if DB_URL is None or DB_URL == "":
    raise ValueError("Database URL not found. Check if the .env file is configured correctly.")

db = create_engine(DB_URL)
Session = sessionmaker(bind=db)
session = Session()

# Creating tables if they do not exist
Base.metadata.create_all(db)

# Configuring the Google Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY is None or GEMINI_API_KEY == "":
    raise ValueError("Google Gemini API key not found. Check if the .env file is configured correctly.")

client_ai = genai.Client(api_key=GEMINI_API_KEY)

system_prompt = 'System Prompt'

chat = client_ai.chats.create(
    model="Gemini-Model",
    config=types.GenerateContentConfig(
        system_instruction=system_prompt
    )
)

async def interact_message(message):
    user = message.author.id
    channel = message.channel.id
    display_name = message.author.display_name
    max_messages_user_history = 5

    # If the user is not in the database, add them
    if not session.query(exists().where(User.id == user)).scalar():
        session.add(User(id=user, username=display_name))
        session.commit()
    
    # Retrieve previous messages for context
    history_messages = session.query(ChatHistory.user_message, ChatHistory.bot_reply).filter(ChatHistory.user_id == user, ChatHistory.channel_id == channel).all()

    if history_messages:
        chat.send_message(f"User {display_name} history:" )
        for user_message, bot_reply in history_messages:
            chat.send_message(f"User message: {user_message}\nYour reply: {bot_reply}")
            waiting_time_prompt_history = 2
            await asyncio.sleep(waiting_time_prompt_history)
    
    # Send current message to the model
    response = chat.send_message(f"Actual message of {display_name}:\n" + message.content)
    await message.reply(response.text)

    # Save interaction in the database
    session.add(ChatHistory(id=message.id, user_id=user, channel_id=channel, user_message=message.content, bot_reply=response.text))
    session.commit()

    # Limit message history per user
    if session.query(ChatHistory).filter(ChatHistory.user_id == user, ChatHistory.channel_id == channel).count() > max_messages_user_history:
        old_message = session.query(ChatHistory).filter(
            ChatHistory.user_id == user,
            ChatHistory.channel_id == channel
        ).order_by(ChatHistory.id.asc()).first()

        if old_message:
            session.delete(old_message)
            session.commit()

@client_discord.event
async def on_ready():
    print("Online!")

@client_discord.event
async def on_message(message):
    if message.author.bot:  # Ignore messages from bots
        return

    # If the message is a reply to the bot
    if message.reference:
        original = await message.channel.fetch_message(message.reference.message_id)
        if original.author == client_discord.user:
            await interact_message(message)
    # If the bot is mentioned
    elif client_discord.user in message.mentions:
        await interact_message(message)

client_discord.run(BOT_API_KEY)