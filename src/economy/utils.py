import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import aiofiles

from src.config import settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OTHER_CONFIG_PATH = PROJECT_ROOT / 'other'


def _config_relative_path(filepath: Path) -> Path:
    config_root = Path(settings.configs_repo_path).resolve()
    target = filepath.resolve()
    try:
        return target.relative_to(config_root)
    except ValueError as error:
        msg = f'Refusing to modify a file outside configs_repo_path: {target}'
        raise RuntimeError(msg) from error


def backup_config_file(filepath: Path) -> Path | None:
    """Copy an existing server config to the configured backup directory."""
    if not filepath.exists():
        return None

    relative_path = _config_relative_path(filepath)
    timestamp = datetime.now(tz=UTC).strftime('%Y%m%dT%H%M%S.%fZ')
    backup_path = Path(settings.config_backup_path) / timestamp / relative_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(filepath, backup_path)
    return backup_path


async def atomic_write_text(filepath: Path, content: str) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = filepath.with_name(f'.{filepath.name}.reborn.tmp')
    try:
        async with aiofiles.open(temporary_path, 'w', encoding='utf-8') as file:
            await file.write(content)
        temporary_path.replace(filepath)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


async def edit_config(filepath: Path, data_key: str, data: list[Any]) -> None:
    async with aiofiles.open(filepath, encoding='utf-8') as f:
        file_data = await f.read()
        full_json = json.loads(file_data)

    full_json[data_key] = data

    backup_config_file(filepath)
    full_json_str = json.dumps(full_json, indent=2, ensure_ascii=False)
    await atomic_write_text(filepath, full_json_str)
