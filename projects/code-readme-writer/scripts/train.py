"""
SFT Training Script for Code README Writer

Fine-tunes TinyLlama-1.1B with QLoRA to generate README.md files
from repository structure and code snippets.

Usage:
    python scripts/train.py --config configs/training_config.yaml

    # On Google Colab (free tier T4 GPU):
    python scripts/train.py --config configs/training_config.yaml \
        --per_device_train_batch_size 2 \
        --gradient_accumulation_steps 8
"""

import argparse
import json
import os
from pathlib import Path

import torch
import yaml
from datasets import Dataset, DatasetDict
from peft import LoraConfig, TaskType, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM


def load_config(config_path: str) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_dataset_from_jsonl(data_dir: str, train_split: float = 0.9) -> DatasetDict:
    """Load the JSONL dataset and split into train/eval."""
    data_path = os.path.join(data_dir, "readme_dataset.jsonl")
    examples = []
    with open(data_path) as f:
        for line in f:
            examples.append(json.loads(line.strip()))

    dataset = Dataset.from_list(examples)
    split = dataset.train_test_split(test_size=1 - train_split, seed=42)
    return DatasetDict({"train": split["train"], "test": split["test"]})


def format_prompt(example: dict, template: str) -> str:
    """Format a single example using the prompt template."""
    return template.format(
        repo_name=example["repo_name"],
        file_tree=example["file_tree"],
        code_snippets=example["code_snippets"],
        readme_content=example["readme_content"],
    )


def create_formatting_function(template: str):
    """Return a formatting function for the SFT trainer."""
    def formatting_func(examples):
        outputs = []
        for i in range(len(examples["repo_name"])):
            text = template.format(
                repo_name=examples["repo_name"][i],
                file_tree=examples["file_tree"][i],
                code_snippets=examples["code_snippets"][i],
                readme_content=examples["readme_content"][i],
            )
            outputs.append(text)
        return outputs
    return formatting_func


def setup_model_and_tokenizer(config: dict):
    """Load and configure the model with QLoRA quantization."""
    model_name = config["model"]["name"]

    # Quantization config for 4-bit QLoRA
    quant_config = BitsAndBytesConfig(
        load_in_4bit=config["quantization"]["load_in_4bit"],
        bnb_4bit_compute_dtype=getattr(torch, config["quantization"]["bnb_4bit_compute_dtype"]),
        bnb_4bit_quant_type=config["quantization"]["bnb_4bit_quant_type"],
        bnb_4bit_use_double_quant=config["quantization"]["bnb_4bit_use_double_quant"],
    )

    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=quant_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(model)

    # LoRA config
    lora_config = LoraConfig(
        r=config["lora"]["r"],
        lora_alpha=config["lora"]["lora_alpha"],
        lora_dropout=config["lora"]["lora_dropout"],
        target_modules=config["lora"]["target_modules"],
        bias=config["lora"]["bias"],
        task_type=TaskType.CAUSAL_LM,
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    return model, tokenizer, lora_config


def train(config: dict, cli_overrides: dict | None = None):
    """Run the full training pipeline."""
    print("=" * 60)
    print("Code README Writer - SFT Training")
    print("=" * 60)

    # Setup model
    print("\n[1/4] Loading model and tokenizer...")
    model, tokenizer, lora_config = setup_model_and_tokenizer(config)

    # Load data
    print("\n[2/4] Loading dataset...")
    dataset = load_dataset_from_jsonl(
        config.get("data_dir", "data"),
        train_split=config["data"]["train_split"],
    )
    print(f"  Train: {len(dataset['train'])} examples")
    print(f"  Eval:  {len(dataset['test'])} examples")

    # Limit samples if configured
    max_samples = config["data"].get("max_samples")
    if max_samples:
        if len(dataset["train"]) > max_samples:
            dataset["train"] = dataset["train"].select(range(max_samples))
        eval_max = max(100, max_samples // 10)
        if len(dataset["test"]) > eval_max:
            dataset["test"] = dataset["test"].select(range(eval_max))

    # Setup training arguments
    training_config = config["training"].copy()
    if cli_overrides:
        training_config.update(cli_overrides)

    training_args = TrainingArguments(**training_config)

    # Formatting function
    template = config["data"]["prompt_template"]
    formatting_func = create_formatting_function(template)

    # Response template for completion-only training
    # Only compute loss on the assistant's response (the README)
    response_template = "<|assistant|>\n"
    collator = DataCollatorForCompletionOnlyLM(
        response_template=response_template,
        tokenizer=tokenizer,
    )

    # Setup trainer
    print("\n[3/4] Initializing SFT Trainer...")
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"],
        formatting_func=formatting_func,
        data_collator=collator,
        max_seq_length=config["model"]["max_length"],
        packing=False,
    )

    # Train
    print("\n[4/4] Starting training...")
    print(f"  Model: {config['model']['name']}")
    print(f"  LoRA rank: {config['lora']['r']}")
    print(f"  Learning rate: {training_config['learning_rate']}")
    print(f"  Epochs: {training_config['num_train_epochs']}")
    print(f"  Batch size: {training_config['per_device_train_batch_size']}")
    print(f"  Gradient accumulation: {training_config['gradient_accumulation_steps']}")
    effective_batch = (
        training_config["per_device_train_batch_size"]
        * training_config["gradient_accumulation_steps"]
    )
    print(f"  Effective batch size: {effective_batch}")
    print()

    train_result = trainer.train()

    # Save metrics
    metrics = train_result.metrics
    trainer.log_metrics("train", metrics)
    trainer.save_metrics("train", metrics)

    # Evaluate
    print("\nRunning evaluation...")
    eval_metrics = trainer.evaluate()
    trainer.log_metrics("eval", eval_metrics)
    trainer.save_metrics("eval", eval_metrics)

    # Save the LoRA adapter
    output_dir = training_config["output_dir"]
    print(f"\nSaving LoRA adapter to {output_dir}/final_adapter...")
    trainer.save_model(os.path.join(output_dir, "final_adapter"))
    tokenizer.save_pretrained(os.path.join(output_dir, "final_adapter"))

    print("\nTraining complete!")
    print(f"  Train loss: {metrics.get('train_loss', 'N/A'):.4f}")
    print(f"  Eval loss:  {eval_metrics.get('eval_loss', 'N/A'):.4f}")

    return trainer


def main():
    parser = argparse.ArgumentParser(description="Train Code README Writer with SFT")
    parser.add_argument("--config", type=str, default="configs/training_config.yaml",
                        help="Path to training config YAML")
    parser.add_argument("--data_dir", type=str, default="data",
                        help="Path to data directory")
    parser.add_argument("--per_device_train_batch_size", type=int, default=None)
    parser.add_argument("--gradient_accumulation_steps", type=int, default=None)
    parser.add_argument("--num_train_epochs", type=int, default=None)
    parser.add_argument("--learning_rate", type=float, default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    config["data_dir"] = args.data_dir

    # Build CLI overrides
    overrides = {}
    if args.per_device_train_batch_size is not None:
        overrides["per_device_train_batch_size"] = args.per_device_train_batch_size
    if args.gradient_accumulation_steps is not None:
        overrides["gradient_accumulation_steps"] = args.gradient_accumulation_steps
    if args.num_train_epochs is not None:
        overrides["num_train_epochs"] = args.num_train_epochs
    if args.learning_rate is not None:
        overrides["learning_rate"] = args.learning_rate

    train(config, overrides if overrides else None)


if __name__ == "__main__":
    main()
