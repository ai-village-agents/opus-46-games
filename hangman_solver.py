#!/usr/bin/env python3
"""Hangman solver - uses letter frequency to guess words."""
import pexpect, time, re, string

child = pexpect.spawn('/usr/games/hangman', encoding='utf-8', timeout=10, 
                      dimensions=(24, 80))
time.sleep(1)

# Letter frequency order
freq_order = "etaoinshrdlcumwfgypbvkjxqz"

won = False
max_wrong = 9  # typical hangman allows ~9 wrong guesses

for attempt in range(5):  # try up to 5 words
    # Read initial state
    try:
        data = child.read_nonblocking(8192, timeout=2)
    except:
        data = ""
    
    print(f"\n--- Word {attempt+1} ---", flush=True)
    guessed = set()
    
    for guess_num in range(26):
        # Pick next letter from frequency order
        letter = None
        for l in freq_order:
            if l not in guessed:
                letter = l
                break
        
        if not letter:
            break
        
        guessed.add(letter)
        child.sendline(letter)
        time.sleep(0.5)
        
        try:
            data = child.read_nonblocking(8192, timeout=2)
        except:
            data = ""
        
        clean = data.replace('\r', '').replace('\x1b[H\x1b[J', '')
        
        # Check for "You got it" or "Another word"
        if "got it" in data.lower() or "you win" in data.lower():
            print(f"  SOLVED after {guess_num+1} guesses!", flush=True)
            won = True
            # Answer "Another word?" with n
            time.sleep(0.5)
            child.sendline("n")
            time.sleep(0.5)
            break
        
        if "you lose" in data.lower() or "the word was" in data.lower():
            print(f"  LOST after {guess_num+1} guesses.", flush=True)
            # Try another word - answer y
            time.sleep(0.5)
            child.sendline("y")
            time.sleep(0.5)
            break
        
        # Check if we see the pattern
        pattern_match = re.search(r'Guess:\s*([a-z])', data)
        word_match = re.findall(r'[_a-z]+', data.lower())
        
        if guess_num < 3:
            print(f"  Guessed '{letter}'", flush=True)
    
    if won:
        break

try:
    remaining = child.read_nonblocking(8192, timeout=2)
    print(f"Final output: {remaining[:200]}", flush=True)
except:
    pass

child.close()

if won:
    print(f"\n=== HANGMAN WON! ===", flush=True)
else:
    print(f"\nDid not win.", flush=True)
