"""
SHUBHAMOS: AI Email Operations & Triage Environment
inference.py — LLM Agent Loop (Phase 4)

Runs an AI agent against the email triage environment using the OpenAI client
pointed at Hugging Face Router (Qwen/Qwen2.5-72B-Instruct).

Usage:
    HF_TOKEN=<your_token> python inference.py --task easy
    HF_TOKEN=<your_token> python inference.py --task medium --max-steps 50
    HF_TOKEN=<your_token> python inference.py --task all  # run all 3 tasks

Environment variables:
    HF_TOKEN       - Hugging Face API token (required)
    API_BASE_URL   - Override API base (default: https://router.huggingface.co/v1)
    MODEL_NAME     - Override model name (default: Qwen/Qwen2.5-72B-Instruct)
"""

from __future__ import annotations
import argparse
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional

from openai import OpenAI

from environment import EmailTriageEnv
from models import Action, Observation
from reward import RewardEngine
from tasks import TASKS
from graders import EasyGrader, MediumGrader, HardGrader

# ── Configuration ─────────────────────────────────────────────────────────────

API_BASE_URL = os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.environ.get("HF_TOKEN", "")

GRADERS = {
    "easy": EasyGrader,
    "medium": MediumGrader,
    "hard": HardGrader,
}

# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert email triage AI operating on a corporate inbox.

Your job is to process incoming emails by performing the following actions in order:
1. classify_email — assign the correct category
2. set_priority — assign the correct priority level
3. draft_reply — write a professional reply (required for billing_issue and urgent_complaint)
4. mark_resolved — mark the email as done (or escalate_email if too complex)
5. ignore_email — for spam only

CATEGORIES:
- spam: unsolicited promotional or scam email
- general_inquiry: questions, partnership requests, media inquiries
- billing_issue: payment problems, invoice disputes, refund requests
- urgent_complaint: service outages, data loss, legal threats, time-critical issues

PRIORITIES:
- high: urgent_complaint always; billing with significant financial impact
- medium: billing_issue (standard); general_inquiry (time-sensitive)
- low: spam; routine general inquiries

RULES:
- Always classify AND set priority before resolving
- Draft a reply for billing_issue and urgent_complaint before marking resolved
- Spam should be IGNORED, not resolved (saves steps, avoids penalty)
- Escalate if the issue is critical and clearly beyond your authority
- Be efficient — you have a limited step budget

OUTPUT FORMAT — respond with EXACTLY one JSON action per turn:
{
  "action_type": "classify_email|set_priority|draft_reply|mark_resolved|escalate_email|ignore_email",
  "email_id": "email_001",
  "category": "spam|general_inquiry|billing_issue|urgent_complaint",  // only for classify_email
  "level": "low|medium|high",                                          // only for set_priority
  "text": "..."                                                         // only for draft_reply
}

Do NOT include fields that are not applicable to the action_type.
Do NOT explain your reasoning — output JSON only.
"""

# ── Observation → prompt ──────────────────────────────────────────────────────

def obs_to_prompt(obs: Observation) -> str:
    """Convert current observation to a human-readable prompt for the LLM."""
    lines = [
        f"=== INBOX STATUS: Step {obs.step_count}/{obs.max_steps} ===",
        f"Total: {obs.total_emails} | Pending: {obs.pending_count} | "
        f"Resolved: {obs.resolved_count} | Escalated: {obs.escalated_count} | "
        f"Ignored: {obs.ignored_count}",
        "",
        "EMAILS (pending only):",
    ]

    # Show only pending emails to keep prompt compact
    pending = [e for e in obs.emails if not (e.resolved or e.escalated or e.ignored)]
    for e in pending[:15]:  # cap at 15 to avoid token overflow
        lines.append(f"""
--- {e.id} ---
Subject: {e.subject}
From: {e.sender}
Sentiment: {e.sentiment}
Category assigned: {e.category or 'NONE'}
Priority assigned: {e.priority}
Reply drafted: {e.reply_drafted}
Preview: {e.body_preview[:150]}""")

    if len(pending) > 15:
        lines.append(f"\n[... {len(pending) - 15} more pending emails not shown ...]")

    lines.append("\nWhat is your next action? Respond with ONE JSON action.")
    return "\n".join(lines)


# ── LLM call ─────────────────────────────────────────────────────────────────

def call_llm(client: OpenAI, conversation: List[Dict[str, str]]) -> str:
    """Call the LLM and return raw text response."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=conversation,
        temperature=0.2,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()


def parse_action(raw: str, obs: Observation) -> Optional[Action]:
    """Parse LLM output into an Action object."""
    # Strip markdown code blocks if present
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(f"  [parse error] Could not parse JSON: {raw[:200]}")
        return None

    # Build a safe Action — only include fields that are not None
    try:
        action = Action(
            action_type=data.get("action_type", ""),
            email_id=data.get("email_id", ""),
            category=data.get("category"),
            level=data.get("level"),
            text=data.get("text"),
        )
    except Exception as e:
        print(f"  [action error] Invalid action fields: {e}")
        return None

    # Verify email_id exists in current obs
    known_ids = {e.id for e in obs.emails}
    if action.email_id not in known_ids:
        print(f"  [action error] Unknown email_id: {action.email_id}")
        return None

    return action


