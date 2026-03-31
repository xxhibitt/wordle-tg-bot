import random

# A predefined short list of 5-letter English words
WORD_LIST = [
    "APPLE", "TRAIN", "HOUSE", "MOUSE", "SMILE", "CRANE", "SLATE",
    "TRACK", "BEACH", "GHOST", "BLAME", "PLANT", "WATER", "BOARD",
    "STONE", "HEART", "NIGHT", "LIGHT", "DREAM", "GREEN", "BLACK",
    "WORLD", "SWORD", "MAGIC", "PIZZA", "AUDIO", "VIDEO", "CHAIR"
]

def get_random_word() -> str:
    """
    Returns a random 5-letter word from the predefined list.
    """
    return random.choice(WORD_LIST).upper()

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
    """
    Generates the visual grid for the Wordle game.
    Always exactly 5 columns and 6 rows.
    """
    rows = []
    
    for guess in guesses:
        # First line: letters separated by full-width spaces, wrapped in <code>
        letters = "\u2003".join(list(guess.upper()))
        rows.append(f"<code>{letters}</code>")
        
        # Second line: emoji feedback aligned directly under the letters
        emojis = " ".join(check_word(guess, target_word))
        rows.append(emojis)
        
    # Remaining empty attempts (up to 6 total rows)
    remaining_attempts = 6 - len(guesses)
    for _ in range(remaining_attempts):
        placeholder = "\u2003".join(["_"] * 5)
        rows.append(f"<code>{placeholder}</code>")
        rows.append("⬜ ⬜ ⬜ ⬜ ⬜")
        
    return "\n".join(rows)

# Simple testing if the script is run directly
if __name__ == "__main__":
    target = "APPLE"
    print(f"Target: {target}")
    
    test_guesses = ["PAPER", "APPLY"]
    print("\n--- Grid Output ---\n")
    print(generate_grid(test_guesses, target))
