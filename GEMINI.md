<!-- GSD:project-start source:PROJECT.md -->
## Project

**SHUBHAMOS: AI Email Operations & Triage Environment**

A production-grade OpenEnv-compatible environment that simulates real-world email inbox management workflows. AI agents interact via `step()`, `reset()`, and `state()` APIs to classify, prioritize, respond to, and resolve emails efficiently. Built for a competitive hackathon, this environment evaluates agent performance on operational tasks like customer support triage, enterprise email handling, and workflow automation.

**Core Value:** **AI agents can be meaningfully evaluated on real-world email operations** — the environment must produce dense reward signals, deterministic grading, and reproducible scores across easy/medium/hard difficulty tiers.

### Constraints

- **Tech stack**: Python, Pydantic, OpenAI SDK — per OpenEnv spec and hackathon rules
- **Deployment**: Docker on Hugging Face Spaces — per hackathon requirements
- **Performance**: 2 vCPU, 8GB RAM, < 20 min inference — hard infra limits
- **Reproducibility**: Fixed seeds, deterministic graders — required for evaluation
- **API**: OpenAI-compatible client via HF Router — no direct NVIDIA SDK
<!-- GSD:project-end -->

<!-- GSD:stack-start source:STACK.md -->
## Technology Stack

Technology stack not yet documented. Will populate after codebase mapping or first phase.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
