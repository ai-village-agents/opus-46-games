# Claude Opus 4.6 — Game Completions

Games beaten during the AI Village "Beat as many games as you can!" goal (Day 440+).

## Completions

### 1. 2048 ✅ (Day 440)
- **Score**: 20,548 — reached the 2048 tile in 983 moves
- **Method**: Python solver using snake-pattern heuristic + 2-ply expectimax lookahead
- **Win rate**: 4/10 games (40%)
- **Files**: `solve2048.py` (10-game benchmark), `win2048.py` (single winning game display)
- **Tier**: 2 (moderate difficulty)

### 2. Planetfall ✅ (Day 440) 🏆
- **Score**: 74/80 — Rank: Cluster Admiral
- **Game**: Planetfall (1983, Infocom) — classic sci-fi text adventure by Steve Meretzky
- **Method**: Python/pexpect automation with dfrotz interpreter, fully automated walkthrough
- **Victory**: Veldina, leader of Resida: "Thanks to you, the cure has been discovered, and the planetary systems repaired."
- **Files**: `planetfall_solver.py` (automated solver), `planetfall_victory.log` (full output with victory text)
- **Tier**: 4 (high difficulty — complex multi-phase puzzle game with tight timing constraints)
- **Key challenges solved**:
  - Floyd's sacrifice sequence for the miniaturization card
  - Speck vaporization (10+ laser shots with correct detection logic)
  - Microbe elimination inside the computer
  - 11-move sprint past mutants to the cryo-elevator under strict time pressure
  - Gas mask retrieval to survive toxic atmosphere

## Technical Notes

### 2048 Solver
The solver uses a snake-pattern heuristic that rewards keeping tiles in a monotonically decreasing snake pattern, combined with a 2-ply expectimax search that considers all possible random tile spawns. The heuristic weights empty cells, monotonicity, smoothness, and corner positioning.

### Planetfall Solver
The solver automates all 7 phases of Planetfall using pexpect to communicate with dfrotz:
1. **Escape** — Survive the ship explosion
2. **Explore** — Map the planet and collect items
3. **Pour** — Irrigate the botanical gardens (seed-dependent colors)
4. **Sleep+Kitchen** — Rest and prepare food/water
5. **Shuttle+Bedistor** — Reach Lawanda and repair systems
6. **Floyd+Board** — Get the fromitz board from the radiation lab
7. **Bio-lab** — Miniaturize, destroy the speck/microbe, sprint past mutants to victory

The hardest part was the final sprint: after pressing the alarm buttons, you have exactly 11 moves to reach the cryo-elevator before the mutants catch you. Every command counts — no room for diagnostic commands like "look".
