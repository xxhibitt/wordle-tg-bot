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

def check_guess(target_word: str, user_guess: str) -> str:
    """
    Compares a 5-letter guess to the target word and returns a string of 5 emojis.
    🟩: Correct letter and position
    🟨: Correct letter, wrong position
    ⬛: Incorrect letter
    """
    target = list(target_word.upper())
    guess = list(user_guess.upper())
    
    # Ensure we only check up to 5 letters
    length = min(len(target), len(guess), 5)
    result = ["⬛"] * length
    
    # First pass: Check for correct letters in the correct positions (Green squares)
    for i in range(length):
        if guess[i] == target[i]:
            result[i] = "🟩"
            target[i] = None  # Mark this letter in target as used
            guess[i] = None   # Mark this letter in guess as matched so we skip it later

    # Second pass: Check for correct letters in wrong positions (Yellow squares)
    for i in range(length):
        if guess[i] is not None:
            if guess[i] in target:
                result[i] = "🟨"
                # Remove the found letter from target so it can't be matched again
                target[target.index(guess[i])] = None 

    return "".join(result)

# Simple testing if the script is run directly
if __name__ == "__main__":
    target = "APPLE"
    print(f"Target: {target}")
    
    test_guesses = ["PAPER", "APPLY", "PUPIL", "HELLO", "PLEAD"]
    for g in test_guesses:
        print(f"Guess: {g} -> {check_guess(target, g)}")
