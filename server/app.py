import gradio as gr
import os
import json
import pandas as pd
from .server import app as fastapi_app
from .tasks import TASKS
from inference import run_agent
from fastapi.middleware.cors import CORSMiddleware

# ── Gradio Logic ──────────────────────────────────────────────────────────────

def run_benchmark_ui(hf_token, task_id):
    """Bridge for Gradio to call the inference agent."""
    if not hf_token:
        # Default to environment token if empty
        hf_token = os.environ.get("HF_TOKEN", "")
        if not hf_token:
            return "Error: Please provide a Hugging Face Token.", None
    
    try:
        # Set token in environment for backend stability
        os.environ["HF_TOKEN"] = hf_token
        
        # Run agent
        result = run_agent(task_id, hf_token=hf_token, verbose=False)
        
        if "error" in result:
            return f"Error: {result['error']}", None
            
        # Format results for display
        scores = result.get("scores", {})
        df_data = {
            "Metric": ["Final Score", "Classification Accuracy", "Priority Accuracy", "Resolution Rate", "Urgent Handling"],
            "Value": [
                f"{scores.get('final_score', 0):.3f}",
                f"{scores.get('classification_accuracy', 0):.3f}",
                f"{scores.get('priority_accuracy', 0):.3f}",
                f"{scores.get('resolution_rate', 0):.3f}",
                f"{scores.get('urgent_handling', 0):.3f}"
            ]
        }
        df = pd.DataFrame(df_data)
        
        summary = f"### Benchmark Complete! 🚀\n**Status:** {'PASS ✅' if result.get('passed') else 'FAIL ❌'}\n**Total Reward:** {result.get('total_reward', 0):.3f}"
        
        return summary, df
        
    except Exception as e:
        return f"Fatal Error: {str(e)}", None

# ── Build UI ──────────────────────────────────────────────────────────────────

with gr.Blocks(title="SHUBHAMOS: AI Email Triage Benchmarking") as demo:
    gr.Markdown("# 📈 SHUBHAMOS Benchmark Controller")
    gr.Markdown("Test your AI agent's email triage capabilities using the OpenEnv protocol.")
    
    with gr.Row():
        with gr.Column(scale=1):
            token_input = gr.Textbox(
                label="Hugging Face Token", 
                placeholder="hf_...", 
                type="password",
                info="Required to call the AI Router (Qwen/Qwen2.5-72B-Instruct)."
            )
            task_select = gr.Radio(
                choices=["easy", "medium", "hard"], 
                value="easy", 
                label="Simulation Task"
            )
            run_btn = gr.Button("Run Agent Benchmark 🚀", variant="primary")
            gr.Markdown("---")
            gr.Markdown("### API Endpoints")
            gr.Markdown("- [FastAPI Docs](/docs)")
            gr.Markdown("- [Environment Spec](/openenv.yaml)")
            gr.Markdown("- [Dashboard](/dashboard)")

        with gr.Column(scale=2):
            result_summary = gr.Markdown("### Results will appear here...")
            result_table = gr.Dataframe(label="Performance Metrics")

    run_btn.click(
        fn=run_benchmark_ui,
        inputs=[token_input, task_select],
        outputs=[result_summary, result_table]
    )

# ── Mount & Launch ────────────────────────────────────────────────────────────

# Combine FastAPI and Gradio
app = gr.mount_gradio_app(fastapi_app, demo, path="/")

def start_server():
    """CLI entry point for the OpenEnv 'server' command."""
    import uvicorn
    import threading
    import time
    
    # Start background diagnostics to avoid blocking uvicorn
    def run_diagnostics():
        time.sleep(5)
        try:
            from .health_check import run_preflight_checks
            print("\n[Diagnostic] Running background system check...")
            run_preflight_checks()
        except Exception as e:
            print(f"\n[Diagnostic] Background check failed: {e}")

    diag_thread = threading.Thread(target=run_diagnostics, daemon=True)
    diag_thread.start()

    port = int(os.environ.get("PORT", 7860))
    # Note: Use string import to avoid bootstrap issues
    uvicorn.run("server.app:app", host="0.0.0.0", port=port)

if __name__ == "__main__":
    start_server()
