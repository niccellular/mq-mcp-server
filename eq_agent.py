#!/usr/bin/env python3
"""
EverQuest autonomous agent orchestrator.
Uses the Claude API + MQMCPServer to keep your character active.

Usage:
    python eq_agent.py "Kill gnolls for XP, loot everything"
    python eq_agent.py  (uses default goal)

Requirements:
    pip install anthropic httpx
    Set ANTHROPIC_API_KEY env var.
"""

import json
import sys
import time
from datetime import datetime

import anthropic
import httpx

# ── Config ──────────────────────────────────────────────────────────────────
MCP_URL      = "http://127.0.0.1:8284"
MODEL        = "claude-sonnet-4-6"   # swap to opus for better reasoning
MAX_TOKENS   = 1024
LOOP_SLEEP   = 1.5     # seconds between ticks when idle
MAX_HISTORY  = 30      # message pairs to keep (trim older to avoid ctx overflow)
NUDGE_EVERY  = 8       # inject a state nudge every N seconds even if Claude is quiet

SYSTEM_PROMPT = """
You are controlling an EverQuest character via MacroQuest. Act decisively.
After every action, a current state snapshot is returned — read it before deciding next.

## State fields
- hp_pct / mana_pct: health/mana percentages
- invisible: true if currently invisible
- moving: true if position changed last tick
- position: {x, y, z}
- zone: current zone short name
- aggro_count: enemies in XTarget window
- aggressors: [{name, level, distance}] enemies targeting you
- target: {name, type, distance, hp_pct} current target
- mem_spells: [{gem, name, id}] memorized spell gems (0-indexed)
- loot_available: [{name, noDrop, personal}] items in AdvLoot window
- recent_chat: last 10 lines of game/MQ chat (combat hits, spell results, etc.)

## Combat
- Engage if aggro_count <= 3. Flee if aggro_count > 5: /travelto <safe_zone>
- To attack: /target <name>, /attack on, /cast <gem> for spells
- Stop at hp_pct < 30 — heal or run first
- Sit to meditate when mana_pct < 20: /sit on (stand when full: /sit off)

## Looting
- When loot_available is non-empty: /executeadvloot lootall
- Confirm with get_state after looting

## Navigation
- Within zone: navigate_to tool
- Zone travel: execute_command "/travelto <shortname>"

## Spells
- Cast by gem slot: /cast 1  (checks recent_chat for fizzle/success)
- mem_spells shows gem→name mapping

## Invisibility
- invisible=true means hidden. Drops on attack or most spells.

## Key rules
1. Always check recent_chat for feedback (hits, misses, fizzles, deaths)
2. One action at a time — wait for state to confirm before next
3. Never spam the same command if recent_chat shows it failing
4. If you have nothing to do, find a nearby NPC and engage it
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

# ── Agent loop ────────────────────────────────────────────────────────────────

def ts() -> str:
    return datetime.now().strftime("%H:%M:%S")

def trim_history(messages: list) -> list:
    """Keep the last MAX_HISTORY*2 messages to avoid context overflow."""
    if len(messages) > MAX_HISTORY * 2:
        messages = messages[-(MAX_HISTORY * 2):]
    return messages

def run(goal: str):
    client = anthropic.Anthropic()
    messages = []
    last_nudge = time.time()

    print(f"[{ts()}] Starting agent. Goal: {goal}")
    print(f"[{ts()}] Connecting to MQMCPServer at {MCP_URL}...")

    # Seed with initial state
    initial_state = get_current_state()
    print(f"[{ts()}] Initial state received.")
    messages.append({
        "role": "user",
        "content": (
            f"Goal: {goal}\n\n"
            f"Initial game state:\n{initial_state}\n\n"
            "Begin pursuing the goal now."
        )
    })

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

            # Log what Claude said/decided
            for block in response.content:
                if hasattr(block, "text") and block.text:
                    print(f"[{ts()}] Claude: {block.text[:200]}")
                elif hasattr(block, "name"):
                    print(f"[{ts()}] Tool: {block.name}({json.dumps(block.input)})")

            if response.stop_reason == "tool_use":
                # Execute all tool calls and collect results
                tool_results = []
                for block in response.content:
                    if block.type != "tool_use":
                        continue
                    result = call_mcp_tool(block.name, block.input)
                    print(f"[{ts()}]  -> {result[:200]}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

                messages.append({"role": "user", "content": tool_results})
                last_nudge = time.time()
                time.sleep(LOOP_SLEEP)

            elif response.stop_reason == "end_turn":
                # Claude decided it was done — nudge it with fresh state
                elapsed = time.time() - last_nudge
                time.sleep(max(0, NUDGE_EVERY - elapsed))
                state = get_current_state()
                now = ts()
                messages.append({
                    "role": "user",
                    "content": (
                        f"[{now}] Continue pursuing goal: {goal}\n"
                        f"Current state:\n{state}"
                    )
                })
                last_nudge = time.time()
                print(f"[{now}] Nudged Claude with fresh state.")

            else:
                # max_tokens or other stop — just continue
                state = get_current_state()
                messages.append({
                    "role": "user",
                    "content": f"[{ts()}] State:\n{state}"
                })
                time.sleep(LOOP_SLEEP)

        except anthropic.APIError as e:
            print(f"[{ts()}] API error: {e}. Retrying in 5s...")
            time.sleep(5)
        except httpx.ConnectError:
            print(f"[{ts()}] Cannot reach MQMCPServer. Is EQ running with the plugin loaded? Retrying in 5s...")
            time.sleep(5)
        except KeyboardInterrupt:
            print(f"\n[{ts()}] Stopping agent.")
            break


if __name__ == "__main__":
    goal = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else \
        "Grind XP by killing nearby NPCs. Loot everything. Meditate to recover mana between fights."
    run(goal)