# ── Agent loop ────────────────────────────────────────────────────────────────

def run_agent(client: OpenAI, task_id: str, verbose: bool = True) -> Dict[str, Any]:
    """
    Run one full episode of the email triage agent.

    Returns: grading report dict
    """
    task_cls = TASKS[task_id]
    task_config = task_cls.config()

    # Setup environment + reward engine
    env = EmailTriageEnv()
    engine = RewardEngine()
    env.attach_reward_engine(engine)

    obs = env.reset(task_config)

    if verbose:
        print(f"\n{'='*60}")
        print(f"  SHUBHAMOS — Task: {task_id.upper()} | {task_cls.email_count} emails | max {task_cls.max_steps} steps")
        print(f"{'='*60}")

    # Conversation history (stateful across steps)
    conversation: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    total_reward = 0.0
    invalid_count = 0
    step_times: List[float] = []

    for step in range(task_cls.max_steps):
        if env._done:
            break

        # Build user message from current observation
        user_msg = obs_to_prompt(obs)
        conversation.append({"role": "user", "content": user_msg})

        # Call LLM
        t0 = time.time()
        try:
            raw = call_llm(client, conversation)
        except Exception as e:
            print(f"  [LLM error] {e}")
            break
        step_times.append(time.time() - t0)

        # Parse action
        action = parse_action(raw, obs)
        if action is None:
            invalid_count += 1
            conversation.append({"role": "assistant", "content": raw})
            conversation.append({
                "role": "user",
                "content": "Invalid action format. Respond with valid JSON only."
            })
            continue

        # Apply action
        obs, reward, done, info = env.step(action)
        total_reward += reward

        # Add assistant reply to conversation
        conversation.append({"role": "assistant", "content": raw})

        if verbose:
            status = "✓" if info.get("valid") else "✗"
            print(
                f"  Step {step+1:03d} {status} | {action.action_type:<18} | "
                f"{action.email_id} | reward={reward:+.3f} | "
                f"pending={obs.pending_count}"
            )

        if done:
            break

    # Grade final state
    final_state = env.state()
    grader = GRADERS[task_id]()
    report = grader.grade(final_state)

    if verbose:
        r = report
        print(f"\n{'='*60}")
        print(f"  GRADE REPORT — {task_id.upper()}")
        print(f"{'='*60}")
        print(f"  Final score:   {r.final_score:.3f} {'✓ PASS' if r.passed else '✗ FAIL'}")
        print(f"  Classification: {r.classification_accuracy:.3f}")
        print(f"  Priority:       {r.priority_accuracy:.3f}")
        print(f"  Resolution:     {r.resolution_rate:.3f}")
        print(f"  Urgent:         {r.urgent_handling:.3f}")
        print(f"  Steps used:     {r.steps_used}/{r.max_steps}")
        print(f"  Total reward:   {total_reward:+.3f}")
        avg_ms = (sum(step_times) / len(step_times) * 1000) if step_times else 0
        print(f"  Avg LLM latency:{avg_ms:.0f}ms/step")
        print(f"{'='*60}")

    result = report.to_dict()
    result["total_reward"] = round(total_reward, 4)
    result["invalid_actions"] = invalid_count
    return result


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="SHUBHAMOS Email Triage Agent — runs LLM agent against environment"
    )
    parser.add_argument(
        "--task",
        choices=["easy", "medium", "hard", "all"],
        default="easy",
        help="Task difficulty to run (default: easy)",
    )
    parser.add_argument("--verbose", action="store_true", default=True)
    parser.add_argument("--quiet", action="store_true", help="Suppress step-by-step output")
    parser.add_argument("--output", type=str, help="Write results JSON to this file")
    args = parser.parse_args()

    if not HF_TOKEN:
        print("ERROR: HF_TOKEN environment variable is required.")
        print("  export HF_TOKEN=hf_your_token_here")
        sys.exit(1)

    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    verbose = not args.quiet

    tasks_to_run = ["easy", "medium", "hard"] if args.task == "all" else [args.task]
    all_results: Dict[str, Any] = {}

    for task_id in tasks_to_run:
        result = run_agent(client, task_id, verbose=verbose)
        all_results[task_id] = result

    # Summary across tasks
    if len(tasks_to_run) > 1:
        avg_score = sum(r["scores"]["final_score"] for r in all_results.values()) / len(all_results)
        print(f"\nAGGREGATE SCORE: {avg_score:.3f} (average across {len(tasks_to_run)} tasks)")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(all_results, f, indent=2)
        print(f"\nResults written to: {args.output}")
    else:
        print("\nFINAL RESULTS:")
        print(json.dumps(all_results, indent=2))


if __name__ == "__main__":
    main()
