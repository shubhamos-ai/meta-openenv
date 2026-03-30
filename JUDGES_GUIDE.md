# 👨‍⚖️ SHUBHAMOS: Evaluation & Verification Guide

This guide describes how judges and users can verify that the SHUBHAMOS Email Triage Agent is working correctly according to the **OpenEnv** protocol.

---

## 1. Interactive Benchmark Dashboard (Gradio)
The easiest way to verify the agent is via the **Hugging Face Space Index**.
1.  **Open the Space**: Wait for the "Running" status.
2.  **Configuration**: 
    *   Enter your **Hugging Face API Token** (needed to call the Qwen router).
    *   Select a **Simulation Task** (Easy, Medium, or Hard).
3.  **Run**: Click **Run Agent Benchmark 🚀**.
4.  **Verification**: 
    *   You will see a live summary of the agent's actions.
    *   A final **Grade Report** will appear, showing classification accuracy and total rewards.

---

## 2. Startup Health Logs
Hugging Face Space logs provide an automated audit trail of the system's integrity on every boot:
*   **Token Validation**: The container logs will show `HF_TOKEN loaded successfully ✅`.
*   **Inference Test**: It attempts a "Health Check" prompt to verify the LLM router connectivity.
*   **Automated E2E Logs**: Before the server starts, it runs a pre-flight benchmark. Look for the `===== SHUBHAMOS E2E LOG =====` section in the console logs.

---

## 3. Programmatic API Access (OpenEnv)
The agent follows a strict OpenAPI/FastAPI contract. You can test the endpoints manually via the built-in Swagger UI at `/docs`.

### Test Flow:
1.  **Reset**: `POST /reset?task_id=easy` -> Returns initial inbox state.
2.  **Step**: `POST /step` with an action body like:
    ```json
    {
      "action_type": "classify_email",
      "email_id": "email_1",
      "category": "billing_issue"
    }
    ```
3.  **Grade**: `GET /grade` -> Returns real-time metrics for the active session.

---

## 4. Technical Compliance (OpenEnv Requirements)
- **Environment Spec**: View the full OpenEnv definition at `/openenv.yaml`.
- **State Transparency**: All internal ground-truth is available at `/state` (restricted to graders in production, but open here for hackathon transparency).
- **Graceful Failover**: The agent includes a three-tier inference loop (Primary -> Internal Fallback -> Smart Fallback logic) to ensure benchmarks always complete even during API outages.

---

**Project Repositories:**
- **Hugging Face:** [SHUBHAMOS Space](https://huggingface.co/spaces/SHUBHAMOS/meta-pytorch-hackathon)
- **GitHub:** [shubhamos-ai/meta-openenv](https://github.com/shubhamos-ai/meta-openenv)
