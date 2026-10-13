from typing import Any

import httpx

from src.config import settings


class Tables:
    @staticmethod
    def users() -> str:
        return _required_table_id(settings.teable_users_table_id, 'teable_users_table_id')

    @staticmethod
    def trader_price() -> str:
        return _required_table_id(
            settings.teable_trader_price_table_id,
            'teable_trader_price_table_id',
        )


def _required_table_id(value: str, setting_name: str) -> str:
    if not value:
        msg = f'{setting_name} is not configured'
        raise RuntimeError(msg)
    return value


def _headers() -> dict[str, str]:
    return {
        'Authorization': f'Bearer {settings.teable_token.get_secret_value()}',
        'Content-Type': 'application/json',
    }


def _api_url(path: str) -> str:
    return f'{settings.teable_api_url.rstrip("/")}/{path.lstrip("/")}'


async def get_records(
    table_id: str, *, field_key_type: str = 'dbFieldName', params: dict[str, Any] | None = None
) -> httpx.Response:
    if not params:
        params = {}

    params['fieldKeyType'] = field_key_type

    async with httpx.AsyncClient() as client:
        response = await client.get(
            _api_url(f'table/{table_id}/record'),
            headers=_headers(),
            params=params,
        )

        response.raise_for_status()
        return response


async def update_record(
    table_id: str,
    record_id: str,
    record_data: dict[str, Any],
    *,
    field_key_type: str = 'dbFieldName',
    params: dict[str, Any] | None = None,
) -> httpx.Response:
    if not params:
        params = {}

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            _api_url(f'table/{table_id}/record/{record_id}'),
            headers=_headers(),
            params=params,
            json={'fieldKeyType': field_key_type, 'record': {'fields': record_data}},
        )

        response.raise_for_status()
        return response


async def create_record(
    table_id: str,
    fields: dict[str, Any],
    *,
    field_key_type: str = 'dbFieldName',
    params: dict[str, Any] | None = None,
) -> httpx.Response:
    if not params:
        params = {}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            _api_url(f'table/{table_id}/record'),
            headers=_headers(),
            params=params,
            json={'fieldKeyType': field_key_type, 'records': [{'fields': fields}]},
        )

        response.raise_for_status()
        return response


async def create_records(
    table_id: str,
    records_data: list[dict[str, Any]],
    *,
    field_key_type: str = 'dbFieldName',
    params: dict[str, Any] | None = None,
) -> httpx.Response:
    if not params:
        params = {}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            _api_url(f'table/{table_id}/record'),
            headers=_headers(),
            params=params,
            json={'fieldKeyType': field_key_type, 'records': records_data},
        )

        response.raise_for_status()
        return response
