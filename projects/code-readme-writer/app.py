"""
Gradio Demo App for Code README Writer

Interactive web interface that generates README files from repository
information, with side-by-side base vs fine-tuned model comparison.

Usage:
    python app.py --adapter_path outputs/readme-writer-tinyllama/final_adapter
    python app.py --share  # Create public Gradio link
"""

import argparse
import os

import gradio as gr
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# Global model references
base_model = None
ft_model = None
tokenizer = None


def load_models(adapter_path: str | None = None):
    """Load both base and fine-tuned models."""
    global base_model, ft_model, tokenizer

    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )

    print("Loading base model...")
    base_model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, quantization_config=quant_config,
        device_map="auto", trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token

    if adapter_path and os.path.exists(adapter_path):
        print("Loading fine-tuned adapter...")
        ft_model = PeftModel.from_pretrained(base_model, adapter_path)
        print("Fine-tuned model loaded.")
    else:
        print("No adapter path provided. Only base model available.")


def build_prompt(repo_name: str, file_tree: str, code_snippets: str) -> str:
    return (
        "<|system|>\n"
        "You are a technical writer that generates comprehensive README.md files "
        "for code repositories. Given the repository structure and code contents, "
        "write a clear, well-structured README.</s>\n"
        "<|user|>\n"
        "Generate a README.md for the following repository:\n\n"
        f"Repository name: {repo_name}\n\n"
        f"File structure:\n{file_tree}\n\n"
        f"Key files:\n{code_snippets}</s>\n"
        "<|assistant|>\n"
    )


def generate(model, prompt: str, max_tokens: int, temperature: float) -> str:
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=max_tokens,
            temperature=temperature, top_p=0.9,
            repetition_penalty=1.15, do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    generated = outputs[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True).strip()


def generate_readmes(
    repo_name: str,
    file_tree: str,
    code_snippets: str,
    max_tokens: int,
    temperature: float,
):
    """Generate README with both base and fine-tuned models."""
    if not repo_name.strip():
        return "Please provide a repository name.", ""

    prompt = build_prompt(repo_name, file_tree, code_snippets)

    # Base model output
    base_output = generate(base_model, prompt, int(max_tokens), temperature)

    # Fine-tuned output
    if ft_model is not None:
        ft_output = generate(ft_model, prompt, int(max_tokens), temperature)
    else:
        ft_output = "_Fine-tuned model not loaded. Provide --adapter_path to enable._"

    return base_output, ft_output


# Example repository for demo
EXAMPLE_REPO_NAME = "fastapi-todo-app"
EXAMPLE_FILE_TREE = """app/
app/__init__.py
app/main.py
app/models.py
app/database.py
app/schemas.py
app/routers/
app/routers/__init__.py
app/routers/todos.py
app/routers/users.py
tests/
tests/test_todos.py
tests/test_users.py
requirements.txt
Dockerfile
docker-compose.yml
.env.example
alembic.ini
alembic/
alembic/versions/"""

EXAMPLE_CODE = """--- requirements.txt ---
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.2
alembic==1.13.0
python-jose==3.3.0
passlib==1.7.4
python-multipart==0.0.6
pytest==7.4.3
httpx==0.25.2

--- app/main.py ---
from fastapi import FastAPI
from app.routers import todos, users
from app.database import engine
from app import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo API", version="1.0.0")
app.include_router(todos.router, prefix="/api/todos", tags=["todos"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

@app.get("/health")
def health_check():
    return {"status": "healthy"}

--- app/models.py ---
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    todos = relationship("Todo", back_populates="owner")

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="todos")"""


def create_demo():
    """Build the Gradio interface."""
    with gr.Blocks(
        title="Code README Writer - Before/After Demo",
        theme=gr.themes.Soft(),
    ) as demo:
        gr.Markdown(
            "# Code README Writer\n"
            "### SFT Fine-tuned TinyLlama for README Generation\n"
            "Enter repository details below to generate a README. "
            "Compare the **base model** output vs the **fine-tuned** output side by side."
        )

        with gr.Row():
            with gr.Column():
                repo_name = gr.Textbox(
                    label="Repository Name",
                    placeholder="e.g., my-awesome-project",
                    value=EXAMPLE_REPO_NAME,
                )
                file_tree = gr.Textbox(
                    label="File Structure",
                    placeholder="Paste the file tree here...",
                    value=EXAMPLE_FILE_TREE,
                    lines=12,
                )
                code_snippets = gr.Textbox(
                    label="Key Code Files",
                    placeholder="Paste key file contents here...",
                    value=EXAMPLE_CODE,
                    lines=15,
                )
                with gr.Row():
                    max_tokens = gr.Slider(
                        minimum=128, maximum=2048, value=1024, step=64,
                        label="Max Tokens",
                    )
                    temperature = gr.Slider(
                        minimum=0.1, maximum=1.5, value=0.7, step=0.1,
                        label="Temperature",
                    )
                generate_btn = gr.Button("Generate README", variant="primary")

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Before (Base TinyLlama-1.1B)")
                base_output = gr.Markdown(label="Base Model Output")
            with gr.Column():
                gr.Markdown("### After (SFT Fine-tuned)")
                ft_output = gr.Markdown(label="Fine-tuned Output")

        generate_btn.click(
            fn=generate_readmes,
            inputs=[repo_name, file_tree, code_snippets, max_tokens, temperature],
            outputs=[base_output, ft_output],
        )

    return demo


def main():
    parser = argparse.ArgumentParser(description="Code README Writer Demo")
    parser.add_argument("--adapter_path", type=str, default=None,
                        help="Path to fine-tuned LoRA adapter")
    parser.add_argument("--share", action="store_true",
                        help="Create a public Gradio link")
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()

    load_models(args.adapter_path)
    demo = create_demo()
    demo.launch(server_port=args.port, share=args.share)


if __name__ == "__main__":
    main()
