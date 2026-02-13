"""
Inference Script for Code README Writer

Generates READMEs using both the base model and fine-tuned model
to produce side-by-side before/after comparisons.

Usage:
    # Compare base vs fine-tuned on a local repo
    python scripts/inference.py \
        --repo_path /path/to/repo \
        --adapter_path outputs/readme-writer-tinyllama/final_adapter

    # Compare on a GitHub repo
    python scripts/inference.py \
        --github_repo owner/repo \
        --adapter_path outputs/readme-writer-tinyllama/final_adapter

    # Base model only (no adapter)
    python scripts/inference.py \
        --repo_path /path/to/repo \
        --base_only
"""

import argparse
import json
import os
import sys
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


# Reuse constants from prepare_data
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs",
    ".cpp", ".c", ".h", ".rb", ".php", ".swift", ".kt", ".scala",
    ".cs", ".r", ".jl", ".lua", ".sh", ".bash", ".zsh",
}

IMPORTANT_FILES = {
    "setup.py", "setup.cfg", "pyproject.toml", "package.json",
    "cargo.toml", "go.mod", "build.gradle", "pom.xml",
    "makefile", "dockerfile", "docker-compose.yml",
    "requirements.txt", "gemfile", ".env.example",
}

IGNORE_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    ".eggs", "*.egg-info", "dist", "build", ".tox", ".mypy_cache",
    ".pytest_cache", ".next", "target", "vendor",
}

MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
MAX_FILE_CHARS = 1500
MAX_TOTAL_CODE_CHARS = 6000


def scan_local_repo(repo_path: str) -> tuple[str, str, str]:
    """Scan a local repository and extract structure + key files."""
    repo_path = Path(repo_path).resolve()
    repo_name = repo_path.name

    # Build file tree
    all_files = []
    for root, dirs, files in os.walk(repo_path):
        # Filter ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]
        for f in files:
            full = Path(root) / f
            rel = full.relative_to(repo_path)
            all_files.append(str(rel))

    all_files.sort()
    if len(all_files) > 80:
        file_tree = "\n".join(all_files[:80]) + "\n... (truncated)"
    else:
        file_tree = "\n".join(all_files)

    # Select key files
    key_files = []
    for f in all_files:
        basename = os.path.basename(f).lower()
        if basename in IMPORTANT_FILES:
            key_files.append(f)

    for f in all_files:
        ext = os.path.splitext(f)[1].lower()
        if ext in CODE_EXTENSIONS and f.count("/") <= 2:
            if f not in key_files:
                key_files.append(f)

    key_files = key_files[:10]

    # Read key files
    snippets = []
    total_chars = 0
    for f in key_files:
        if total_chars >= MAX_TOTAL_CODE_CHARS:
            break
        full_path = repo_path / f
        try:
            content = full_path.read_text(errors="replace")[:MAX_FILE_CHARS]
            total_chars += len(content)
            snippets.append(f"--- {f} ---\n{content}")
        except (OSError, UnicodeDecodeError):
            continue

    code_snippets = "\n\n".join(snippets)
    return repo_name, file_tree, code_snippets


def scan_github_repo(owner_repo: str, token: str | None = None) -> tuple[str, str, str]:
    """Fetch repository info from GitHub API."""
    import requests

    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    owner, repo = owner_repo.split("/")

    # Get tree
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    tree = resp.json().get("tree", [])

    # Build file tree
    paths = sorted(
        item["path"] for item in tree
        if item["type"] in ("blob", "tree")
        and not any(part.startswith(".") for part in item["path"].split("/"))
        and "node_modules" not in item["path"]
        and "__pycache__" not in item["path"]
    )
    if len(paths) > 80:
        file_tree = "\n".join(paths[:80]) + "\n... (truncated)"
    else:
        file_tree = "\n".join(paths)

    # Select key files
    key_files = []
    for item in tree:
        if item["type"] == "blob":
            basename = os.path.basename(item["path"]).lower()
            if basename in IMPORTANT_FILES:
                key_files.append(item["path"])

    for item in tree:
        if item["type"] != "blob":
            continue
        ext = os.path.splitext(item["path"])[1].lower()
        if ext in CODE_EXTENSIONS and item["path"].count("/") <= 2:
            if item["path"] not in key_files:
                key_files.append(item["path"])

    key_files = key_files[:10]

    # Download key files
    snippets = []
    total_chars = 0
    for path in key_files:
        if total_chars >= MAX_TOTAL_CODE_CHARS:
            break
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{path}"
        resp = requests.get(raw_url, headers=headers)
        if resp.status_code == 200:
            content = resp.text[:MAX_FILE_CHARS]
            total_chars += len(content)
            snippets.append(f"--- {path} ---\n{content}")

    code_snippets = "\n\n".join(snippets)
    return owner_repo, file_tree, code_snippets


