import random

def load_words(language_code: str, difficulty: str) -> list[str]:
    """
    Reads the specific difficulty file (e.g. en_easy.txt) and returns a list of words.
    """
    filename = f"{language_code}_{difficulty}.txt"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip().upper() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Warning: dictionary {filename} not found.")
        return []

def get_random_word(language_code: str, difficulty: str = "easy") -> str:
    """
    Uses load_words to pick a random target word for the given language and difficulty.
    """
    words = load_words(language_code, difficulty)
    if not words:
        # Fallback in case dictionary is missing
        return "APPLE" if language_code == 'en' else "СЛОВО"
    return random.choice(words).upper()

# Cache for master word lists to prevent reloading files on every guess
_master_words_cache = {}

def get_master_word_list(language_code: str) -> set[str]:
    """
    Loads all words from easy, medium, and hard files for a language into a single set.
    """
    if language_code in _master_words_cache:
        return _master_words_cache[language_code]
        
    master_set = set()
    for diff in ["easy", "medium", "hard"]:
        master_set.update(load_words(language_code, diff))
        
    _master_words_cache[language_code] = master_set
    return master_set

def is_valid_word(guess: str, language_code: str) -> bool:
    """
    Checks if the user's guess exists in ANY of the difficulty dictionaries for that language.
    """
    master_set = get_master_word_list(language_code)
    return guess.upper() in master_set

def check_word(guess: str, target_word: str) -> list[str]:
    """
    Compares a 5-letter guess to the target word and returns a list of 5 emojis.
    🟩: Correct letter and position
    🟨: Correct letter, wrong position
    ⬛: Incorrect letter
    """
    target = list(target_word.upper())
    guess_list = list(guess.upper())
    
    # Ensure we only check up to 5 letters
    length = min(len(target), len(guess_list), 5)
    result = ["⬛"] * length
    
    # First pass: Check for correct letters in the correct positions (Green squares)
    for i in range(length):
        if guess_list[i] == target[i]:
            result[i] = "🟩"
            target[i] = None  # Mark this letter in target as used
            guess_list[i] = None   # Mark this letter in guess as matched so we skip it later

    # Second pass: Check for correct letters in wrong positions (Yellow squares)
    for i in range(length):
        if guess_list[i] is not None:
            if guess_list[i] in target:
                result[i] = "🟨"
                # Remove the found letter from target so it can't be matched again
                target[target.index(guess_list[i])] = None 

    return result

def generate_grid(guesses: list, target_word: str) -> str:
    # Используем \u2003 (Em Space) - он визуально равен ширине эмодзи
    wide_space = "\u2003" 
    grid_lines = []
    
    # Отрисовываем уже введенные слова
    for guess in guesses:
        # Разбиваем слово на буквы и вставляем широкие пробелы
        spaced_letters = wide_space.join(list(guess.upper()))
        # Оборачиваем в моноширинный тег
        grid_lines.append(f"<code>{spaced_letters}</code>")
        
        # Получаем эмодзи и склеиваем их без пробелов (они и так широкие)
        emojis = check_word(guess, target_word) 
        grid_lines.append("".join(emojis))
        
    # Добиваем пустые строки (всего должно быть 6 попыток)
    remaining_attempts = 6 - len(guesses)
    for _ in range(remaining_attempts):
        spaced_underscores = wide_space.join(["_"] * 5)
        grid_lines.append(f"<code>{spaced_underscores}</code>")
        grid_lines.append("⬜⬜⬜⬜⬜")
        
    return "\n".join(grid_lines)

# Simple testing if the script is run directly
if __name__ == "__main__":
    target = "APPLE"
    print(f"Target: {target}")
    
    test_guesses = ["PAPER", "APPLY"]
    print("\n--- Grid Output ---\n")
    print(generate_grid(test_guesses, target))
