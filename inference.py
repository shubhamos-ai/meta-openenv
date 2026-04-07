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

import argparse
import json
import os
import sys
import time
import re
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Load secrets from .env file
load_dotenv()

from openai import OpenAI

from server.environment import EmailTriageEnv
from server.models import Action, Observation
from server.reward import RewardEngine
from server.tasks import TASKS
from server.graders import EasyGrader, MediumGrader, HardGrader, PeacefulGrader, ExtremeGrader

# ── AI Client Setup ──────────────────────────────────────────────────────────

# Load default config from environment
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

# Global storage for clients to avoid re-initializing if token hasn't changed.
_primary_client = None
_internal_client = None
_current_token = None

def setup_clients(hf_token: Optional[str] = None):
    """Initializes or updates the OpenAI clients with a specific token."""
    global _primary_client, _internal_client, _current_token
    token = hf_token or HF_TOKEN
    
    if not token and not os.getenv("INTERNAL_AI_KEY"):
        print("  [Setup Error] No HF_TOKEN provided.")
        return None, None
        
    if _primary_client and _current_token == token:
        return _primary_client, _internal_client
        
    _current_token = token
    base_url = os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1")
    model_name = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
    
    _primary_client = OpenAI(base_url=base_url, api_key=token, max_retries=0)
    
    # Internal AI Fallback
    internal_url = os.environ.get("INTERNAL_AI_URL", "https://integrate.api.nvidia.com/v1")
    internal_model = os.environ.get("INTERNAL_AI_MODEL", "qwen/qwen3.5-122b-a10b")
    internal_key = os.environ.get("INTERNAL_AI_KEY", "")
    
    _internal_client = OpenAI(base_url=internal_url, api_key=internal_key, max_retries=0) if internal_key else None
    
    return _primary_client, _internal_client

GRADERS = {
    "peaceful": PeacefulGrader,
    "easy": EasyGrader,
    "medium": MediumGrader,
    "hard": HardGrader,
    "extreme": ExtremeGrader,
}

# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an AI email triage agent.

Your GOAL is to process emails efficiently. 
PRIORitize classify_email for incoming emails before other actions.

You MUST respond ONLY with valid JSON.
No explanations, no markdown, no extra text.

STRICT FORMAT:
{
"action_type": "<one of: classify_email, set_priority, draft_reply, mark_resolved, escalate_email, ignore_email>",
"email_id": "<email_id>",
"category": "<optional>",
"priority": "<optional>"
}

EXAMPLES:
Example 1 (Billing):
Input: billing issue from customer
Output: { "action_type": "classify_email", "email_id": "email_1", "category": "billing" }

Example 2 (Urgency):
Input: urgent complaint
Output: { "action_type": "set_priority", "email_id": "email_2", "priority": "high" }

