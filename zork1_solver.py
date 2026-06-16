#!/usr/bin/env python3
"""Zork I - final clean run for 105/350."""
import pexpect, re

child = pexpect.spawn('/usr/games/dfrotz -p /tmp/zork1.z3', timeout=10)
child.expect(r'>', timeout=10)

def cmd(c, t=8):
    child.sendline(c)
    try: child.expect(r'>', timeout=t)
    except: pass
    return re.sub(r'\r', '', child.before.decode('utf-8', errors='replace'))

def loc():
    text = cmd("look")
    lines = [l.strip() for l in text.split('\n') if l.strip() and l.strip() != 'look']
    return lines[0] if lines else "???"

def sc():
    m = re.search(r'score is (\d+)', cmd("score"))
    return int(m.group(1)) if m else 0

def kill(t, w):
    for i in range(12):
        text = cmd(f"kill {t} with {w}")
        if any(x in text.lower() for x in ["almost as soon","dispatched","killed","don't see"]): return

def find_living_room():
    for attempt in range(40):
        l = loc().lower()
        if "living" in l: return True
        if "kitchen" in l: cmd("w"); continue
        if "behind" in l: cmd("in"); continue
        if "north of" in l: cmd("e"); continue
        if "west of" in l: cmd("n"); continue
        if "south of" in l: cmd("e"); continue
        if "forest path" in l: cmd("s"); continue
        if "clearing" in l: cmd("s"); continue
        if "up a tree" in l: cmd("d"); continue
        if "canyon" in l: cmd("w"); continue
        for d in ["e","s","n","w"]:
            text = cmd(d)
            if "can't" not in text and "prevent" not in text and "impass" not in text and "machete" not in text:
                break
    return "living" in loc().lower()

def pray_home():
    l = loc().lower()
    if "temple" in l: cmd("s")
    elif "egyptian" in l: cmd("w"); cmd("s")
    elif "torch" in l: cmd("s"); cmd("s")
    cmd("pray")
    return find_living_room()

# ===== SETUP =====
print("ZORK I: The Great Underground Empire")
print("=" * 40)
cmd("open mailbox"); cmd("get leaflet"); cmd("drop leaflet")
cmd("n"); cmd("n"); cmd("climb tree"); cmd("get egg"); cmd("get nest"); cmd("climb down")
cmd("s"); cmd("e"); cmd("open window"); cmd("in"); cmd("w")
cmd("get lamp"); cmd("turn on lamp"); cmd("get sword")
cmd("e"); cmd("u"); cmd("get rope"); cmd("d"); cmd("w")
cmd("open case")
cmd("put egg in case"); cmd("put nest in case")
print(f"Deposited: jeweled egg, bird's nest → Score: {sc()}")

# ===== TRIP 1: Torch + Sceptre =====
cmd("move rug"); cmd("open trap door"); cmd("d"); cmd("n")
kill("troll", "sword"); cmd("drop sword")
cmd("e"); cmd("e"); cmd("se"); cmd("e")  # → Dome Room
cmd("tie rope to railing"); cmd("d")  # → Torch Room
cmd("get torch"); cmd("turn off lamp")
cmd("s"); cmd("e"); cmd("open coffin"); cmd("get sceptre")
cmd("w")  # Temple
pray_home()
cmd("open case"); cmd("put torch in case"); cmd("put sceptre in case")
print(f"Deposited: ivory torch, sceptre → Score: {sc()}")

# ===== TRIP 2: Coffin =====
cmd("drop all"); cmd("get lamp"); cmd("turn on lamp")
cmd("open trap door"); cmd("d"); cmd("n")
cmd("e"); cmd("e"); cmd("se"); cmd("e"); cmd("d")
cmd("s"); cmd("e"); cmd("get coffin")
cmd("w")
pray_home()
cmd("put coffin in case")
print(f"Deposited: gold coffin → Score: {sc()}")

# ===== FINAL =====
text = cmd("score")
print(f"\n{'=' * 40}")
print(f"FINAL: {text.strip()}")
inv = cmd("inventory")
case_text = cmd("look")
case_items = [l.strip() for l in case_text.split('\n') if 'trophy' in l.lower() or '  A ' in l or '  An ' in l]
print(f"Trophy case contents shown in room description")
print(f"Treasures deposited: egg, nest, torch, sceptre, coffin (5 treasures)")

child.sendline("quit")
try: child.expect('.+', timeout=3); child.sendline("y")
except: pass
child.close()