def build_prompt(repo_name: str, file_tree: str, code_snippets: str) -> str:
    """Build the inference prompt (without the assistant response)."""
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


def load_base_model():
    """Load the base TinyLlama model with 4-bit quantization."""
    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=quant_config,
        device_map="auto",
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    return model, tokenizer


def load_finetuned_model(adapter_path: str):
    """Load the base model with the fine-tuned LoRA adapter merged."""
    model, tokenizer = load_base_model()
    model = PeftModel.from_pretrained(model, adapter_path)
    return model, tokenizer


def generate_readme(
    model,
    tokenizer,
    prompt: str,
    max_new_tokens: int = 1024,
    temperature: float = 0.7,
    top_p: float = 0.9,
    repetition_penalty: float = 1.15,
) -> str:
    """Generate a README from the given prompt."""
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            repetition_penalty=repetition_penalty,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )

    # Decode only the generated tokens
    generated = outputs[0][inputs["input_ids"].shape[1]:]
    text = tokenizer.decode(generated, skip_special_tokens=True)
    return text.strip()


def compare_outputs(
    repo_name: str,
    file_tree: str,
    code_snippets: str,
    adapter_path: str | None = None,
    output_dir: str = "outputs/comparisons",
) -> dict:
    """Generate and compare base vs fine-tuned outputs."""
    prompt = build_prompt(repo_name, file_tree, code_snippets)

    print("Loading base model...")
    base_model, tokenizer = load_base_model()

    print("Generating README with base model...")
    base_output = generate_readme(base_model, tokenizer, prompt)
    print(f"  Base model output: {len(base_output)} chars")

    finetuned_output = None
    if adapter_path:
        print("Loading fine-tuned adapter...")
        ft_model = PeftModel.from_pretrained(base_model, adapter_path)

        print("Generating README with fine-tuned model...")
        finetuned_output = generate_readme(ft_model, tokenizer, prompt)
        print(f"  Fine-tuned output: {len(finetuned_output)} chars")

        # Cleanup
        del ft_model
    del base_model
    torch.cuda.empty_cache()

    # Save comparison
    os.makedirs(output_dir, exist_ok=True)
    safe_name = repo_name.replace("/", "_")

    result = {
        "repo_name": repo_name,
        "base_model": MODEL_NAME,
        "base_output": base_output,
    }
    if finetuned_output:
        result["finetuned_output"] = finetuned_output

    # Save JSON
    json_path = os.path.join(output_dir, f"{safe_name}_comparison.json")
    with open(json_path, "w") as f:
        json.dump(result, f, indent=2)

    # Save readable markdown comparison
    md_path = os.path.join(output_dir, f"{safe_name}_comparison.md")
    with open(md_path, "w") as f:
        f.write(f"# README Comparison: {repo_name}\n\n")
        f.write("---\n\n")
        f.write(f"## Before (Base Model: {MODEL_NAME})\n\n")
        f.write(base_output)
        f.write("\n\n---\n\n")
        if finetuned_output:
            f.write("## After (Fine-tuned with SFT + QLoRA)\n\n")
            f.write(finetuned_output)
        f.write("\n")

    print(f"\nComparison saved to: {md_path}")
    return result


def main():
    parser = argparse.ArgumentParser(description="Generate READMEs with before/after comparison")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--repo_path", type=str, help="Path to local repository")
    group.add_argument("--github_repo", type=str, help="GitHub repo (owner/repo)")

    parser.add_argument("--adapter_path", type=str, default=None,
                        help="Path to fine-tuned LoRA adapter")
    parser.add_argument("--base_only", action="store_true",
                        help="Only run base model (no fine-tuned comparison)")
    parser.add_argument("--output_dir", type=str, default="outputs/comparisons",
                        help="Directory to save comparison outputs")
    parser.add_argument("--max_new_tokens", type=int, default=1024)
    parser.add_argument("--temperature", type=float, default=0.7)
    args = parser.parse_args()

    # Get repo info
    if args.repo_path:
        repo_name, file_tree, code_snippets = scan_local_repo(args.repo_path)
    else:
        token = os.environ.get("GITHUB_TOKEN")
        repo_name, file_tree, code_snippets = scan_github_repo(args.github_repo, token)

    print(f"Repository: {repo_name}")
    print(f"File tree entries: {len(file_tree.splitlines())}")
    print(f"Code snippet length: {len(code_snippets)} chars")
    print()

    adapter_path = None if args.base_only else args.adapter_path
    compare_outputs(repo_name, file_tree, code_snippets, adapter_path, args.output_dir)


if __name__ == "__main__":
    main()
