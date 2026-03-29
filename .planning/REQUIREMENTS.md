# Requirements: SHUBHAMOS

## v1.1 — Integration, Robustness, and Submission Hardening

| ID | Description | Phase | Status |
|----|-------------|-------|--------|
| **REQ-700** | **Robust LLM Output Handling:** Implement a safe JSON parser to strip markdown blocks (```json) and extra text. | 07 | Not Started |
| **REQ-701** | **LLM Fallback Action:** If parsing fails, return a safe default action (e.g., ignore or classify as general). Inference script must never crash on bad output. | 07 | Not Started |
| **REQ-702** | **API Resiliency Layer:** Add a retry mechanism for API calls (2-3 retries) with exponential backoff handling timeouts, rate limits, and empty responses. | 07 | Not Started |
| **REQ-703** | **Safe Inference Loop:** Add max step guards and exception handling around `step()`. Ensure loop completes and closes cleanly. | 07 | Not Started |
| **REQ-800** | **End-to-End Execution:** Run the full episode for "easy" and "medium" tasks to confirm no crashes and final bounded scores (0.0-1.0). | 08 | Not Started |
| **REQ-801** | **Detailed Validated Logging:** Log all actions taken, rewards per step, and final episode scores. | 08 | Not Started |
| **REQ-900** | **HF Space Deployment:** Push the project to Hugging Face Spaces (Docker) with API_BASE_URL, MODEL_NAME, and HF_TOKEN variables. | 09 | Not Started |
| **REQ-901** | **Deployment Validation:** Verify container builds correctly and the API responds to `/reset` from the live Hugging Face Space. | 09 | Not Started |

**Success Criteria:**
- Full E2E run succeeds reliably.
- No runtime crashes occur under any prompt condition.
- Deployment works unconditionally on Hugging Face.
- System is 100% safe for automated evaluation via Hackathon Judges.
