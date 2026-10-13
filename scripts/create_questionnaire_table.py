import argparse
import asyncio
import os
from typing import Any

import httpx


def questionnaire_table_definition() -> dict[str, Any]:
    return {
        'name': 'Анкеты',
        'dbTableName': 'users',
        'fields': [
            {
                'name': 'Позывной',
                'dbFieldName': 'nickname',
                'type': 'singleLineText',
                'isPrimary': True,
            },
            {
                'name': 'Статус',
                'dbFieldName': 'status',
                'type': 'singleLineText',
            },
            {
                'name': 'Steam ID',
                'dbFieldName': 'steam_id',
                'type': 'singleLineText',
            },
            {
                'name': 'Квента',
                'dbFieldName': 'quent_link',
                'type': 'singleLineText',
            },
            {
                'name': 'Дата рождения',
                'dbFieldName': 'birth_date',
                'type': 'singleLineText',
            },
            {
                'name': 'Discord username',
                'dbFieldName': 'discord_slug',
                'type': 'singleLineText',
            },
            {
                'name': 'Discord ID',
                'dbFieldName': 'discord_id',
                'type': 'singleLineText',
            },
            {
                'name': 'Discord channel ID',
                'dbFieldName': 'discord_channel_id',
                'type': 'singleLineText',
            },
            {
                'name': 'Имя персонажа',
                'dbFieldName': 'character_name',
                'type': 'singleLineText',
            },
        ],
        'views': [{'name': 'Все анкеты', 'type': 'grid'}],
    }


async def create_table(api_url: str, token: str, base_id: str) -> str:
    url = f'{api_url.rstrip("/")}/base/{base_id}/table/'
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            url,
            headers=headers,
            json=questionnaire_table_definition(),
        )
        response.raise_for_status()
        table_id = response.json()['id']
        return str(table_id)


async def main() -> None:
    parser = argparse.ArgumentParser(
        description='Create the questionnaire table in an imported Reborn Teable base.'
    )
    parser.add_argument('--api-url', default='http://127.0.0.1:3000/api')
    parser.add_argument('--base-id', required=True)
    args = parser.parse_args()

    token = os.environ.get('TEABLE_TOKEN')
    if not token:
        parser.error('Set TEABLE_TOKEN in the environment before running this script')

    table_id = await create_table(args.api_url, token, args.base_id)
    print(f'teable_users_table_id={table_id}')  # noqa: T201 - CLI output


if __name__ == '__main__':
    asyncio.run(main())
