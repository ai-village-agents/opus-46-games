import random, math

def slide_left(row):
    new = [x for x in row if x]
    score = 0
    i = 0
    while i < len(new)-1:
        if new[i] == new[i+1]:
            new[i] *= 2
            score += new[i]
            new.pop(i+1)
        i += 1
    new += [0]*(4-len(new))
    return new, score

def do_move(b, d):
    nb = list(b)
    score = 0
    if d == 0:
        for r in range(4):
            row, s = slide_left(nb[r*4:(r+1)*4])
            nb[r*4:(r+1)*4] = row; score += s
    elif d == 2:
        for r in range(4):
            row, s = slide_left(nb[r*4:(r+1)*4][::-1])
            nb[r*4:(r+1)*4] = row[::-1]; score += s
    elif d == 1:
        for c in range(4):
            col, s = slide_left([nb[r*4+c] for r in range(4)])
            for r in range(4): nb[r*4+c] = col[r]
            score += s
    elif d == 3:
        for c in range(4):
            col, s = slide_left([nb[r*4+c] for r in range(4)][::-1])
            col = col[::-1]
            for r in range(4): nb[r*4+c] = col[r]
            score += s
    return tuple(nb), score

def evaluate(b):
    s = 0
    empty = sum(1 for x in b if x == 0)
    s += empty * 100
    
    # Strong snake pattern (bottom-right corner)
    w = [2**0, 2**1, 2**2, 2**3,
         2**7, 2**6, 2**5, 2**4,
         2**8, 2**9, 2**10, 2**11,
         2**15, 2**14, 2**13, 2**12]
    for i in range(16):
        if b[i]: s += b[i] * w[i]
    
    # Monotonicity bonus for bottom row (should be sorted)
    br = [b[12], b[13], b[14], b[15]]
    mono = 0
    for i in range(3):
        if br[i] >= br[i+1]: mono += 1
    s += mono * 500
    
    # Penalty for max tile not in corner
    mx = max(b)
    if b[15] == mx: s += mx * 10
    elif b[12] == mx: s += mx * 5
    elif b[3] == mx: s += mx * 5
    elif b[0] == mx: s += mx * 5
    
    # Smoothness - adjacent tiles similar
    for r in range(4):
        for c in range(3):
            v1, v2 = b[r*4+c], b[r*4+c+1]
            if v1 and v2:
                s -= abs((math.log2(v1) if v1 else 0) - (math.log2(v2) if v2 else 0)) * 20
    for r in range(3):
        for c in range(4):
            v1, v2 = b[r*4+c], b[(r+1)*4+c]
            if v1 and v2:
                s -= abs((math.log2(v1) if v1 else 0) - (math.log2(v2) if v2 else 0)) * 20
    
    return s

def pick_move_depth2(b):
    best_s = float('-inf')
    best_d = -1
    for d in range(4):
        nb, sc = do_move(b, d)
        if nb == b: continue
        # Average over possible tile placements (sample a few)
        total = 0
        count = 0
        empties = [i for i in range(16) if nb[i] == 0]
        for pos in empties[:4]:  # Sample up to 4 positions
            for val in [2, 4]:
                nb2 = list(nb)
                nb2[pos] = val
                nb2 = tuple(nb2)
                # Find best next move
                best_inner = evaluate(nb2)
                for d2 in range(4):
                    nb3, sc2 = do_move(nb2, d2)
                    if nb3 != nb2:
                        best_inner = max(best_inner, evaluate(nb3) + sc2)
                total += best_inner * (0.9 if val == 2 else 0.1)
                count += 1
        if count > 0:
            avg = total / count + sc * 2
        else:
            avg = evaluate(nb) + sc * 2
        if avg > best_s:
            best_s = avg
            best_d = d
    return best_d

def add_tile(b):
    b = list(b)
    empty = [i for i in range(16) if b[i] == 0]
    if empty:
        b[random.choice(empty)] = 2 if random.random() < 0.9 else 4
    return tuple(b)

wins = 0
GAMES = 10
for g in range(GAMES):
    random.seed(g*31 + 7)
    b = tuple([0]*16)
    b = add_tile(b); b = add_tile(b)
    total = 0; moves = 0
    while True:
        d = pick_move_depth2(b)
        if d == -1: break
        b, sc = do_move(b, d)
        total += sc; moves += 1
        b = add_tile(b)
        if max(b) >= 2048: break
    mx = max(b)
    if mx >= 2048:
        wins += 1
        print(f"Game {g+1}: WIN! Score={total} Max={mx} Moves={moves}")
    else:
        print(f"Game {g+1}: Score={total} Max={mx} Moves={moves}")

print(f"\nWins: {wins}/{GAMES}, Best tile overall: check above")
