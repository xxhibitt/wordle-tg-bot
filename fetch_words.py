import requests
from wordfreq import zipf_frequency

def fetch_and_process_words(url, lang_code, is_russian=False):
    print(f"Fetching {lang_code.upper()} words from {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        words = set()
        for line in response.text.splitlines():
            word = line.strip().lower()
            
            # Check length and ensure it contains only letters
            if len(word) == 5 and word.isalpha():
                if is_russian:
                    # Cyrillic check
                    if all('\u0400' <= char <= '\u04FF' or char == 'ё' for char in word):
                        words.add(word)
                else:
                    # ASCII check
                    if all(ord(char) < 128 for char in word):
                        words.add(word)
        
        word_list = list(words)
        print(f"  Valid 5-letter words found: {len(word_list)}")
        
        # Get frequency for each word
        # The zipf_frequency returns a float (logarithmic scale, higher is more common)
        # Unrecognized words return 0.0
        scored_words = []
        for word in word_list:
            freq = zipf_frequency(word, lang_code)
            scored_words.append((word, freq))
            
        # Sort by frequency descending. 
        # Secondary sort by word alphabetically to ensure consistent splits on ties (0.0 freq)
        scored_words.sort(key=lambda x: (-x[1], x[0]))
        
        # Calculate split indices for 15% / 35% / 50%
        total = len(scored_words)
        idx_easy = int(total * 0.15)
        idx_medium = idx_easy + int(total * 0.35)
        
        # Slice the lists (extracting just the words, discarding the scores)
        easy_words = [w[0] for w in scored_words[:idx_easy]]
        medium_words = [w[0] for w in scored_words[idx_easy:idx_medium]]
        hard_words = [w[0] for w in scored_words[idx_medium:]]
        
        # Save files
        save_list(easy_words, f"{lang_code}_easy.txt")
        save_list(medium_words, f"{lang_code}_medium.txt")
        save_list(hard_words, f"{lang_code}_hard.txt")
        
        print(f"  Saved {lang_code}_easy.txt ({len(easy_words)} words)")
        print(f"  Saved {lang_code}_medium.txt ({len(medium_words)} words)")
        print(f"  Saved {lang_code}_hard.txt ({len(hard_words)} words)\n")
        
    except requests.RequestException as e:
        print(f"Failed to fetch data for {lang_code}: {e}")
    except Exception as e:
        print(f"An error occurred while processing {lang_code}: {e}")

def save_list(word_list, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        # Keeping them sorted by frequency within the file
        for word in word_list:
            f.write(f"{word}\n")

if __name__ == "__main__":
    ENG_URL = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
    RU_URL = "https://raw.githubusercontent.com/danakt/russian-words/master/russian.txt"
    
    print("Starting word fetch and frequency analysis process...\n")
    fetch_and_process_words(ENG_URL, 'en', is_russian=False)
    fetch_and_process_words(RU_URL, 'ru', is_russian=True)
    print("Done. You can now use these categorized files in your game.")