Return ONLY JSON. 
DO NOT include any explanation. 
DO NOT include text before or after JSON.
"""

# ── Observation → prompt ──────────────────────────────────────────────────────

def obs_to_prompt(obs: Observation, email_id: str, prev_action_result: str = "") -> str:
    """Focuses the LLM on exactly ONE email to maximize precision and avoid confusion."""
    email = next((e for e in obs.emails if e.id == email_id), None)
    if not email:
        return "No emails pending. Respond with {'action_type': 'ignore_email', 'email_id': 'none'}"

    lines = [
        f"=== FOCUS: EMAIL {email.id} ===",
        f"Subject: {email.subject}",
        f"From: {email.sender}",
        f"Current Status: {email.category or 'UNCLASSIFIED'} / {email.priority or 'NONE'}",
        f"Body: {email.body_preview[:250]}",
        "",
        "HISTORY:",
        f"Last action result: {prev_action_result or 'Start of flow'}",
        "",
        "GOAL for this email:",
        "1. If UNCLASSIFIED -> action_type: classify_email (e.g. billing_issue, tech_support)",
        "2. If Priority NONE -> action_type: set_priority (e.g. high, medium, low)",
        "3. If Classified & Prioritized -> action_type: mark_resolved",
        "",
        "Return ONLY JSON. No explanation. No extra text."
    ]
    return "\n".join(lines)


# ── API Health Check ─────────────────────────────────────────────────────────

def handle_rate_limit(provider_name: str) -> None:
    """Requested 429 handling with loasing animation."""
    print(f"\n  [Rate Limit] {provider_name}: Ai got rate limitws")
    print("  Waiting 10 seconds...")
    pass # Removed mock loading for production speed

def check_client_health() -> bool:
    """Run a single test prompt to see if the Primary AI is active."""
    if not _primary_client:
        return False
        
    model_name = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
    print(f"  [Health Check] Testing Primary AI ({model_name}) with JSON Mode...")
    try:
        response = _primary_client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Respond with {'status': 'ok'} in JSON format."}],
            max_tokens=20,
            timeout=10,
            response_format={"type": "json_object"}
        )
        if response.choices[0].message.content:
            print("  [Health Check] Primary AI is HEALTHY ✅")
            return True
    except Exception as e:
        print(f"  [Health Check] Primary AI failed: {str(e)[:80]} ❌")
        return False

# ── LLM call ─────────────────────────────────────────────────────────────────

def _safe_llm_call(client, model, messages, timeout=20):
    """Internal helper to try JSON mode with a fallback to standard completions."""
    try:
        # Final optimization: Strict Token & Temperature Control
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.05, # Ultra-low for consistency
            max_tokens=80,   # Lean JSON only
            timeout=timeout,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        # If response_format is NOT supported, fallback to standard call
        if "response_format" in str(e) or "json_object" in str(e):
             response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.05,
                max_tokens=80,
                timeout=timeout
            )
             return response.choices[0].message.content
        raise e

def call_llm(conversation: List[Dict[str, str]], primary_healthy: bool = True, clients: tuple = (None, None)) -> str:
    """
    Call the LLM with three-tier logic: Primary AI -> Experimental AI (Fallback).
    JSON Mode enforcement included.
    """
    p_client, i_client = clients
    primary_model = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
    internal_model = os.environ.get("INTERNAL_AI_MODEL", "qwen/qwen3.5-122b-a10b")

    # ── TIER 1: Primary AI if healthy ──────────────────────────────────
    if p_client and primary_healthy:
        try:
            content = _safe_llm_call(p_client, primary_model, conversation, timeout=15)
            if content:
                time.sleep(1) # Fast throttle for success
                return content.strip()
        except Exception as e:
            if "429" in str(e):
                handle_rate_limit("Primary AI")
            elif "402" in str(e):
                print("  [Primary Error] Credits depleted (402). Switching to Fallback.")
            else:
                print(f"  [Primary Error] {str(e)[:100]}")

    # ── TIER 2: Secondary AI Fallback (Secret) ───────────────────────────────────
    if i_client:
        try:
            content = _safe_llm_call(i_client, internal_model, conversation, timeout=20)
            if content:
                return content.strip()
        except Exception as e:
            print(f"  [Fallback Error] {str(e)[:80]}")

    # ── TIER 3: Desperation Primary (even if failed health) ──────────────────
    # Only try this if we haven't already tried it in Tier 1
    if p_client and not primary_healthy:
        try:
            content = _safe_llm_call(p_client, primary_model, conversation, timeout=25)
            if content:
                return content.strip()
        except Exception:
            pass

    return ""

def get_fallback_action(obs: Observation, email_id: Optional[str] = None) -> Action:
    """Deterministic SMART fallback logic when LLM fails."""
    if not obs.emails:
        return Action(action_type="ignore_email", email_id="none")
    
    # Try to find target email
    target_id = email_id
    if not target_id:
        # Default to first unresolved email if possible
        target_id = obs.emails[0].id
        
    email = next((e for e in obs.emails if e.id == target_id), obs.emails[0])
    text = (email.subject + " " + email.body_preview).lower()
    
    # Priority Keywords
    is_urgent = any(k in text for k in ["urgent", "asap", "critical", "blocking", "emergency", "immediately"])
    
    # Classification Keywords
    if "billing" in text or "invoice" in text or "payment" in text or "charged" in text:
        return Action(action_type="classify_email", email_id=email.id, category="billing_issue")
    if "issue" in text or "bug" in text or "broken" in text or "not working" in text:
        return Action(action_type="classify_email", email_id=email.id, category="tech_support")
    
    if is_urgent and email.priority != "high":
        return Action(action_type="set_priority", email_id=email.id, level="high")
    
    # Final smart safety: resolve if it looks handled, otherwise classify general
    if email.category and email.priority:
        return Action(action_type="mark_resolved", email_id=email.id)
    
    return Action(action_type="classify_email", email_id=email.id, category="general_inquiry")
    
    # Robust default: classify as general
    return Action(action_type="classify_email", email_id=email.id, category="general_inquiry")

def parse_action(raw: str, obs: Observation) -> Action:
    """Parse LLM output focusing on structured JSON Mode response."""
    print(f"  [DEBUG] RAW MODEL OUTPUT:\n{raw}\n{'-'*40}")
    
    if not raw or "{" not in raw:
        return get_fallback_action(obs)

    try:
        # Try direct load first (ideal for JSON Mode)
        try:
            data = json.loads(raw.strip())
        except json.JSONDecodeError:
            # Simple single-pattern extraction if chatter persists
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if not match: return get_fallback_action(obs)
            data = json.loads(match.group(0))

        if not isinstance(data, dict) or "action_type" not in data:
            # Handle "action" hallucination
            if "action" in data:
                data["action_type"] = data.pop("action")
            else:
                return get_fallback_action(obs)
            
        action_type = data.get("action_type")
        email_id = data.get("email_id")
        
        valid_actions = {
            "classify_email", "set_priority", "draft_reply", 
            "mark_resolved", "escalate_email", "ignore_email"
        }
        
        if action_type not in valid_actions or not email_id:
            return get_fallback_action(obs, email_id)

        known_ids = {e.id for e in obs.emails}
        if email_id not in known_ids:
            return get_fallback_action(obs)

        # Normalization for Category
        cat = data.get("category")
        if cat:
            cat = str(cat).lower()
            if "bill" in cat: cat = "billing_issue"
            elif "urgent" in cat or "complaint" in cat: cat = "urgent_complaint"
            elif "tech" in cat or "support" in cat: cat = "tech_support"
            elif "general" in cat: cat = "general_inquiry"
            elif "spam" in cat: cat = "spam"
            else: cat = "general_inquiry" # fallback safe

        # Normalization for Priority Level
        level = data.get("priority") or data.get("level") or data.get("priority_level")
        if level:
            level = str(level).lower()
            if "high" in level or "urgent" in level or "critical" in level: level = "high"
            elif "med" in level: level = "medium"
            elif "low" in level: level = "low"
            else: level = "unknown"

        action = Action(
            action_type=action_type,
            email_id=email_id,
            category=cat,
            level=level,
            text=data.get("reply_text") or data.get("text") or data.get("reply")
        )
        return action
    except Exception as e:
        print(f"  [Parse Error] {e}")
        return get_fallback_action(obs)


# ── Agent loop ────────────────────────────────────────────────────────────────

def run_agent(task_id: str, hf_token: Optional[str] = None, verbose: bool = True) -> Dict[str, Any]:
    """
    Run one full episode of the email triage agent.

    Returns: grading report dict
    """
    clients = setup_clients(hf_token)
    p_client, i_client = clients
    
    if not p_client:
        return {"error": "AI client not initialized. Check HF_TOKEN."}

    # Step: Check AI Health (User's "Check then Use" request)
    primary_healthy = check_client_health_with_client(p_client)

    task_cls = TASKS[task_id]
    task_config = task_cls.config()

    # Setup environment + reward engine
    env = EmailTriageEnv()
    engine = RewardEngine()
    env.attach_reward_engine(engine)

    obs = env.reset(task_config)

    if verbose:
        model_name_env = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
        print(f"[START] task={task_id} env=shubhamos model={model_name_env}", flush=True)
        print(f"\n{'='*60}")
        print(f"  SHUBHAMOS — Task: {task_id.upper()} | {task_cls.email_count} emails | max {task_cls.max_steps} steps")
        print(f"{'='*60}")

    total_reward = 0.0
    parse_success = 0
    parse_failure = 0
    failure_streak = 0
    last_action_summary = ""
    step_times: List[float] = []
    rewards_list: List[float] = []

    for step in range(task_cls.max_steps):
        # STOP EARLY: All handled?
        pending = [e for e in obs.emails if not (e.resolved or e.escalated or e.ignored)]
        if not pending:
            if verbose: print("  [Early Stop] All emails processed. Ending episode.")
            break

        # TARGET SELECTION: Focus on the first pending email
        target_email = pending[0]
        
        # Build user message (Stateful & Focused)
        user_msg = obs_to_prompt(obs, target_email.id, prev_action_result=last_action_summary)
        
        # FAST FAIL: If LLM is failing repeatedly, switch to pure fallback for this step
        if failure_streak >= 2:
            if verbose: print("  [Fast Fail] Consecutive failures. Reverting to Smart Fallback.")
            action = get_fallback_action(obs, target_email.id)
            setattr(action, "_is_fallback", True)
            raw = "{}" # Dummy
            failure_streak = 0 # reset streak after one fallback
        else:
            conversation = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg}
            ]
            t0 = time.time()
            raw = call_llm(conversation, primary_healthy=primary_healthy, clients=clients)
            step_times.append(time.time() - t0)
            action = parse_action(raw, obs)

        # Trace failure for metrics & streak
        is_llm_failure = not raw or raw == "{}" or getattr(action, "_is_fallback", False) or action.action_type not in raw
        
        if is_llm_failure:
            parse_failure += 1
            failure_streak += 1
            if not getattr(action, "_is_fallback", False): # if parse failed but streak not yet triggered
                 action = get_fallback_action(obs, target_email.id)
        else:
            parse_success += 1
            failure_streak = 0

        # Apply action
        done = False
        error = None
        try:
            obs, reward, done, info = env.step(action)
            total_reward += reward
            last_action_summary = f"Success: {action.action_type} on {action.email_id}"
        except Exception as e:
            error = str(e)[:50].replace('\n', ' ')
            last_action_summary = f"Error: {error}"
            # One last try with fallback
            try:
                action = get_fallback_action(obs, target_email.id)
                obs, reward, done, info = env.step(action)
                total_reward += reward
                error = None
            except Exception as e2:
                reward = 0.0
                error = str(e2)[:50].replace('\n', ' ')
                done = True

        rewards_list.append(reward)

        if verbose:
            done_val = "true" if done else "false"
            error_val = "null" if not error else f"'{error}'"
            print(f"[STEP] step={step+1} action={action.action_type} reward={reward:.2f} done={done_val} error={error_val}", flush=True)
            print(f"  Step {step+1:02d} | Action: {action.action_type} | Reward: {reward:+.2f} | Fallback: {'Yes' if is_llm_failure else 'No'}")

        if done: break
        time.sleep(2) # Key protection

    # Final Output...
    final_state = env.state()
    report = GRADERS[task_id]().grade(final_state)
    
    result = report.to_dict()
    score = result.get("scores", {}).get("final_score", 0.0)
    
    if verbose:
        rewards_str = ",".join(f"{r:.2f}" for r in rewards_list)
        success_val = "true" if score > 0 else "false"
        steps_taken = len(rewards_list)
        print(f"[END] success={success_val} steps={steps_taken} score={score:.3f} rewards={rewards_str}", flush=True)

    result["total_reward"] = round(total_reward, 4)
    return result

def check_client_health_with_client(client) -> bool:
    """Run a single test prompt to see if the client is active."""
    if not client: return False
    model_name = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
    print(f"  [Health Check] Testing AI ({model_name}) with JSON Mode...")
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Respond with {'status': 'ok'} in JSON format."}],
            max_tokens=20,
            timeout=10,
            response_format={"type": "json_object"}
        )
        if response.choices[0].message.content:
            print("  [Health Check] Provider is HEALTHY ✅")
            return True
    except Exception as e:
        print(f"  [Health Check] AI failed: {str(e)[:80]} ❌")
        return False
    return False


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="SHUBHAMOS Email Triage Agent — runs LLM agent against environment"
    )
    parser.add_argument(
        "--task",
        choices=["peaceful", "easy", "medium", "hard", "extreme", "all"],
        default="all",
        help="Task difficulty to run (default: all — runs all 5 tasks)",
    )
    parser.add_argument("--verbose", action="store_true", default=True)
    parser.add_argument("--quiet", action="store_true", help="Suppress step-by-step output")
    parser.add_argument("--output", type=str, help="Write results JSON to this file")
    args = parser.parse_args()

    p_client, i_client = setup_clients()
    if not p_client and not i_client:
        print("ERROR: No AI clients configured. Check your .env file.")
        sys.exit(1)

    # Use the global clients initialized above
    verbose = not args.quiet
    
    tasks_to_run = ["peaceful", "easy", "medium", "hard", "extreme"] if args.task == "all" else [args.task]
    all_results: Dict[str, Any] = {}

    for task_id in tasks_to_run:
        result = run_agent(task_id, hf_token=None, verbose=verbose)
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
