#!/usr/bin/env python3
"""Hunt the Wumpus solver v6 - fixed game loop."""
import pexpect, time, re, random

child = pexpect.spawn('/usr/games/wump', encoding='utf-8', timeout=10)

child.expect(r'y-n\)')
child.sendline("n")

won = False
total_games = 0

for game_num in range(1, 201):
    total_games = game_num
    shot_idx = 0  # cycle through tunnel indices for systematic shooting
    
    for turn in range(60):
        try:
            idx = child.expect([
                r'Move or shoot\? \(m-s\)',
                r'Care to play another game\? \(y-n\)',
                pexpect.TIMEOUT, pexpect.EOF
            ], timeout=5)
        except:
            break
        
        output = child.before or ""
        
        # Check for win
        if "slain" in output.lower() or "won the game" in output.lower():
            won = True
            print(f"\n*** WON GAME {game_num}! ***", flush=True)
            print(f"Text: {output[-400:]}", flush=True)
            break
        
        if idx == 1:
            # Game over - play again
            child.sendline("y")
            break
        
        if idx >= 2:
            break
        
        # Parse state
        room_m = re.search(r'room (\d+)', output)
        arr_m = re.search(r'(\d+) arrow', output)
        tun_m = re.search(r'tunnels? to rooms? ([\d, and]+)', output)
        
        if not room_m or not tun_m:
            break
        
        current = int(room_m.group(1))
        arrows = int(arr_m.group(1)) if arr_m else 0
        tunnels = [int(x) for x in re.findall(r'\d+', tun_m.group(1))]
        
        smell = "sniff" in output.lower()
        draft = "whoosh" in output.lower() or "draft" in output.lower()
        
        if smell and arrows > 0 and tunnels:
            # Systematic: cycle through tunnels
            target = tunnels[shot_idx % len(tunnels)]
            shot_idx += 1
            child.sendline(f"s {target}")
        elif tunnels:
            target = random.choice(tunnels)
            child.sendline(f"m {target}")
        else:
            break
    
    if won:
        break
    
    if game_num % 20 == 0:
        print(f"  {game_num} games played...", flush=True)

if won:
    # Don't play again
    try:
        child.expect(r'Care to play', timeout=3)
        child.sendline("n")
    except:
        pass
    print(f"\n=== HUNT THE WUMPUS WON IN GAME {total_games}! ===", flush=True)
else:
    print(f"\nFailed after {total_games} games.", flush=True)

child.close()
