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
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
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
    playing = State()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with the `/start` command
    and displays the Play Wordle inline keyboard.
    """
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Play Wordle", callback_data="play_wordle")]]
    )
    await message.answer("Welcome to Wordle Bot!", reply_markup=kb)


@dp.callback_query(F.data == "play_wordle")
async def play_wordle_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handles the 'Play Wordle' button press.
    """
    await callback.answer()
    
    target_word = wordle_engine.get_random_word()
    
    # Send the initial empty grid
    grid_text = wordle_engine.generate_grid([], target_word)
    sent_msg = await callback.message.answer(grid_text)
    
    # Save the target word, empty guesses list, and the grid message id
    await state.update_data(target_word=target_word, guesses=[], grid_message_id=sent_msg.message_id)
    
    # Set the state to playing
    await state.set_state(WordleGame.playing)


@dp.message(WordleGame.playing, F.text)
async def process_guess_handler(message: Message, state: FSMContext) -> None:
    """
    Catches text messages when the user is playing Wordle.
    """
    # IMMEDIATELY delete the user's message to keep the chat clean
    await message.delete()
    
    user_guess = message.text.strip().upper()
    
    if len(user_guess) != 5 or not user_guess.isalpha():
        temp_msg = await message.answer("⚠️ Send a 5-letter word")
        await asyncio.sleep(3)
        await temp_msg.delete()
        return
    
    # Retrieve the state data
    user_data = await state.get_data()
    target_word = user_data["target_word"]
    guesses = user_data.get("guesses", [])
    grid_message_id = user_data["grid_message_id"]
    
    # Append guess
    guesses.append(user_guess)
    await state.update_data(guesses=guesses)
    
    # Generate the new grid string
    grid_text = wordle_engine.generate_grid(guesses, target_word)
    
    game_over = False
    
    # Check win/loss condition
    if user_guess == target_word:
        grid_text += "\n\n🎉 Congratulations! You guessed the word!"
        game_over = True
    elif len(guesses) >= 6:
        grid_text += f"\n\nGame Over! 😢 The word was {target_word}."
        game_over = True
        
    reply_markup = None
    if game_over:
        await state.clear()
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Play Again", callback_data="play_wordle")]]
        )
        
    # Edit the original grid message
    await message.bot.edit_message_text(
        text=grid_text,
        chat_id=message.chat.id,
        message_id=grid_message_id,
        reply_markup=reply_markup
    )


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
