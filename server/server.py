"""
SHUBHAMOS: AI Email Operations & Triage Environment
server.py — FastAPI HTTP server wrapping the OpenEnv API

Endpoints:
    POST /reset    — Start a new episode
    POST /step     — Apply one action, get observation + reward
    GET  /state    — Get full internal state (with ground truth)
    GET  /health   — Liveness check
    GET  /grade    — Grade the current episode
    GET  /         — Serve dashboard

Usage:
    uvicorn server:app --host 0.0.0.0 --port 7860
    OR
    python server.py
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel as PydanticBaseModel

from .environment import EmailTriageEnv
from .models import Action
from .reward import RewardEngine
from .tasks import TASKS
from .graders import EasyGrader, MediumGrader, HardGrader

# ── Setup ─────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="SHUBHAMOS: AI Email Operations & Triage Environment",
    description="OpenEnv-compatible email triage environment with reset/step/state API",
    version="1.0.0",
)

# Singleton environment (one episode at a time per server instance)
_env = EmailTriageEnv()
_engine = RewardEngine()
_env.attach_reward_engine(_engine)
_initialized = False

GRADERS = {
    "easy": EasyGrader,
    "medium": MediumGrader,
    "hard": HardGrader,
}

# ── Request / Response models ─────────────────────────────────────────────────

class ResetRequest(PydanticBaseModel):
    task_id: str = "easy"  # easy | medium | hard
    seed: Optional[int] = None
    email_count: Optional[int] = None
    max_steps: Optional[int] = None


class StepRequest(PydanticBaseModel):
    action_type: str
    email_id: str
    category: Optional[str] = None
    level: Optional[str] = None
    text: Optional[str] = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Liveness / readiness probe."""
    return {"status": "ok", "service": "SHUBHAMOS", "version": "1.0.0"}


@app.post("/reset")
async def reset(req: Optional[ResetRequest] = None):
    """
    Start a new episode.

    Uses task presets from openenv.yaml but allows override of seed/email_count/max_steps.
    """
    global _initialized

    # Handle empty body by using defaults
    if req is None:
        req = ResetRequest(task_id="easy")

    if req.task_id not in TASKS:
        raise HTTPException(400, f"Unknown task_id '{req.task_id}'. Choose: easy, medium, hard")

    task_cls = TASKS[req.task_id]
    task_config = task_cls.config()

    # Allow caller to override task defaults
    if req.seed is not None:
        task_config["seed"] = req.seed
    if req.email_count is not None:
        task_config["email_count"] = req.email_count
    if req.max_steps is not None:
        task_config["max_steps"] = req.max_steps

    obs = _env.reset(task_config)
    _initialized = True

    return JSONResponse(content=_obs_to_json(obs))


@app.post("/step")
async def step(req: StepRequest):
    """Apply one action and return (observation, reward, done, info)."""
    if not _initialized:
        raise HTTPException(400, "Call /reset first to start an episode")

    try:
        action = Action(
            action_type=req.action_type,
            email_id=req.email_id,
            category=req.category,
            level=req.level,
            text=req.text,
        )
    except Exception as e:
        raise HTTPException(422, f"Invalid action: {e}")

    try:
        obs, reward, done, info = _env.step(action)
    except RuntimeError as e:
        raise HTTPException(400, str(e))

    return JSONResponse(content={
        "observation": _obs_to_json(obs),
        "reward": reward,
        "done": done,
        "info": info,
    })


@app.get("/state")
async def state():
    """Return full internal state including ground truth labels (for graders)."""
    if not _initialized:
        raise HTTPException(400, "No active episode. Call /reset first.")

    s = _env.state()
    # Serialize via pydantic
    return JSONResponse(content=json.loads(s.model_dump_json()))


@app.get("/grade")
async def grade():
    """Grade the current episode using the deterministic grader."""
    if not _initialized:
        raise HTTPException(400, "No active episode. Call /reset first.")

    s = _env.state()
    if s.task_id not in GRADERS:
        raise HTTPException(400, f"No grader for task_id '{s.task_id}'")

    grader = GRADERS[s.task_id]()
    report = grader.grade(s)
    return JSONResponse(content=report.to_dict())


@app.get("/tasks")
async def list_tasks():
    """List available tasks with their configurations."""
    result = {}
    for tid, cls in TASKS.items():
        result[tid] = {
            "task_id": cls.task_id,
            "difficulty": cls.difficulty,
            "seed": cls.seed,
            "email_count": cls.email_count,
            "max_steps": cls.max_steps,
            "description": cls.description(),
        }
    return JSONResponse(content=result)


@app.get("/openenv.yaml", response_class=HTMLResponse)
async def openenv_yaml():
    """Serve the openenv.yaml spec file."""
    yaml_path = Path(__file__).parent / "openenv.yaml"
    if yaml_path.exists():
        return HTMLResponse(content=yaml_path.read_text(), media_type="text/yaml")
    raise HTTPException(404, "openenv.yaml not found")


# ── Dashboard ─────────────────────────────────────────────────────────────────

DASHBOARD_DIR = Path(__file__).parent / "dashboard"

@app.get("/")
async def root_health():
    """Root health check for Hugging Face Spaces."""
    return {
        "status": "ok",
        "message": "SHUBHAMOS is running 🚀"
    }


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve the minimal monitoring dashboard."""
    html_path = DASHBOARD_DIR / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text())
    return HTMLResponse(content="""
    <html><body>
    <h1>SHUBHAMOS — Email Triage Environment</h1>
    <p>API is running. Dashboard not found.</p>
    <p>Endpoints: <a href="/docs">/docs</a> | <a href="/health">/health</a></p>
    </body></html>
    """)


# ── Serialization helper ──────────────────────────────────────────────────────

def _obs_to_json(obs) -> Dict[str, Any]:
    """Convert Observation to JSON-serializable dict."""
    return json.loads(obs.model_dump_json())


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from .app import start_server
    start_server()
