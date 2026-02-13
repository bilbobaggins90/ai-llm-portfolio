---
title: Code README Writer
emoji: 📝
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 4.10.0
app_file: app.py
pinned: false
license: mit
---

# Code README Writer

Generate README.md files from repository structure and code using a fine-tuned TinyLlama-1.1B model (SFT + QLoRA).

Enter your repository's file tree and key source files to get a well-structured README with installation instructions, usage examples, API docs, and more.

## How to Deploy

1. Train the model (see `notebooks/train_colab.ipynb`)
2. Upload the LoRA adapter to this Space as `adapter/`
3. The app will load the adapter automatically

## Model Details

- **Base Model:** TinyLlama-1.1B-Chat-v1.0
- **Method:** SFT with QLoRA (4-bit NF4)
- **Training Data:** 5K+ GitHub repo-README pairs
- **Adapter Size:** ~20MB
