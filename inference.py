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
    """Call the LLM and return raw text response with exponential backoff for network errors."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=conversation,
                temperature=0.2,
                max_tokens=300,
                timeout=30,  # enforce 30s timeout per call
            )
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("Empty response from API")
            return content.strip()
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"  [API Fatal] Max retries reached: {e}")
                return ""  # Trigger fallback downstream
            time.sleep(2 ** attempt)  # 1s, 2s, 4s

    return ""

def get_fallback_action(obs: Observation, email_id: Optional[str] = None) -> Action:
    """Deterministic fallback to prevent environment crashes."""
    known_ids = [e.id for e in obs.emails]
    if not known_ids:
        # Edge case: no emails available at all? Should not happen if not done.
        return Action(action_type="ignore_email", email_id="unknown")
        
    if email_id and email_id in known_ids:
        return Action(action_type="classify_email", email_id=email_id, category="general_inquiry")
    
    # Priority fallback if email_id missing or invalid
    return Action(action_type="ignore_email", email_id=known_ids[0])


def parse_action(raw: str, obs: Observation) -> Action:
    """Parse LLM output into an Action object via bracket matching, returning fallback on any fail."""
    if not raw:
        return get_fallback_action(obs)

    # 1. Strip markdown code blocks if present
    text = raw.strip()
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 3:
            text = parts[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

    # 2. Bracket Matching for JSON extraction
    start_idx = text.find("{")
    if start_idx == -1:
        return get_fallback_action(obs)
        
    bracket_depth = 0
    end_idx = -1
    for i in range(start_idx, len(text)):
        if text[i] == "{":
            bracket_depth += 1
        elif text[i] == "}":
            bracket_depth -= 1
            if bracket_depth == 0:
                end_idx = i
                break
                
    if end_idx == -1:
        return get_fallback_action(obs)
        
    json_str = text[start_idx:end_idx+1]

    # 3. Attempt JSON parse
    try:
        data = json.loads(json_str)
    except Exception:
        return get_fallback_action(obs)

    # 4. Action Validation
    if not isinstance(data, dict):
        return get_fallback_action(obs)
        
    action_type = data.get("action_type")
    email_id = data.get("email_id")
    
    valid_actions = {
        "classify_email", "set_priority", "draft_reply", 
        "mark_resolved", "escalate_email", "ignore_email"
    }
    
    if action_type not in valid_actions:
        return get_fallback_action(obs, email_id)
        
    if not email_id:
        return get_fallback_action(obs)

    known_ids = {e.id for e in obs.emails}
    if email_id not in known_ids:
        return get_fallback_action(obs)

    # Construct safe final action
    try:
        action = Action(
            action_type=action_type,
            email_id=email_id,
            category=data.get("category"),
            level=data.get("level"),
            text=data.get("text"),
        )
        return action
    except Exception:
        return get_fallback_action(obs, email_id)


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

        fallback_used = False
        error_msg = "None"
        reward = 0.0

        # Build user message from current observation
        user_msg = obs_to_prompt(obs)
        conversation.append({"role": "user", "content": user_msg})

        # Call LLM
        t0 = time.time()
        raw = call_llm(client, conversation)
        step_times.append(time.time() - t0)

        # Parse action (guaranteed to return valid Action via fallback)
        action_before_fallback_check = raw
        action = parse_action(raw, obs)
        
        # Determine if fallback logic activated
        if not raw or raw.find("{") == -1 or getattr(action, "_is_fallback", False) or action.action_type not in raw:
            fallback_used = True
            error_msg = "LLM parse failure bounded to fallback"

        # Apply action inside strict try/except
        try:
            obs, reward, done, info = env.step(action)
            total_reward += reward
        except Exception as e:
            error_msg = f"Env Step Exception: {str(e)}"
            fallback_used = True
            
            # Inject ultimate override to prevent crash blocking
            fallback_action = get_fallback_action(obs)
            try:
                obs, reward, done, info = env.step(fallback_action)
                action = fallback_action
                total_reward += reward
            except Exception as e_inner:
                print(f"  [CRITICAL] Fallback failure at Step {step+1}: {e_inner}")
                break

        # Add assistant reply to conversation
        conversation.append({"role": "assistant", "content": raw if raw else '{"action_type": "ignore_email"}'})

        if verbose:
            print(f"\n[STEP {step+1:03d}]")
            print(f"Action: {action.action_type} ({action.email_id})")
            print(f"Reward: {reward:+.3f}")
            print(f"Fallback: {'YES' if fallback_used else 'NO'}")
            print(f"Error: {error_msg}")

        if done:
            break

    # Guard envelope safely closing environment memory
    try:
        env.close()
    except Exception:
        pass

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

    # Print exact required output formats for final scores
    print()
    for task_id in tasks_to_run:
        score = all_results.get(task_id, {}).get("scores", {}).get("final_score", 0.0)
        print(f"FINAL SCORE ({task_id}): {score:.2f}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(all_results, f, indent=2)
        print(f"\nResults written to: {args.output}")


if __name__ == "__main__":
    main()
