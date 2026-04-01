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
    and asks the user to choose their language.
    """
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
        ]]
    )
    await message.answer("Choose your language / Выберите язык:", reply_markup=kb)


@dp.callback_query(F.data.startswith("lang_"))
async def language_selection_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handles the language selection buttons and asks for difficulty.
    """
    await callback.answer()
    
    # Extract the language code ('ru' or 'en')
    lang_code = callback.data.split("_")[1]
    
    # Save the selected language to FSM
    await state.update_data(lang_code=lang_code)
    
    # Edit the message text and keyboard to ask for difficulty
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="🟢 Easy", callback_data="diff_easy"),
            InlineKeyboardButton(text="🟡 Medium", callback_data="diff_medium"),
            InlineKeyboardButton(text="🔴 Hard", callback_data="diff_hard")
        ]]
    )
    await callback.message.edit_text("Choose difficulty: / Выберите сложность:", reply_markup=kb)

@dp.callback_query(F.data.startswith("diff_"))
async def difficulty_selection_handler(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handles difficulty selection and starts the game.
    """
    await callback.answer()
    
    # Extract the difficulty
    diff_code = callback.data.split("_")[1]
    
    # Save difficulty to FSM and retrieve language
    await state.update_data(difficulty=diff_code)
    user_data = await state.get_data()
    lang_code = user_data.get("lang_code", "en")
    
    # Fetch the random target word
    target_word = wordle_engine.get_random_word(lang_code, diff_code)
    
    # Send the initial empty grid by editing the current message
    grid_text = wordle_engine.generate_grid([], target_word)
    await callback.message.edit_text(grid_text)
    
    # Save the target word, guesses, and message id
    await state.update_data(
        target_word=target_word, 
        guesses=[], 
        grid_message_id=callback.message.message_id
    )
    
    # Transition to the playing state
    await state.set_state(WordleGame.playing)


@dp.message(WordleGame.playing, F.text)
async def process_guess_handler(message: Message, state: FSMContext) -> None:
    """
    Catches text messages when the user is playing Wordle.
    """
    # IMMEDIATELY delete the user's message to keep the chat clean
    await message.delete()
    
    user_guess = message.text.strip().upper()
    
    # Retrieve the state data first to get the lang_code
    user_data = await state.get_data()
    lang_code = user_data.get("lang_code", "en")
    target_word = user_data["target_word"]
    guesses = user_data.get("guesses", [])
    grid_message_id = user_data["grid_message_id"]

    if len(user_guess) != 5:
        temp_msg = await message.answer("⚠️ Send exactly 5 letters")
        await asyncio.sleep(3)
        await temp_msg.delete()
        return
        
    # Validate the word against the language dictionary
    if not wordle_engine.is_valid_word(user_guess, lang_code):
        temp_msg = await message.answer("⚠️ This word is not in the dictionary! Type a real word.")
        await asyncio.sleep(3)
        await temp_msg.delete()
        return
    
    # Append guess
    guesses.append(user_guess)
    await state.update_data(guesses=guesses)
    
    # Generate the new grid string
    grid_text = wordle_engine.generate_grid(guesses, target_word)
    
    game_over = False
    
    # Check win/loss condition
    if user_guess == target_word:
        msg = "🎉 Congratulations! You guessed the word!" if lang_code == 'en' else "🎉 Поздравляем! Вы отгадали слово!"
        grid_text += f"\n\n{msg}"
        game_over = True
    elif len(guesses) >= 6:
        msg = f"Game Over! 😢 The word was {target_word}." if lang_code == 'en' else f"Игра окончена! 😢 Слово было {target_word}."
        grid_text += f"\n\n{msg}"
        game_over = True
        
    reply_markup = None
    if game_over:
        await state.clear()
        # Offer to play again by choosing a language
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
            ]]
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
