"""
Data Preparation for Code README Writer

Collects repository-README pairs from GitHub for SFT training.
Builds a dataset of (repo_structure + code_snippets) -> README pairs.

Usage:
    python scripts/prepare_data.py \
        --output_dir data/ \
        --num_repos 5000 \
        --github_token YOUR_TOKEN
"""

import argparse
import json
import os
import re
import time
from pathlib import Path

import requests
from tqdm import tqdm


GITHUB_API = "https://api.github.com"

# File extensions to include as "key files"
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs",
    ".cpp", ".c", ".h", ".rb", ".php", ".swift", ".kt", ".scala",
    ".cs", ".r", ".jl", ".lua", ".sh", ".bash", ".zsh",
}

# Files that are typically informative for understanding a repo
IMPORTANT_FILES = {
    "setup.py", "setup.cfg", "pyproject.toml", "package.json",
    "cargo.toml", "go.mod", "build.gradle", "pom.xml",
    "makefile", "dockerfile", "docker-compose.yml",
    "requirements.txt", "gemfile", ".env.example",
}

# Max characters per code file to include
MAX_FILE_CHARS = 1500
# Max total code characters per repo
MAX_TOTAL_CODE_CHARS = 6000
# Max README length in characters
MAX_README_CHARS = 4000


def get_headers(token: str | None) -> dict:
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def search_repos(
    token: str | None,
    language: str,
    min_stars: int = 10,
    max_stars: int = 5000,
    per_page: int = 100,
    page: int = 1,
) -> list[dict]:
    """Search GitHub for repositories with READMEs in a given language."""
    headers = get_headers(token)
    query = f"language:{language} stars:{min_stars}..{max_stars} has:readme"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": per_page,
        "page": page,
    }
    resp = requests.get(f"{GITHUB_API}/search/repositories", headers=headers, params=params)
    resp.raise_for_status()
    return resp.json().get("items", [])


def get_repo_tree(owner: str, repo: str, token: str | None) -> list[dict] | None:
    """Get the full file tree of a repository."""
    headers = get_headers(token)
    url = f"{GITHUB_API}/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return None
    return resp.json().get("tree", [])


def get_file_content(owner: str, repo: str, path: str, token: str | None) -> str | None:
    """Download raw file content from a repository."""
    headers = get_headers(token)
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{path}"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return None
    return resp.text


def build_file_tree_string(tree: list[dict], max_entries: int = 80) -> str:
    """Build a readable file tree string from the GitHub tree API response."""
    paths = sorted(
        item["path"]
        for item in tree
        if item["type"] in ("blob", "tree")
        and not any(part.startswith(".") for part in item["path"].split("/"))
        and "node_modules" not in item["path"]
        and "__pycache__" not in item["path"]
        and ".egg-info" not in item["path"]
    )
    if len(paths) > max_entries:
        paths = paths[:max_entries]
        paths.append("... (truncated)")
    return "\n".join(paths)


def select_key_files(tree: list[dict]) -> list[str]:
    """Select the most informative code files to include as context."""
    selected = []

    # Always include important config files
    for item in tree:
        if item["type"] == "blob":
            basename = os.path.basename(item["path"]).lower()
            if basename in IMPORTANT_FILES:
                selected.append(item["path"])

    # Include top-level and src-level code files
    for item in tree:
        if item["type"] != "blob":
            continue
        ext = os.path.splitext(item["path"])[1].lower()
        if ext not in CODE_EXTENSIONS:
            continue
        depth = item["path"].count("/")
        if depth <= 2:
            selected.append(item["path"])

    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for path in selected:
        if path not in seen:
            seen.add(path)
            deduped.append(path)

    return deduped[:10]  # Limit to 10 files


def build_code_snippets(
    owner: str, repo: str, file_paths: list[str], token: str | None
) -> str:
    """Download and concatenate key file contents."""
    snippets = []
    total_chars = 0

    for path in file_paths:
        if total_chars >= MAX_TOTAL_CODE_CHARS:
            break
        content = get_file_content(owner, repo, path, token)
        if content is None:
            continue
        content = content[:MAX_FILE_CHARS]
        total_chars += len(content)
        snippets.append(f"--- {path} ---\n{content}")

    return "\n\n".join(snippets)


