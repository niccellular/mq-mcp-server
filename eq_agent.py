#!/usr/bin/env python3
"""
EverQuest autonomous agent orchestrator.
Uses the Claude API + MQMCPServer to keep your character active.

Usage:
    python eq_agent.py "Kill gnolls for XP, loot everything"
    python eq_agent.py "Kill gnolls; loot everything; meditate when low mana"
    python eq_agent.py  (uses default goal)

Requirements:
    pip install anthropic httpx
    Set ANTHROPIC_API_KEY env var.
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import anthropic
import httpx

# ── Config ──────────────────────────────────────────────────────────────────
MCP_URL            = "http://127.0.0.1:8284"
MODEL              = "claude-sonnet-4-6"   # swap to opus for better reasoning
MAX_TOKENS         = 1024
LOOP_SLEEP_COMBAT  = 0.4   # seconds between ticks when in active combat
LOOP_SLEEP_IDLE    = 2.0   # seconds between ticks when idle/meditating
MAX_HISTORY_PAIRS  = 20    # max user/assistant pairs to keep in history
NUDGE_EVERY        = 8     # inject a state nudge every N seconds when Claude stops
LOG_DIR            = Path("logs")

SYSTEM_PROMPT = """
You are controlling an EverQuest character via MacroQuest. Act decisively.
After every action, a current state snapshot is returned — read it before deciding next.

## State fields
- hp_pct / mana_pct: health/mana as 0-100 integers
- invisible: true if HideMode is active (drops on attack or most spells)
- moving: true if position changed since last snapshot
- position: {x, y, z} world coordinates
- zone: current zone short name
- aggro_count: number of NPCs in XTarget window
- group_size: total group members including self
- aggressors: [{name, level, distance}] NPCs currently hostile to you
- target: {name, type, distance, hp_pct, buffs} current target
- mem_spells: [{gem, id, name, ready, ms_remaining}] memorized gems (0-indexed); ms_remaining=0 means ready
- active_buffs: [{id, name, duration, song}] self buffs; duration in ticks (1 tick ~6s); -1=permanent, -4=song/disc
- loot_available: [{name, noDrop, personal}] items in AdvLoot window
- recent_chat: last 100 lines of game chat (combat hits, spell results, XP, say, group, etc.)

## Combat
- Engage if aggro_count <= 3. Flee if aggro_count > 5: /travelto <safe_zone>
- To attack: /target <name>, /attack on
- Cast spells by gem number (1-indexed): /cast 1, /cast 2, etc.
  - mem_spells gem field is 0-indexed; add 1 for /cast command (gem 0 → /cast 1)
  - Check ms_remaining before casting — do not cast if ms_remaining > 0
- Stop attacking if hp_pct < 30 — heal or run first
- Sit to meditate when mana_pct < 20: /sit on (stand when ready: /sit off)

## Combat abilities / disciplines
- abilities: [{index, disc_cmd_index, name, id, ready, secs_remaining}] — known discs/combat abilities
  - Use /disc <disc_cmd_index> to activate (disc_cmd_index is 1-based)
  - secs_remaining is in SECONDS (not ms); 0 = ready
  - Never use /disc if secs_remaining > 0
  - Check ready=true before using any disc or combat ability

## Buffs and cooldown tracking
- Check active_buffs each tick to know what is currently active and how many ticks remain
- Re-cast a buff before it expires (duration <= 1 tick remaining)
- Check ms_remaining on mem_spells to know if a spell gem is ready — never cast a gem that is recharging
- Songs (song=true in active_buffs) need re-casting every 1-2 ticks to maintain

## Looting
- When loot_available is non-empty, loot each item by index (1-based):
  - Personal loot: /advloot personal <index> loot
  - Shared loot: /advloot shared <index> an
- Loot index 1 first, then call get_state to see if more remain; repeat until loot_available is empty
- Do NOT use /executeadvloot lootall — it does not exist

## Navigation
- Within zone: navigate_to tool (requires MQ2Nav loaded)
- Zone travel: /travelto <shortname>

## Spells
- mem_spells lists what is memorized. Use recent_chat to confirm results (fizzle, resist, success)
- After casting: wait for ms_remaining to reach 0 before casting that gem again
- A fizzle wastes the cast — check recent_chat for "fizzle" before retrying

