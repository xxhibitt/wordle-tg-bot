import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup
from dotenv import load_dotenv

import wordle_engine

# Load environment variables from .env file
load_dotenv()

# Retrieve the bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Basic validation
if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
    print("Error: BOT_TOKEN is not set. Please update your .env file.", file=sys.stderr)
    sys.exit(1)

# Initialize Dispatcher
dp = Dispatcher()

# Define the FSM state group
class WordleGame(StatesGroup):
    waiting_for_guess = State()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with the `/start` command
    and displays the Play Wordle reply keyboard.
    """
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Play Wordle")]],
        resize_keyboard=True
    )
    await message.answer("Welcome to Wordle Bot!", reply_markup=kb)


@dp.message(F.text == "Play Wordle")
async def play_wordle_handler(message: Message, state: FSMContext) -> None:
    """
    Handles the 'Play Wordle' button press.
    """
    target_word = wordle_engine.get_random_word()
    
    # Save the target word and initialize attempts counter
    await state.update_data(target_word=target_word, attempts=0)
    
    # Set the state to waiting_for_guess
    await state.set_state(WordleGame.waiting_for_guess)
    
    await message.answer("I have chosen a 5-letter word. Send me your first guess!")


@dp.message(WordleGame.waiting_for_guess, F.text)
async def process_guess_handler(message: Message, state: FSMContext) -> None:
    """
    Catches text messages only when the user is in the waiting_for_guess state.
    """
    user_guess = message.text.upper()
    
    if len(user_guess) != 5:
        await message.answer("Please enter exactly 5 letters.")
        return
    
    # Retrieve the state data
    user_data = await state.get_data()
    target_word = user_data["target_word"]
    attempts = user_data.get("attempts", 0)
    
    # Increment attempts and update state
    attempts += 1
    await state.update_data(attempts=attempts)
    
    # Check the guess
    result_emojis = wordle_engine.check_guess(target_word, user_guess)
    
    # Prepare the response
    response = f"Your guess: {user_guess}\nResult: {result_emojis}\nAttempts: {attempts}/6"
    
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Play Wordle")]],
        resize_keyboard=True
    )
    
    if result_emojis == "🟩🟩🟩🟩🟩":
        response += "\n\n🎉 Congratulations! You guessed the word!\nPlay again?"
        await state.clear()
        await message.answer(response, reply_markup=kb)
    elif attempts >= 6:
        response += f"\n\nGame Over! 😢 The word was {target_word}.\nPlay again?"
        await state.clear()
        await message.answer(response, reply_markup=kb)
    else:
        response += "\n\nSend me your next guess!"
        await message.answer(response)


async def main() -> None:
    # Initialize Bot instance with default properties
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    # Start polling
    logging.info("Starting bot polling...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Setup basic logging
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped!")
