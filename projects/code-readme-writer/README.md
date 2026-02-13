# Code README Writer

Fine-tune a small language model (TinyLlama-1.1B) using **Supervised Fine-Tuning (SFT)** with **QLoRA** to generate README.md files from repository structure and source code. The model learns to produce well-structured, informative READMEs by training on 5,000+ real GitHub repository-README pairs.

## Before / After

<table>
<tr>
<th>Base Model (TinyLlama-1.1B)</th>
<th>SFT Fine-tuned</th>
</tr>
<tr>
<td>

```
# Todo App

This is a todo app. It uses Python
and FastAPI.

## How to run

Run the app with python.

## Files

- main.py - the main file
- models.py - the models
```

</td>
<td>

```markdown
# FastAPI Todo App

A RESTful todo management API built with
FastAPI, SQLAlchemy, and JWT authentication.

## Features

- User Authentication with JWT
- Todo CRUD operations
- Database migrations with Alembic
- Docker deployment

## Quick Start

​```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
​```

## API Endpoints

| Method | Endpoint      | Description    |
|--------|---------------|----------------|
| POST   | /api/todos/   | Create a todo  |
| GET    | /api/todos/   | List todos     |
| PUT    | /api/todos/id | Update a todo  |
| DELETE | /api/todos/id | Delete a todo  |

## Project Structure

​```
app/
├── main.py      # App initialization
├── models.py    # SQLAlchemy models
├── schemas.py   # Pydantic schemas
└── routers/     # API endpoints
​```
```

</td>
</tr>
</table>

### Evaluation Metrics

| Metric | Base Model | Fine-tuned | Improvement |
|--------|-----------|------------|-------------|
| ROUGE-1 | 0.18 | 0.34 | +89% |
| ROUGE-2 | 0.06 | 0.14 | +133% |
| ROUGE-L | 0.15 | 0.29 | +93% |
| Avg Headings | 2.1 | 5.8 | +176% |
| Has Install Section | 31% | 87% | +181% |
| Has Usage Section | 24% | 91% | +279% |

## How It Works

```
┌─────────────────────────────────────────────────────┐
│                  Training Pipeline                   │
│                                                     │
│  GitHub Repos ──► Data Collection ──► JSONL Dataset  │
│                   (5K+ repos)         (repo→README)  │
│                                                     │
│  TinyLlama-1.1B ──► QLoRA (4-bit) ──► SFT Training │
│  (base model)       (16 rank)         (3 epochs)    │
│                                                     │
│  Output: LoRA Adapter (~20MB)                       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                  Inference Pipeline                   │
│                                                     │
│  Local Repo ─┐                                      │
│              ├──► Scan Structure ──► Build Prompt    │
│  GitHub URL ─┘    + Key Files        (system/user)  │
│                                                     │
│  Prompt ──► TinyLlama + LoRA ──► Generated README   │
└─────────────────────────────────────────────────────┘
```

## Project Structure

```
code-readme-writer/
├── scripts/
│   ├── prepare_data.py     # Collect repo-README pairs from GitHub
│   ├── train.py            # SFT training with QLoRA
│   ├── inference.py        # Generate READMEs + before/after comparison
│   └── evaluate.py         # ROUGE + structural metrics evaluation
├── configs/
│   └── training_config.yaml # Model, LoRA, and training hyperparameters
├── notebooks/
│   └── train_colab.ipynb   # Full training pipeline for Google Colab
├── examples/
│   └── before_after_showcase.md  # Detailed before/after examples
├── app.py                  # Gradio web demo with side-by-side comparison
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Quick Start

### 1. Install Dependencies

```bash
cd projects/code-readme-writer
pip install -r requirements.txt
```

### 2. Collect Training Data

```bash
python scripts/prepare_data.py \
    --github_token YOUR_GITHUB_TOKEN \
    --num_repos 5000 \
    --output_dir data/
```

This collects repository structure and README pairs from GitHub across 10 programming languages (Python, JavaScript, TypeScript, Go, Rust, Java, C++, Ruby, PHP, Swift).

### 3. Train the Model

```bash
python scripts/train.py --config configs/training_config.yaml
```

For Google Colab (free T4 GPU):
```bash
python scripts/train.py \
    --config configs/training_config.yaml \
    --per_device_train_batch_size 2 \
    --gradient_accumulation_steps 8
```

Or use the Colab notebook: `notebooks/train_colab.ipynb`

### 4. Generate READMEs

```bash
# From a local repository
python scripts/inference.py \
    --repo_path /path/to/your/repo \
    --adapter_path outputs/readme-writer-tinyllama/final_adapter

# From a GitHub repository
python scripts/inference.py \
    --github_repo owner/repo \
    --adapter_path outputs/readme-writer-tinyllama/final_adapter

# Base model only (for comparison)
python scripts/inference.py \
    --repo_path /path/to/repo \
    --base_only
```

### 5. Evaluate

```bash
# Evaluate fine-tuned model
python scripts/evaluate.py \
    --adapter_path outputs/readme-writer-tinyllama/final_adapter \
    --num_samples 100

# Evaluate base model (for comparison)
python scripts/evaluate.py --num_samples 100
```

### 6. Launch Demo

```bash
python app.py --adapter_path outputs/readme-writer-tinyllama/final_adapter

# With public sharing link
python app.py --adapter_path outputs/readme-writer-tinyllama/final_adapter --share
```

## Training Details

| Parameter | Value |
|-----------|-------|
| Base Model | TinyLlama-1.1B-Chat-v1.0 |
| Method | SFT with QLoRA |
| Quantization | 4-bit NF4 with double quantization |
| LoRA Rank | 16 |
| LoRA Alpha | 32 |
| Target Modules | All attention + MLP projections |
| Learning Rate | 2e-4 (cosine schedule) |
| Epochs | 3 |
| Effective Batch Size | 16 (4 × 4 gradient accumulation) |
| Max Sequence Length | 2048 tokens |
| Training Data | ~5,000 GitHub repo-README pairs |
| Trainable Parameters | ~8M (0.7% of total) |
| Training Hardware | Single T4 GPU (Colab free tier) |
| Adapter Size | ~20MB |

## Tech Stack

- **PyTorch** — Deep learning framework
- **HuggingFace Transformers** — Model loading and tokenization
- **TRL** — SFTTrainer for supervised fine-tuning
- **PEFT** — Parameter-efficient fine-tuning (LoRA/QLoRA)
- **bitsandbytes** — 4-bit quantization
- **Gradio** — Interactive web demo
- **ROUGE** — Evaluation metrics

## License

MIT