def clean_readme(readme: str) -> str:
    """Clean and normalize README content."""
    # Remove badges/shields (noisy for training)
    readme = re.sub(r"\[!\[.*?\]\(.*?\)\]\(.*?\)", "", readme)
    readme = re.sub(r"!\[.*?\]\(.*?\)", "", readme)
    # Collapse excessive whitespace
    readme = re.sub(r"\n{3,}", "\n\n", readme)
    return readme.strip()


def is_quality_readme(readme: str) -> bool:
    """Filter for reasonably high-quality READMEs."""
    if len(readme) < 200:
        return False
    if len(readme) > MAX_README_CHARS:
        return False
    # Should have at least some structure
    if readme.count("#") < 2:
        return False
    # Should have some descriptive text
    words = readme.split()
    if len(words) < 50:
        return False
    return True


def process_repo(repo_info: dict, token: str | None) -> dict | None:
    """Process a single repository into a training example."""
    owner = repo_info["owner"]["login"]
    repo = repo_info["name"]
    repo_name = repo_info["full_name"]

    # Get file tree
    tree = get_repo_tree(owner, repo, token)
    if tree is None:
        return None

    # Get README
    readme_path = None
    for item in tree:
        if item["type"] == "blob" and item["path"].lower() in (
            "readme.md", "readme.rst", "readme.txt", "readme",
        ):
            readme_path = item["path"]
            break

    if readme_path is None:
        return None

    readme_content = get_file_content(owner, repo, readme_path, token)
    if readme_content is None:
        return None

    readme_content = clean_readme(readme_content)
    if not is_quality_readme(readme_content):
        return None

    # Build input features
    file_tree = build_file_tree_string(tree)
    key_files = select_key_files(tree)
    code_snippets = build_code_snippets(owner, repo, key_files, token)

    if not code_snippets:
        return None

    return {
        "repo_name": repo_name,
        "file_tree": file_tree,
        "code_snippets": code_snippets,
        "readme_content": readme_content,
        "stars": repo_info.get("stargazers_count", 0),
        "language": repo_info.get("language", "unknown"),
    }


def collect_dataset(
    token: str | None,
    num_repos: int = 5000,
    output_dir: str = "data",
) -> None:
    """Collect the full training dataset."""
    os.makedirs(output_dir, exist_ok=True)
    examples = []

    languages = [
        "Python", "JavaScript", "TypeScript", "Go", "Rust",
        "Java", "C++", "Ruby", "PHP", "Swift",
    ]

    repos_per_language = num_repos // len(languages)

    for lang in languages:
        print(f"\nCollecting {lang} repositories...")
        page = 1
        collected = 0

        while collected < repos_per_language:
            try:
                repos = search_repos(
                    token, lang,
                    per_page=min(100, repos_per_language - collected),
                    page=page,
                )
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    print("Rate limited. Sleeping 60s...")
                    time.sleep(60)
                    continue
                raise

            if not repos:
                break

            for repo_info in tqdm(repos, desc=f"{lang} page {page}"):
                example = process_repo(repo_info, token)
                if example:
                    examples.append(example)
                    collected += 1
                time.sleep(0.5)  # Rate limit courtesy

            page += 1

        print(f"  Collected {collected} {lang} examples")

    # Save dataset
    output_path = os.path.join(output_dir, "readme_dataset.jsonl")
    with open(output_path, "w") as f:
        for example in examples:
            f.write(json.dumps(example) + "\n")

    print(f"\nTotal examples collected: {len(examples)}")
    print(f"Dataset saved to: {output_path}")

    # Save stats
    stats = {
        "total_examples": len(examples),
        "by_language": {},
    }
    for ex in examples:
        lang = ex["language"]
        stats["by_language"][lang] = stats["by_language"].get(lang, 0) + 1

    stats_path = os.path.join(output_dir, "dataset_stats.json")
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"Stats saved to: {stats_path}")


def main():
    parser = argparse.ArgumentParser(description="Collect repo-README pairs for SFT")
    parser.add_argument("--output_dir", type=str, default="data",
                        help="Output directory for dataset")
    parser.add_argument("--num_repos", type=int, default=5000,
                        help="Target number of repositories to collect")
    parser.add_argument("--github_token", type=str, default=None,
                        help="GitHub personal access token (recommended for rate limits)")
    args = parser.parse_args()

    token = args.github_token or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Warning: No GitHub token provided. Rate limits will be very restrictive.")
        print("Set GITHUB_TOKEN env var or pass --github_token")

    collect_dataset(token, args.num_repos, args.output_dir)


if __name__ == "__main__":
    main()
