from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


DEFAULT_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".vue",
    ".html",
    ".css",
    ".scss",
    ".sass",
    ".less",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".md",
}

DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".idea",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "coverage",
}

DEFAULT_EXCLUDED_FILES = {
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "uv.lock",
}

COMMENT_PREFIXES = {
    ".py": ("#",),
    ".js": ("//",),
    ".jsx": ("//",),
    ".ts": ("//",),
    ".tsx": ("//",),
    ".vue": ("//",),
    ".css": ("//", "/*", "*", "*/"),
    ".scss": ("//", "/*", "*", "*/"),
    ".sass": ("//", "/*", "*", "*/"),
    ".less": ("//", "/*", "*", "*/"),
    ".html": ("<!--",),
    ".md": ("<!--",),
}


@dataclass(slots=True)
class FileStats:
    files: int = 0
    total_lines: int = 0
    non_empty_lines: int = 0
    code_lines: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Count lines of code in this project.")
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Project root directory. Defaults to current directory.",
    )
    parser.add_argument(
        "--ext",
        nargs="+",
        help="Only count these extensions, e.g. --ext .py .vue .ts",
    )
    parser.add_argument(
        "--include-lock",
        action="store_true",
        help="Include lock files such as package-lock.json and uv.lock.",
    )
    parser.add_argument(
        "--show-files",
        action="store_true",
        help="Show per-file statistics.",
    )
    return parser.parse_args()


def normalize_extensions(raw_extensions: list[str] | None) -> set[str]:
    if not raw_extensions:
        return set(DEFAULT_EXTENSIONS)
    normalized = set()
    for extension in raw_extensions:
        normalized.add(extension if extension.startswith(".") else f".{extension}")
    return normalized


def should_skip(path: Path, root: Path, include_lock: bool) -> bool:
    if path.is_dir():
        return path.name in DEFAULT_EXCLUDED_DIRS

    relative_parts = path.relative_to(root).parts
    if any(part in DEFAULT_EXCLUDED_DIRS for part in relative_parts[:-1]):
        return True

    if not include_lock and path.name in DEFAULT_EXCLUDED_FILES:
        return True

    return False


def count_file(path: Path) -> tuple[int, int, int]:
    total_lines = 0
    non_empty_lines = 0
    code_lines = 0
    comment_prefixes = COMMENT_PREFIXES.get(path.suffix.lower(), ())

    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            total_lines += 1
            stripped = line.strip()
            if not stripped:
                continue

            non_empty_lines += 1
            if stripped.startswith(comment_prefixes):
                continue

            code_lines += 1

    return total_lines, non_empty_lines, code_lines


def iter_files(root: Path, extensions: set[str], include_lock: bool) -> list[Path]:
    matched_files: list[Path] = []
    for path in root.rglob("*"):
        if should_skip(path, root, include_lock):
            continue
        if path.is_file() and path.suffix.lower() in extensions:
            matched_files.append(path)
    return sorted(matched_files)


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    extensions = normalize_extensions(args.ext)
    files = iter_files(root, extensions, args.include_lock)

    totals = FileStats()
    stats_by_extension: dict[str, FileStats] = defaultdict(FileStats)
    stats_by_file: list[tuple[Path, int, int, int]] = []

    for file_path in files:
        total_lines, non_empty_lines, code_lines = count_file(file_path)
        extension = file_path.suffix.lower()

        totals.files += 1
        totals.total_lines += total_lines
        totals.non_empty_lines += non_empty_lines
        totals.code_lines += code_lines

        bucket = stats_by_extension[extension]
        bucket.files += 1
        bucket.total_lines += total_lines
        bucket.non_empty_lines += non_empty_lines
        bucket.code_lines += code_lines

        if args.show_files:
            stats_by_file.append((file_path, total_lines, non_empty_lines, code_lines))

    print(f"Project root: {root}")
    print(f"Extensions: {', '.join(sorted(extensions))}")
    print()
    print("Summary")
    print(f"  Files:           {totals.files}")
    print(f"  Total lines:     {totals.total_lines}")
    print(f"  Non-empty lines: {totals.non_empty_lines}")
    print(f"  Code lines:      {totals.code_lines}")
    print()
    print("By extension")
    for extension in sorted(stats_by_extension):
        item = stats_by_extension[extension]
        print(
            f"  {extension:<6} files={item.files:<3} "
            f"total={item.total_lines:<6} non-empty={item.non_empty_lines:<6} code={item.code_lines:<6}"
        )

    if args.show_files:
        print()
        print("By file")
        for file_path, total_lines, non_empty_lines, code_lines in stats_by_file:
            relative_path = file_path.relative_to(root)
            print(
                f"  {relative_path} | total={total_lines} "
                f"non-empty={non_empty_lines} code={code_lines}"
            )


if __name__ == "__main__":
    main()
