"""
Evaluation Script for Code README Writer

Computes ROUGE and structural metrics comparing generated READMEs
against ground-truth references from the held-out test set.

Usage:
    python scripts/evaluate.py \
        --adapter_path outputs/readme-writer-tinyllama/final_adapter \
        --data_dir data/ \
        --num_samples 100
"""

import argparse
import json
import os
import re
from collections import Counter

import torch
from peft import PeftModel
from rouge_score import rouge_scorer
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"


def load_model(adapter_path: str | None = None):
    """Load base or fine-tuned model."""
    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, quantization_config=quant_config,
        device_map="auto", trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token

    if adapter_path:
        model = PeftModel.from_pretrained(model, adapter_path)

    return model, tokenizer


def build_prompt(example: dict) -> str:
    return (
        "<|system|>\n"
        "You are a technical writer that generates comprehensive README.md files "
        "for code repositories. Given the repository structure and code contents, "
        "write a clear, well-structured README.</s>\n"
        "<|user|>\n"
        "Generate a README.md for the following repository:\n\n"
        f"Repository name: {example['repo_name']}\n\n"
        f"File structure:\n{example['file_tree']}\n\n"
        f"Key files:\n{example['code_snippets']}</s>\n"
        "<|assistant|>\n"
    )


def generate(model, tokenizer, prompt: str, max_new_tokens: int = 1024) -> str:
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=max_new_tokens,
            temperature=0.7, top_p=0.9, repetition_penalty=1.15,
            do_sample=True, pad_token_id=tokenizer.eos_token_id,
        )
    generated = outputs[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True).strip()


def structural_score(text: str) -> dict:
    """Evaluate structural quality of a generated README."""
    lines = text.split("\n")
    headings = [l for l in lines if l.strip().startswith("#")]
    code_blocks = len(re.findall(r"```", text)) // 2
    has_install = bool(re.search(r"(?i)(install|setup|getting.started)", text))
    has_usage = bool(re.search(r"(?i)(usage|how.to.use|example|quick.start)", text))
    has_description = len(text) > 100
    bullet_points = len([l for l in lines if l.strip().startswith(("-", "*", "•"))])

    return {
        "num_headings": len(headings),
        "num_code_blocks": code_blocks,
        "has_install_section": has_install,
        "has_usage_section": has_usage,
        "has_description": has_description,
        "num_bullet_points": bullet_points,
        "total_length": len(text),
        "total_lines": len(lines),
    }


def compute_structural_aggregate(scores: list[dict]) -> dict:
    """Aggregate structural scores across examples."""
    n = len(scores)
    return {
        "avg_headings": sum(s["num_headings"] for s in scores) / n,
        "avg_code_blocks": sum(s["num_code_blocks"] for s in scores) / n,
        "pct_has_install": sum(s["has_install_section"] for s in scores) / n * 100,
        "pct_has_usage": sum(s["has_usage_section"] for s in scores) / n * 100,
        "pct_has_description": sum(s["has_description"] for s in scores) / n * 100,
        "avg_bullet_points": sum(s["num_bullet_points"] for s in scores) / n,
        "avg_length": sum(s["total_length"] for s in scores) / n,
        "avg_lines": sum(s["total_lines"] for s in scores) / n,
    }


def evaluate(
    adapter_path: str | None,
    data_dir: str,
    num_samples: int,
    output_dir: str,
    label: str = "finetuned",
):
    """Run full evaluation pipeline."""
    # Load test data
    data_path = os.path.join(data_dir, "readme_dataset.jsonl")
    examples = []
    with open(data_path) as f:
        for line in f:
            examples.append(json.loads(line.strip()))

    # Use last N as test set (matching the train split)
    split_idx = int(len(examples) * 0.9)
    test_examples = examples[split_idx:]
    if len(test_examples) > num_samples:
        test_examples = test_examples[:num_samples]

    print(f"Evaluating {label} model on {len(test_examples)} examples...")

    # Load model
    model, tokenizer = load_model(adapter_path)

    # Score
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    rouge_scores = {"rouge1": [], "rouge2": [], "rougeL": []}
    struct_scores = []
    results = []

    for example in tqdm(test_examples, desc=f"Evaluating ({label})"):
        prompt = build_prompt(example)
        generated = generate(model, tokenizer, prompt)
        reference = example["readme_content"]

        # ROUGE
        scores = scorer.score(reference, generated)
        for key in rouge_scores:
            rouge_scores[key].append(scores[key].fmeasure)

        # Structural
        s_score = structural_score(generated)
        struct_scores.append(s_score)

        results.append({
            "repo_name": example["repo_name"],
            "generated": generated,
            "reference": reference,
            "rouge1": scores["rouge1"].fmeasure,
            "rouge2": scores["rouge2"].fmeasure,
            "rougeL": scores["rougeL"].fmeasure,
            "structural": s_score,
        })

    # Aggregate
    avg_rouge = {k: sum(v) / len(v) for k, v in rouge_scores.items()}
    struct_agg = compute_structural_aggregate(struct_scores)

    # Reference structural scores for comparison
    ref_struct = []
    for ex in test_examples:
        ref_struct.append(structural_score(ex["readme_content"]))
    ref_struct_agg = compute_structural_aggregate(ref_struct)

    summary = {
        "label": label,
        "model": MODEL_NAME,
        "adapter": adapter_path,
        "num_samples": len(test_examples),
        "rouge": avg_rouge,
        "structural": struct_agg,
        "reference_structural": ref_struct_agg,
    }

    # Save
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, f"eval_{label}.json"), "w") as f:
        json.dump(summary, f, indent=2)
    with open(os.path.join(output_dir, f"eval_{label}_details.json"), "w") as f:
        json.dump(results, f, indent=2)

    # Print results
    print(f"\n{'='*50}")
    print(f"Evaluation Results ({label})")
    print(f"{'='*50}")
    print(f"ROUGE-1: {avg_rouge['rouge1']:.4f}")
    print(f"ROUGE-2: {avg_rouge['rouge2']:.4f}")
    print(f"ROUGE-L: {avg_rouge['rougeL']:.4f}")
    print(f"\nStructural Metrics (generated):")
    for k, v in struct_agg.items():
        print(f"  {k}: {v:.2f}")
    print(f"\nStructural Metrics (reference):")
    for k, v in ref_struct_agg.items():
        print(f"  {k}: {v:.2f}")

    return summary


def main():
    parser = argparse.ArgumentParser(description="Evaluate README generation quality")
    parser.add_argument("--adapter_path", type=str, default=None,
                        help="Path to LoRA adapter (omit for base model)")
    parser.add_argument("--data_dir", type=str, default="data")
    parser.add_argument("--num_samples", type=int, default=100)
    parser.add_argument("--output_dir", type=str, default="outputs/eval")
    args = parser.parse_args()

    label = "finetuned" if args.adapter_path else "base"
    evaluate(args.adapter_path, args.data_dir, args.num_samples, args.output_dir, label)


if __name__ == "__main__":
    main()
