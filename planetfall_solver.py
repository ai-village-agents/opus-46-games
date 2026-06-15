import pexpect, time, re, sys

GAME = "/tmp/planetfall.z3"
child = pexpect.spawn(f'/usr/games/dfrotz -p -m -s 1 -w 80 -h 200 {GAME}', encoding=None, timeout=10)
time.sleep(1)
try: child.expect([r'>', pexpect.TIMEOUT], timeout=5)
except: pass

def send(cmd, w=0.3):
    child.sendline(cmd)
    time.sleep(w)
    try: child.expect([r'>', pexpect.TIMEOUT], timeout=3)
    except: pass
    return child.before.decode('latin-1', errors='replace') if child.before else ""

def batch(cmds, w=0.3):
    for c in cmds:
        r = send(c, w)
        if "You have died" in r:
            print(f"DIED after: {c}\n{r[-300:]}")
            return False
    return True

# === PHASES 1-6 ===
batch(["wait"]*8+["w","get into webbing"]+["wait"]*12+["get out of webbing","take all","open door","u","u","u","u","u"])
cmds="n.ne.e.e.take id card.drop all except kit.e.s.s.s.sw.take all.drop battery.ne.n.n.n.n.put bar over crevice.s.e.drop all except key.press blue button.press red button.w.w.w.unlock padlock with key.take padlock.open door.n.drop key and padlock.take ladder.s.e.e.n.n.drop ladder.extend ladder.put ladder over rift.n.w.open desk.put kitchen card and upper card into pocket.w.open desk.put shuttle card into pocket.e.e.s.s.s.e.take kit and flask.open kit.eat red goo.w.s.s.s.se.open robot.close robot.turn on robot.nw.n.n.e.take bedistor.w.n.e.n".split(".")
batch([c.strip() for c in cmds])
batch(["slide upper card through slot","press up button","wait","wait","s","ne"])
batch(["sw","n","press down button","wait","wait","s","w","s","s","s","s","put flask under spout","press gray button","take flask","n","n","n","n","e","n","slide upper card through slot","press up button","wait","wait","s","ne"])
send("pour liquid into hole")
batch(["sw","n","press down button","wait","wait","s","w","s","s","s","s","put flask under spout","press brown button","take flask","n","n","n","n","e","n","slide upper card through slot","press up button","wait","wait","s","ne"])
send("pour liquid into hole")
batch(["sw","n","press down button","wait","wait","s","w","w","s","get in bed","wait","get up","take all","eat green goo","drop kit","n","w","s","take canteen","slide kitchen card through slot","s","open canteen","put canteen into niche","press button","take canteen","close canteen","n","drop kitchen card","n","e","e"])
batch(["e","drop flask","drop upper card","take laser","take pliers","s","slide lower card through slot","press down button","wait","wait","wait","drop lower card","n","e","s","e","slide shuttle card through slot","push lever up"]+["wait"]*11+["pull lever down","pull lever down"]+["wait"]*11+["drop shuttle card","w","n","e","e","ne","e","e","n","open lid","take fused bedistor with pliers","put good bedistor into cube","close cube","open canteen","drink liquid","drop pliers","drop fused bedistor","drop canteen"])
batch(["s","w","w","n"])
for i in range(20):
    r = send("wait")
    if "Floyd" in r and "bound" in r: break
send("floyd, go n")
for i in range(10): send("wait")
send("floyd, get shiny fromitz board")
batch(["s","e","n","open panel","take second board","put shiny board into socket","close panel"])
print("Phase 6:", send("score").strip()[:200])

# === PHASE 7: Bio-lab ===
batch(["s","e","s","s","s"])
for i in range(5):
    r = send("wait")
    if "Floyd" in r and ("glowing" in r.lower() or "examines" in r.lower()): break
send("ne"); send("open bio-lab door"); send("se"); send("e")
send("look through window")
send("open door"); send("close door"); send("wait"); send("open door"); send("close door")
send("take mini card"); send("put mini card into pocket")
send("w"); send("open door"); send("w")
send("s"); send("open lab uniform"); send("take battery"); send("put battery into laser")
send("n"); send("sw"); send("s")
send("slide mini card through slot")
r = send("type 384")
print(f"Mini: {r.strip()[:100]}")
send("e"); send("n"); send("n"); send("turn dial to 1")

