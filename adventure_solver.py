#!/usr/bin/env python3
"""Full adventure solver - 5 treasures + dragon + rug."""
import pexpect, time, sys

child = pexpect.spawn('/usr/games/adventure', encoding='utf-8', timeout=10, maxread=65536)
time.sleep(1)

have_axe = False
score = 0

def send(cmd, retries=3):
    """Send command, handle dwarves and death dynamically."""
    global have_axe
    child.sendline(cmd)
    time.sleep(0.3)
    try:
        resp = child.read_nonblocking(16384, timeout=2).replace('\r', '')
    except:
        resp = ""
    
    # Handle death
    if 'gotten yourself killed' in resp or 'reincarnate' in resp:
        print(f"  *** DIED! ***")
        return resp
    
    # Handle dwarves - throw axe if we have it
    attempts = 0
    while 'threatening little dwarf' in resp and have_axe and attempts < 3:
        attempts += 1
        print(f"  [DWARF detected! Throwing axe... attempt {attempts}]")
        child.sendline('throw axe')
        time.sleep(0.3)
        try:
            r2 = child.read_nonblocking(16384, timeout=2).replace('\r', '')
            resp += r2
        except: pass
        # Get axe back
        child.sendline('get axe')
        time.sleep(0.3)
        try:
            r3 = child.read_nonblocking(16384, timeout=2).replace('\r', '')
            resp += r3
            if 'OK' not in r3:
                have_axe = False
                print("  [Lost axe!]")
        except: pass
    
    # Handle dwarf blocking
    if 'big knife blocks your way' in resp and have_axe:
        print(f"  [BLOCKED by dwarf! Throwing axe]")
        child.sendline('throw axe')
        time.sleep(0.3)
        try:
            r2 = child.read_nonblocking(16384, timeout=2).replace('\r', '')
            resp += r2
        except: pass
        child.sendline('get axe')
        time.sleep(0.3)
        try:
            r3 = child.read_nonblocking(16384, timeout=2).replace('\r', '')
            resp += r3
        except: pass
        # Retry original command
        child.sendline(cmd)
        time.sleep(0.3)
        try:
            r4 = child.read_nonblocking(16384, timeout=2).replace('\r', '')
            resp += r4
        except: pass
    
    return resp

# ======= WALKTHROUGH =======
# Phase 1: Setup
cmds1 = ["no", "in", "get lamp", "get keys", "out",
         "s", "s", "s", "unlock grate", "drop keys",
         "d", "w", "get cage", "on lamp",
         "w", "get rod", "w", "w",
         "drop rod", "get bird", "get rod",
         "w", "d",  # hall of mists
         "w", "wave rod", "drop rod",  # bridge fissure
         "w", "get diamonds",  # west side - diamonds
         "e",  # back to east bank
         "get axe",  # try to get axe (may not be here yet)
         "e",  # hall of mists
         "get axe",  # try again
]

print("=== PHASE 1 ===")
for cmd in cmds1:
    resp = send(cmd)
    if 'axe' in cmd and 'OK' in resp:
        have_axe = True
        print(f"  [GOT AXE!]")
    if resp.strip() and len(resp.strip()) > 5:
        short = resp.strip().split('\n')[0][:80]
        # Only print key events
        if any(k in resp for k in ['OK', 'diamonds', 'bridge', 'axe', 'bird', 'gold']):
            print(f"  {cmd} -> {short}")

# Get gold
print("\n=== GET GOLD ===")
resp = send("s")
print(f"  s -> {resp.strip().split(chr(10))[0][:80]}")
resp = send("get gold")
print(f"  get gold -> {resp.strip()[:40]}")
resp = send("n")

# Hall of Mt King - bird vs snake
print("\n=== SNAKE + TREASURES ===")
resp = send("d")
resp = send("drop bird")
print(f"  drop bird -> {resp.strip().split(chr(10))[0][:80]}")
resp = send("drop cage")

# Get jewelry
resp = send("s")
resp = send("get jewelry")
print(f"  get jewelry -> {resp.strip()[:40]}")
resp = send("n")

# Get coins
resp = send("w")
resp = send("get coins")
print(f"  get coins -> {resp.strip()[:40]}")
resp = send("e")

# Get silver
resp = send("n")
resp = send("get silver")
print(f"  get silver -> {resp.strip()[:40]}")

# Deposit at building
print("\n=== DEPOSIT TRIP 1 ===")
resp = send("n")  # Y2
resp = send("plugh")  # building
for t in ["diamonds", "gold", "jewelry", "coins", "silver"]:
    resp = send(f"drop {t}")
    print(f"  drop {t} -> {resp.strip()[:30]}")

resp = send("score")
print(f"\n  SCORE: {resp.strip()[:120]}")
resp = send("no")

# Trip 2: Kill dragon, get rug
print("\n=== TRIP 2: DRAGON ===")
resp = send("plugh")  # Y2
resp = send("s")  # low passage
resp = send("s")  # hall of mt king

# SW to secret canyon, then W to dragon
resp = send("sw")
print(f"  sw -> {resp.strip().split(chr(10))[0][:80]}")
resp = send("w")
print(f"  w -> {resp.strip().split(chr(10))[0][:80]}")

# Kill dragon
resp = send("kill dragon")
print(f"  kill dragon -> {resp.strip()[:80]}")
resp = send("yes")
print(f"  yes -> {resp.strip()[:120]}")

# Look and get rug
resp = send("look")
print(f"  look -> {resp.strip()[:120]}")
resp = send("get rug")
print(f"  get rug -> {resp.strip()[:40]}")

# Return to building
resp = send("e")  # secret e/w canyon
resp = send("e")  # hall of mt king (or ne?)
print(f"  e -> {resp.strip().split(chr(10))[0][:80]}")
resp = send("n")
print(f"  n -> {resp.strip().split(chr(10))[0][:80]}")
resp = send("n")
print(f"  n -> {resp.strip().split(chr(10))[0][:80]}")
resp = send("plugh")
print(f"  plugh -> {resp.strip().split(chr(10))[0][:80]}")
resp = send("drop rug")
print(f"  drop rug -> {resp.strip()[:40]}")

# Final score
resp = send("score")
print(f"\n  FINAL SCORE: {resp.strip()[:200]}")
resp = send("no")
resp = send("quit")
resp = send("yes")
print(f"\n  {resp.strip()[:200]}")

child.close()
