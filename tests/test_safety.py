import asyncio
import json
from pathlib import Path

import pytest

from src.common_tools import _normalized_role_name
from src.config import settings
from src.economy.muta import MutantConfig
from src.economy.utils import edit_config
from src.quents.schemas import QuentRecordSchema
from src.server_tools.whitelist import WhitelistServise
from src.teable.sql import table_ref


@pytest.mark.parametrize(
    ('actual', 'expected'),
    [
        ('Тех. администратор', 'тех.администратор'),
        (' ТЕХ.   АДМИНИСТРАТОР ', 'тех.администратор'),
    ],
)
def test_role_name_normalization(actual: str, expected: str) -> None:
    assert _normalized_role_name(actual) == _normalized_role_name(expected)


def test_questionnaire_record_keeps_teable_record_id() -> None:
    record = QuentRecordSchema.from_teable_record(
        {
            'id': 'recExample',
            'fields': {
                'nickname': 'Stalker',
                'status': 'Создана',
                'steam_id': '76561198000000000',
                'quent_link': 'https://docs.google.com/example',
                'birth_date': '01.01.1990',
                'discord_slug': 'stalker',
                'discord_id': '123',
                'discord_channel_id': '456',
                'character_name': 'Ivan Petrov',
            },
        }
    )

    assert record.id == 'recExample'


def test_table_ref_quotes_valid_identifiers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, 'teable_db_schema', 'bse_example')

    assert table_ref('items') == '"bse_example"."items"'


@pytest.mark.parametrize('value', ['', 'bad-name', 'items; DROP TABLE users'])
def test_table_ref_rejects_invalid_identifiers(
    monkeypatch: pytest.MonkeyPatch,
    value: str,
) -> None:
    monkeypatch.setattr(settings, 'teable_db_schema', 'bse_example')

    with pytest.raises(RuntimeError):
        table_ref(value)


def test_edit_config_creates_backup_and_replaces_json_atomically(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_root = tmp_path / 'configs'
    backup_root = tmp_path / 'backups'
    config_file = config_root / 'TraderPlus' / 'config.json'
    config_file.parent.mkdir(parents=True)
    config_file.write_text('{"Traders": ["old"]}', encoding='utf-8')
    monkeypatch.setattr(settings, 'configs_repo_path', str(config_root))
    monkeypatch.setattr(settings, 'config_backup_path', str(backup_root))

    asyncio.run(edit_config(config_file, 'Traders', ['new']))

    assert json.loads(config_file.read_text(encoding='utf-8')) == {'Traders': ['new']}
    backups = list(backup_root.rglob('config.json'))
    assert len(backups) == 1
    assert json.loads(backups[0].read_text(encoding='utf-8')) == {'Traders': ['old']}
    assert not list(config_root.rglob('*.reborn.tmp'))


def test_mutant_cleanup_preserves_manual_files_and_directories(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_root = tmp_path / 'configs'
    points = config_root / 'MPG_Spawner' / 'Points'
    backup_root = tmp_path / 'backups'
    points.mkdir(parents=True)
    manual = points / 'custom_hnd.json'
    generated = points / 'generated.json'
    unrelated = points / 'notes.txt'
    nested = points / 'manual-assets'
    manual.write_text('{}', encoding='utf-8')
    generated.write_text('{}', encoding='utf-8')
    unrelated.write_text('keep', encoding='utf-8')
    nested.mkdir()
    monkeypatch.setattr(settings, 'configs_repo_path', str(config_root))
    monkeypatch.setattr(settings, 'config_backup_path', str(backup_root))

    result = asyncio.run(
        MutantConfig()._delete_generated_and_get_handmade(points)  # noqa: SLF001
    )

    assert result == ['custom_hnd']
    assert manual.exists()
    assert not generated.exists()
    assert unrelated.exists()
    assert nested.exists()
    assert len(list(backup_root.rglob('generated.json'))) == 1


def test_whitelist_rejects_newlines_and_duplicates(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    whitelist = tmp_path / 'whitelist.txt'
    whitelist.write_text('first', encoding='utf-8')
    monkeypatch.setattr(settings, 'whitelist_path', str(whitelist))

    assert asyncio.run(WhitelistServise.add_to_whitelist('second')) is True
    assert asyncio.run(WhitelistServise.add_to_whitelist('second')) is False
    with pytest.raises(ValueError, match='недопустимые символы'):
        asyncio.run(WhitelistServise.add_to_whitelist('third\nfourth'))

    assert whitelist.read_text(encoding='utf-8').splitlines() == ['first', 'second']
