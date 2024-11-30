import asyncio
import logging
import sys
from os import getenv
import openai
from dotenv import load_dotenv
import os

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message


class Reference:
    """
    A class to store previous responses from the chatGPT API.
    """

    def __init__(self) -> None:
        self.response = ""


# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OpenAI_API_KEY")

reference = Reference()

TOKEN = os.getenv("TOKEN")

# Model name
MODEL_NAME = "gpt-3.5-turbo"

# Initialize Dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()


def clear_past():
    """A function to clear the previous conversation and context."""
    reference.response = ""


@dp.message(CommandStart())
async def welcome(message: Message):
    """
    This handler receives messages with `/start` command.
    """
    await message.reply("Hi\nI am Tele Bot!\nCreated by Prashanth. How can I assist you?")


@dp.message(Command("clear"))
async def clear(message: Message):
    """
    A handler to clear the previous conversation and context.
    """
    clear_past()
    await message.reply("I've cleared the past conversation and context.")


@dp.message(Command("help"))
async def helper(message: Message):
    """
    A handler to display the help menu.
    """
    help_command = """
    Hi There, I'm chatGPT Telegram bot created by prashanth! Please follow these commands -
    /start - to start the conversation
    /clear - to clear the past conversation and context.
    /help - to get this help menu.
    I hope this helps. :)
    """
    await message.reply(help_command)


@dp.message()
async def chatgpt(message: Message):
    """
    A handler to process the user's input and generate a response using the chatGPT API.
    """
    print(f">>> USER: \n\t{message.text}")
    try:
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[
                {"role": "assistant", "content": reference.response},  # Role: assistant
                {"role": "user", "content": message.text},  # User query
            ],
        )
        reference.response = response['choices'][0]['message']['content']
        print(f">>> chatGPT: \n\t{reference.response}")
        await bot.send_message(chat_id=message.chat.id, text=reference.response)
    except Exception as e:
        logging.error(f"Error with OpenAI API: {e}")
        await message.reply("Sorry, I couldn't process your request. Please try again later.")


async def main():
    """
    Main function to initialize and start the bot.
    """
    # Initialize Bot instance
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Run the bot
    asyncio.run(main())
