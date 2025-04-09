import requests
import sys
import os
from dotenv import load_dotenv

# Load API credentials from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

API_KEY = os.getenv('DICT_API')
if not API_KEY:
    print("API key not found. Please check your .env file.")
    sys.exit(1)

MW_API_URL = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/"

def get_definition(word):
    url = f"{MW_API_URL}{word.lower()}?key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("Error fetching data:", e)
        sys.exit(1)

    # Find first valid entry with a 'meta' key
    entry = None
    for item in data:
        if isinstance(item, dict) and 'meta' in item:
            entry = item
            break
    if not entry:
        print("No valid definition found.")
        sys.exit(1)

    # Print Headword and Part of Speech
    headword = entry.get("hwi", {}).get("hw", word)
    pos = entry.get("fl", "Unknown")
    print(f"Word: {headword}")
    print(f"Part of Speech: {pos}")

    # Print first Pronunciation and Audio link (if available)
    prs = entry.get("hwi", {}).get("prs", [])
    if prs:
        first_pron = prs[0].get("mw", "")
        audio = prs[0].get("sound", {}).get("audio", "")
        print(f"Pronunciation: {first_pron}")
        if audio:
            audio_url = f"https://media.merriam-webster.com/audio/prons/en/us/wav/{audio[0]}/{audio}.wav"
            print(f"Audio: {audio_url}")
    else:
        print("No pronunciation available.")

    # Extract definitions
    definitions = []
    if "def" in entry:
        for def_block in entry["def"]:
            sseq = def_block.get("sseq", [])
            for group in sseq:
                for item in group:
                    if isinstance(item, list) and len(item) > 1:
                        details = item[1]
                        # Case 1: details is a dictionary with a 'dt' key
                        if isinstance(details, dict):
                            dt_list = details.get("dt", [])
                            for dt in dt_list:
                                if isinstance(dt, list) and dt[0] == "text":
                                    definitions.append(dt[1])
                        # Case 2: details is a list; iterate through each element
                        elif isinstance(details, list):
                            for det in details:
                                if isinstance(det, dict) and "dt" in det:
                                    dt_list = det.get("dt", [])
                                    for dt in dt_list:
                                        if isinstance(dt, list) and dt[0] == "text":
                                            definitions.append(dt[1])
    
    if definitions:
        print("Definitions:")
        for i, d in enumerate(definitions, start=1):
            print(f"{i}. {d}")
    else:
        print("No definitions found.")

def main():
    if len(sys.argv) > 1:
        word = sys.argv[1]
        get_definition(word)
    else:
        print("Provide a word to define.")
        sys.exit(1)

if __name__ == "__main__":
    main()