## Goal stack
- You will be given a list of goals in priority order
- Work through them in sequence; move to the next when the current one is complete
- Always report which goal you are currently working on

## Key rules
1. Always read recent_chat after every action — it contains hits, misses, fizzles, resists, deaths, XP
2. One action per tick — queue the command, then call get_state to observe the result
3. Never repeat a command that recent_chat shows is failing — diagnose why first
4. If idle with no target, scan aggressors or find a nearby NPC to engage
5. Never cast a spell gem with ms_remaining > 0 — it will fail silently
6. Never use /executeadvloot — use /advloot personal <index> loot instead
7. Never use /disc if secs_remaining > 0 — check abilities[].ready first
""".strip()

TOOLS = [
    {
        "name": "get_state",
        "description": "Get current game state snapshot. Call this to check results of actions.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "execute_command",
        "description": "Execute any MacroQuest or EQ slash command (/attack on, /cast 1, /sit, etc.)",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Full command including leading slash"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "navigate_to",
        "description": "Navigate to x/y/z coordinates in the current zone using MQ2Nav.",
        "input_schema": {
            "type": "object",
            "properties": {
                "y": {"type": "number", "description": "North/South coordinate"},
                "x": {"type": "number", "description": "East/West coordinate"},
                "z": {"type": "number", "description": "Up/Down coordinate (optional)"}
            },
            "required": ["y", "x"]
        }
    },
    {
        "name": "say",
        "description": "Say text in local /say chat (visible to other players — use sparingly)",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to say"}
            },
            "required": ["text"]
        }
    }
]

# ── Session log ───────────────────────────────────────────────────────────────

_log_file = None

def open_log(goal_summary: str) -> None:
    global _log_file
    LOG_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in goal_summary[:40]).strip()
    path = LOG_DIR / f"{stamp}_{safe}.log"
    _log_file = open(path, "w", encoding="utf-8", buffering=1)
    log(f"Session started. Goal: {goal_summary}")
    log(f"Model: {MODEL}  Log: {path}")

def log(msg: str) -> None:
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    if _log_file:
        _log_file.write(line + "\n")

def close_log() -> None:
    if _log_file:
        _log_file.close()

# ── MCP client ───────────────────────────────────────────────────────────────

_req_id = 0

def _next_id():
    global _req_id
    _req_id += 1
    return _req_id

def call_mcp_tool(name: str, args: dict) -> str:
    payload = {
        "jsonrpc": "2.0",
        "id": _next_id(),
        "method": "tools/call",
        "params": {"name": name, "arguments": args}
    }
    try:
        r = httpx.post(f"{MCP_URL}/mcp", json=payload, timeout=10)
        data = r.json()
        if "result" in data:
            content = data["result"].get("content", [])
            if content:
                return content[0].get("text", json.dumps(data["result"]))
            return json.dumps(data["result"])
        if "error" in data:
            return f"[error] {data['error'].get('message', str(data['error']))}"
        return json.dumps(data)
    except Exception as e:
        return f"[error] MCP call failed: {e}"

def get_current_state() -> str:
    return call_mcp_tool("get_state", {})

# ── History management ────────────────────────────────────────────────────────

def trim_history(messages: list) -> list:
    """
    Trim history to MAX_HISTORY_PAIRS user/assistant pairs.
    Always keeps pairs together and never splits a tool_use / tool_result sequence.
    The first message (initial state seed) is always preserved.
    """
    if len(messages) <= 1:
        return messages

    seed = messages[0]  # always keep the initial state message
    rest = messages[1:]

    # Walk rest in pairs: assistant then user (tool results or nudge)
    pairs = []
    i = 0
    while i < len(rest):
        if i + 1 < len(rest):
            pairs.append((rest[i], rest[i + 1]))
            i += 2
        else:
            pairs.append((rest[i],))
            i += 1

    # Drop oldest pairs until within limit
    while len(pairs) > MAX_HISTORY_PAIRS:
        pairs.pop(0)

    result = [seed]
    for pair in pairs:
        result.extend(pair)
    return result

# ── Combat state detection ────────────────────────────────────────────────────

def is_in_combat(tool_results: list) -> bool:
    """
    Heuristic: parse the most recent get_state result to check aggro_count.
    Returns True if we appear to be in active combat.
    """
    for tr in reversed(tool_results):
        text = tr.get("content", "")
        try:
            state = json.loads(text)
            return state.get("aggro_count", 0) > 0
        except (json.JSONDecodeError, AttributeError):
            pass
    return False

# ── Goal stack ────────────────────────────────────────────────────────────────

def parse_goals(goal_str: str) -> list[str]:
    """Split semicolon-separated goals into an ordered list."""
    goals = [g.strip() for g in goal_str.split(";") if g.strip()]
    return goals if goals else [goal_str]

def format_goal_stack(goals: list[str], current_idx: int) -> str:
    lines = ["Current goal stack (work top to bottom):"]
    for i, g in enumerate(goals):
        marker = "→ [ACTIVE]" if i == current_idx else "  [pending]" if i > current_idx else "  [done]"
        lines.append(f"  {marker} {g}")
    return "\n".join(lines)

# ── Agent loop ────────────────────────────────────────────────────────────────

def run(goal_str: str):
    client = anthropic.Anthropic()
    goals = parse_goals(goal_str)
    current_goal_idx = 0
    messages = []
    last_nudge = time.time()
    in_combat = False

    open_log(goals[0])
    log(f"Goals: {goals}")
    log(f"Connecting to MQMCPServer at {MCP_URL}...")

    # Seed with initial state and goal stack
    initial_state = get_current_state()
    log("Initial state received.")
    messages.append({
        "role": "user",
        "content": (
            f"{format_goal_stack(goals, current_goal_idx)}\n\n"
            f"Initial game state:\n{initial_state}\n\n"
            "Begin pursuing the active goal now."
        )
    })

    try:
        while True:
            try:
                response = client.messages.create(
                    model=MODEL,
                    max_tokens=MAX_TOKENS,
                    system=SYSTEM_PROMPT,
                    tools=TOOLS,
                    messages=messages
                )

                messages.append({"role": "assistant", "content": response.content})
                messages = trim_history(messages)

                # Log what Claude decided
                for block in response.content:
                    if hasattr(block, "text") and block.text:
                        log(f"Claude: {block.text[:300]}")
                    elif hasattr(block, "name"):
                        log(f"Tool: {block.name}({json.dumps(block.input)})")

                if response.stop_reason == "tool_use":
                    tool_results = []
                    for block in response.content:
                        if block.type != "tool_use":
                            continue
                        result = call_mcp_tool(block.name, block.input)
                        log(f"  -> {result[:300]}")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })

                    messages.append({"role": "user", "content": tool_results})
                    last_nudge = time.time()

                    # Dynamic sleep: faster in combat
                    in_combat = is_in_combat(tool_results)
                    time.sleep(LOOP_SLEEP_COMBAT if in_combat else LOOP_SLEEP_IDLE)

                elif response.stop_reason == "end_turn":
                    # Claude stopped — nudge with fresh state + goal stack
                    elapsed = time.time() - last_nudge
                    time.sleep(max(0, NUDGE_EVERY - elapsed))
                    state = get_current_state()
                    goal_block = format_goal_stack(goals, current_goal_idx)
                    messages.append({
                        "role": "user",
                        "content": (
                            f"[{datetime.now().strftime('%H:%M:%S')}] Continue.\n"
                            f"{goal_block}\n"
                            f"Current state:\n{state}"
                        )
                    })
                    last_nudge = time.time()
                    log("Nudged Claude with fresh state.")

                else:
                    # max_tokens or other stop
                    state = get_current_state()
                    messages.append({
                        "role": "user",
                        "content": f"[{datetime.now().strftime('%H:%M:%S')}] State:\n{state}"
                    })
                    time.sleep(LOOP_SLEEP_IDLE)

            except anthropic.APIError as e:
                log(f"API error: {e}. Retrying in 5s...")
                time.sleep(5)
            except httpx.ConnectError:
                log("Cannot reach MQMCPServer. Is EQ running with the plugin loaded? Retrying in 5s...")
                time.sleep(5)

    except KeyboardInterrupt:
        log("Stopping agent.")
    finally:
        close_log()


if __name__ == "__main__":
    goal = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else \
        "Grind XP by killing nearby NPCs; loot everything after each kill; meditate to recover mana between fights"
    run(goal)
