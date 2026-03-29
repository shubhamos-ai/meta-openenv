---
status: planned
description: Phase 5 Context reflecting Dockerfile dependencies and README specification mapping.
---

# Phase 5 Context: Dockerfile & README

## Domain Context
The project needs to be deployed via Docker to a Hugging Face Space for hackathon submissions. Additionally, all core OpenEnv schemas must be transparently documented in a public README for agents to test against.

## Decisions Made
- **D-50 [Docker Configuration]**: The environment runs via a FastAPI container exposing `0.0.0.0` port `$PORT` (default 7860 mapping Hugging Face Spaces).
- **D-51 [Server Layer]**: `server.py` implements the requisite API hooks for `# OENV-*` functionality required by Docker configuration boundaries.
- **D-52 [README spec]**: The README outlines Action dispatch loops along with the dense reward configurations detailed in Phase 2.

## Canonical References
- `.planning/REQUIREMENTS.md`

## Code Context
- `Dockerfile`
- `README.md`
- `server.py`

## Specifics & Edge Cases
None.

## Deferred Ideas
None.
