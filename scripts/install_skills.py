#!/usr/bin/env python3
"""Install the repository's bundled skills without downloads or overwrites."""
import argparse
import filecmp
import re
import shutil
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / '.agents' / 'skills'


def same_tree(left: Path, right: Path) -> bool:
    left_files = {p.relative_to(left) for p in left.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    right_files = {p.relative_to(right) for p in right.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    return left_files == right_files and all(filecmp.cmp(left / p, right / p, shallow=False) for p in left_files)


def install(source: Path, destination: Path, names: list[str], dry_run: bool = False) -> list[str]:
    """Preflight the entire selection before copying; preserve existing skills."""
    source = source.resolve()
    destination = destination.expanduser().resolve()
    if destination == source or source in destination.parents:
        raise ValueError('Choose a destination outside the source skills directory.')
    planned = []
    for name in dict.fromkeys(names):
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
            raise ValueError(f'Invalid skill name: {name}')
        skill = source / name
        if not (skill / 'SKILL.md').is_file():
            raise ValueError(f'Unknown or incomplete skill: {name}')
        if any(p.is_symlink() for p in skill.rglob('*')) or skill.is_symlink():
            raise ValueError(f'Source skill contains symlinks: {name}')
        target = destination / name
        if target.is_symlink():
            raise ValueError(f'Refusing to replace destination symlink: {target}')
        if target.exists():
            if target.is_dir() and same_tree(skill, target):
                planned.append((name, 'already installed'))
                continue
            raise ValueError(f'Destination differs; preserved existing files: {target}. Choose a new destination or reconcile manually.')
        planned.append((name, 'would install' if dry_run else 'installed'))
    if not dry_run:
        destination.mkdir(parents=True, exist_ok=True)
        for name, status in planned:
            if status == 'installed':
                shutil.copytree(source / name, destination / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    return [f'{name}: {status} at {destination / name}' for name, status in planned]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', type=Path, required=True, help='Destination containing the skill folders, e.g. ~/.agents/skills')
    parser.add_argument('--skill', action='append', help='Install only this skill (repeatable); defaults to all bundled skills')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    names = args.skill or sorted(p.name for p in SOURCE.iterdir() if (p / 'SKILL.md').is_file())
    try:
        for message in install(SOURCE, args.dest, names, args.dry_run):
            print(message)
    except (ValueError, OSError) as error:
        parser.exit(1, f'Installation failed: {error}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