# SPECK
print("=== SPECK ===")
for i in range(35):
    r = send("fire laser at speck")
    c = r.strip()
    print(f"  {i+1}: {c[:120]}")
    if "vaporize" in c.lower() or "vanish" in c.lower():
        print("  >>> VAPORIZED!"); break
    if "can't see" in c.lower():
        print("  >>> Gone!"); break

# MICROBE
print("=== MICROBE ===")
send("turn dial to 6")
r = send("s")
print(f"S: {r.strip()[:100]}")
for i in range(20):
    r = send("fire laser at microbe")
    c = r.strip()
    print(f"  M{i+1}: {c[:120]}")
    if "warm" in c.lower(): print("  >>> WARM!"); break
    if "can't see" in c.lower(): send("wait"); continue

r = send("throw laser over edge")
print(f"Throw: {r.strip()[:100]}")

# Return to normal
send("s"); send("w"); send("n")

# Gas mask
send("open desk"); send("take gas mask"); send("wear gas mask")
print("Mask on!")

# === SPRINT (FIX: "press button" not "press up button") ===
send("press white button")
r = send("press red button")
print(f"Gas: {r.strip()[:80]}")

# Try step1 shorter path first: open office door, w, w, open door, w, w, w, s, s
# (skips lab door - might work if door is open)
r = send("open office door")
print(f"S1: {r.strip()[:80]}")
r = send("w")  # Bio Lab
print(f"S2: {r.strip()[:80]}")
# Try going w without opening lab door (step1 says w here)
r = send("w")
print(f"S3 (try w without lab door): {r.strip()[:80]}")
# Check if we moved or got blocked
if "closed" in r.lower() or "can't go" in r.lower() or "wall" in r.lower() or r.strip() == "":
    # Door was closed, need to open it - use 2 extra turns
    print("  BLOCKED! Opening lab door...")
    r = send("open lab door")
    print(f"  Open: {r.strip()[:80]}")
    r = send("w")
    print(f"  W: {r.strip()[:80]}")
    # Now continue: w, open door, w, w, w, s, s, press button = 8 more
    r = send("w")
    print(f"S5: {r.strip()[:80]}")
    r = send("open door")
    print(f"S6: {r.strip()[:80]}")
    batch(["w","w","w","s","s"])
    r = send("press button")
    print(f"ELEVATOR (long path): {r.strip()[:200]}")
else:
    # We made it through! Continue step1 path: open door, w, w, w, s, s, press button
    print("  MOVED! Step1 path works!")
    r = send("open door")
    print(f"S4: {r.strip()[:80]}")
    batch(["w","w","w","s","s"])
    r = send("press button")
    print(f"ELEVATOR (short path): {r.strip()[:200]}")

# Check if we survived
if "You have died" in r or "restart" in r.lower():
    print("DIED at elevator!")
elif "no effect" in r.lower():
    print("Button has no effect! Trying alternatives...")
    r = send("push button")
    print(f"Push: {r.strip()[:200]}")
else:
    # Wait for elevator and go north
    for i in range(3):
        r = send("wait")
        print(f"Wait {i+1}: {r.strip()[:150]}")
    # Send "n" and capture ALL output with extended timeout
    child.sendline("n")
    time.sleep(5)  # Wait 5 seconds for all text to appear
    try:
        # Try to read everything available
        child.expect(pexpect.TIMEOUT, timeout=5)
    except:
        pass
    full_output = child.before.decode('latin-1', errors='replace') if child.before else ""
    print(f"\n=== FULL FINAL OUTPUT (len={len(full_output)}) ===")
    print(full_output)
    print("=== END OF OUTPUT ===")
    
    # Try reading any remaining buffer
    try:
        remaining = child.read_nonblocking(size=4096, timeout=2)
        print(f"\n=== REMAINING BUFFER ===")
        print(remaining.decode('latin-1', errors='replace'))
    except:
        print("No remaining buffer")

child.close()
