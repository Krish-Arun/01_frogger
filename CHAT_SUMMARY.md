# Chat Summary: Frogger Lab

## Request
Inspect the existing Python/Pygame Frogger project, fix the deliberate collision bug described in `README.md`, and implement the remaining features (lives, goal/score, timer). Constraints: no rewrite, keep architecture and conventions, no new libraries, don't modify `README.md`, and **git commit after each task**.

## Architecture found (before changes)
| File | Role |
|---|---|
| `frogger/main.py` | Pygame init, event loop, `engine.handle_keydown`, `engine.update`, `engine.draw`, 60 FPS clock |
| `game/game_engine.py` | `GameEngine`: builds frog and vehicles (6 lanes, speeds `[1.5,-2,2,-2.5,1.5,-2]`), input, per-frame update, draw |
| `game/frog.py` | `Frog`: grid position, one-cell moves, cannot go below start row, `reset`, `get_rect` |
| `game/vehicle.py` | `Vehicle`: pixel-space movement (px/frame), wraps at screen edges, `get_rect` |
| `game/collisions.py` | `check_collision` (buggy) |
| `game/renderer.py` | Constants, `draw_scene`, `draw_text`, `draw_banner` |

Original behavior: on a collision the frog reset instantly; reaching the goal also just reset the frog; R rebuilt entities.

## Task 1: Collision fix (commit `Fix collision detection using rect overlap`)
- **Bug:** collision compared the vehicle's grid column (`int(v.x // 50)`) with the frog's column plus the same row. Vehicles are 40–70 px wide and move per pixel, so they can visually overlap the frog while their left-edge column differs, and the hit was missed.
- **Fix:** `collisions.py` now uses `frog.get_rect(CELL_SIZE).colliderect(v.get_rect(CELL_SIZE))` over all vehicles, importing `CELL_SIZE` from `renderer` instead of redefining it. The function only reports whether a hit occurred; consequences live in the engine.
- Verified with a small script: an overlap across a column boundary gives True; no overlap and a different lane give False.

## Task 2: Lives and respawn (commit `Add 3 lives, hit state and respawn`)
- New constants: `STARTING_LIVES = 3`, `HIT_PAUSE_MS = 800`; states `PLAYING`, `HIT`, `GAME_OVER`.
- `_reset_game_state()` is called from `__init__` and on R.
- `_lose_life()` decrements lives by one. At 0 lives the state becomes `GAME_OVER`, with the frog left at the hit spot. Otherwise the state becomes `HIT` and the hit time is recorded.
- In `HIT`, the frog stays in place (drawn white via `draw_scene(..., hit=True)`) for 800 ms and input is ignored. Vehicles keep moving. After the pause the frog resets and play returns to `PLAYING`.
- Input is ignored in any state other than `PLAYING`, except R.
- The UI shows `Lives: N` and a "Game Over - press R to restart" banner.
- Renderer: added `COLOR_FROG_HIT` and a `hit` parameter.

## Task 3: Goal and score (commit `Add goal win state and score`)
- Added the `WON` state and `SCORE_PER_CROSSING = 100`.
- The goal check runs before the collision check, so reaching the goal always wins. It adds the score, sets `WON` and returns.
- The "You Won! - press R to restart" banner and the `Score: N` display were added.
- In `WON` the game ignores movement, collisions and the timer.

## Task 4: 30-second timer (commit `Add 30s per-attempt countdown; timeout costs a life`)
- `ATTEMPT_TIME_MS = 30_000`. An "attempt" means one life: the timer resets to 30 s whenever an attempt begins (game start, after respawn, after R).
- The countdown subtracts real elapsed time from `pygame.time.get_ticks()` each frame (`last_tick_ms`), so it does not depend on FPS. It only runs in `PLAYING` and so freezes during the hit pause, win and game over.
- Timeout calls the same `_lose_life()` as a collision. It costs a life with the visible pause and a respawn with a fresh timer. The third loss gives Game Over, which means no free retries and no instant game over.
- Displayed as `Time: N` (rounded up, using `math.ceil`).
- The goal wins regardless of time remaining. Checked order each frame: goal, collision, timeout.

## Verification performed
Headless runs (SDL dummy driver, mocked `pygame.time.get_ticks`):
- **Lives:** three forced collisions went 3→2→1→0 lives, with the HIT pause visible at 500 ms and the respawn at 1000 ms; input was blocked at Game Over; R restored state and lives.
- **Goal:** seven UP presses gave `WON`, score 100, and DOWN was ignored; R reset the score.
- **Timer:**
  - 10 s elapsed left 20 s.
  - A 30 s timeout cost a life, with respawn and a fresh 30 s.
  - Three timeouts gave Game Over, and the timer stayed frozen afterwards.
  - R restored 3 lives and 30 s.
  - Winning froze the timer.
- `python main.py` ran for 3 s with no crash (stopped by timeout).

## Assumptions and unverified items
- 100 points per win.
- Vehicle speeds are px/frame (FPS-dependent) and were deliberately left unchanged.
- The on-screen layout and the white hit flash were not checked by eye.
- Not run separately: R after a timeout and after a single non-fatal collision (the same reset code path as Game Over).
- No real keyboard-driven playtest was done.

## Git history
```
d2f4a3a Add 30s per-attempt countdown; timeout costs a life
3d6cb40 Add goal win state and score
6faf005 Add 3 lives, hit state and respawn
2c9e238 Fix collision detection using rect overlap
3e4e882 Move README to repository root
5f37c7a Initial Frogger starter
```
`README.md` was not modified. Git warns that LF will be converted to CRLF on this Windows setup; this is harmless.
