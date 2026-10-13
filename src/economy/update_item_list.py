import httpx
from sqlalchemy import text

from src.config import settings
from src.db import session_getter
from src.teable.sql import table_ref


async def insert_classnames(server_items: dict[str, str]) -> None:
    filtered_items = await _filter_items(server_items)
    existing_key_list = await _get_existing_classnames_from_list(list(filtered_items))

    new_items = {k: v for k, v in filtered_items.items() if k not in existing_key_list}

    await _insert_items_to_teable(new_items)


async def _filter_items(items: dict[str, str]) -> dict[str, str]:
    prefix_black_list = ('Land_', 'land_', 'StaticObj_', 'SV_ZSCS', 'ZmbM_')
    return {k: v for k, v in items.items() if not k.startswith(prefix_black_list)}


async def _get_existing_classnames_from_list(classnname_list: list[str]) -> list[str]:
    query = (
        f'SELECT classname FROM {table_ref(settings.teable_items_db_table)} '  # noqa: S608
        'WHERE classname = Any(:items)'
    )
    async with session_getter() as session:
        res = await session.execute(
            text(query),
            {'items': classnname_list},
        )

        return [row['classname'] for row in res.mappings()]


async def _insert_items_to_teable(items_dict: dict[str, str]) -> None:
    if not settings.teable_items_table_id:
        msg = 'teable_items_table_id is not configured'
        raise RuntimeError(msg)

    items_list = list(items_dict.items())
    chunk_size = 50
    async with httpx.AsyncClient() as client:
        for i in range(0, len(items_list), chunk_size):
            chunk = items_list[i : i + chunk_size]

            response = await client.post(
                f'{settings.teable_api_url.rstrip("/")}/table/{settings.teable_items_table_id}/record',
                headers={
                    'Authorization': f'Bearer {settings.teable_token.get_secret_value()}',
                    'Content-Type': 'application/json',
                },
                json={'records': [{'fields': {'Класснейм': k, 'Название': v}} for k, v in chunk]},
            )
            response.raise_for_status()
