from pathlib import Path

from sqlalchemy import text

from src import settings
from src.db import session_getter
from src.economy.git_repo import GitRepo
from src.economy.schemas import FullTraderSchema
from src.economy.utils import edit_config
from src.exceptions import ValidationError
from src.teable.sql import table_ref

TRADERS_CONFIGS_FOLDER = r'TraderPlus\TraderPlusConfig'

PRICE_CONFIG_FILE_NAME = 'TraderPlusPriceConfig.json'
GENERAL_CONFIG_FILE_NAME = 'TraderPlusGeneralConfig.json'
CATEGORY_CONFIG_FILE_NAME = 'TraderPlusIDsConfig.json'


async def update_traders_configs() -> None:
    git_repo = None
    if settings.config_git_push_enabled:
        git_repo = GitRepo(settings.configs_repo_path, settings.ssh_key_path)
    full_data = await _get_full_traiders_data()

    try:
        await _update_traders_price_config(full_data)
        await _update_traders_config(full_data)
        await _update_traiders_categories(full_data)

        if git_repo is not None:
            git_repo.add_changes()
            if git_repo.commit_changes('Update Traders Configs'):
                git_repo.push_changes(
                    settings.config_git_remote,
                    settings.config_git_branch,
                )
    except Exception as error:
        msg = 'Возникли проблемы, конфиги не были применены'
        raise ValidationError(msg) from error


async def _update_traders_price_config(items: list[FullTraderSchema]) -> None:
    traders_data: dict[str, list[str]] = {}
    for item in items:
        trader = item.trader_name
        category = item.category
        trader_category = f'({trader}) {category}'

        if trader_category not in traders_data:
            traders_data[trader_category] = []

        classname = item.item.title
        coef = item.coefficient
        stock = item.max_stock
        quantity = item.trade_quantity
        price = item.item_price
        buy_price = item.item_buy_price
        traders_data[trader_category].append(
            f'{classname},{coef},{stock},{quantity},{price},{buy_price}'
        )

    formatted_data = []
    for category, products in traders_data.items():
        formatted_data.append({'CategoryName': category, 'Products': products})

    general_config_path = (
        Path(settings.configs_repo_path) / Path(TRADERS_CONFIGS_FOLDER) / Path(PRICE_CONFIG_FILE_NAME)
    )
    await edit_config(general_config_path, 'TraderCategories', formatted_data)


async def _update_traders_config(traders: list[FullTraderSchema]) -> None:
    traders_data = {}
    for trader in traders:
        trader_data = {
            'Id': trader.trader_serial,
            'Name': trader.classname,
            'GivenName': trader.trader_name,
            'Role': '' if trader.role is None else trader.role,
            'Position': [float(i) for i in trader.position.split()],
            'Orientation': [float(i) for i in trader.orientation.split()],
            'Clothes': [] if trader.clothes is None else [i.title for i in trader.clothes],
        }
        traders_data[trader.trader_name] = trader_data

    general_config_path = (
        Path(settings.configs_repo_path) / Path(TRADERS_CONFIGS_FOLDER) / Path(GENERAL_CONFIG_FILE_NAME)
    )
    await edit_config(general_config_path, 'Traders', list(traders_data.values()))


async def _update_traiders_categories(items: list[FullTraderSchema]) -> None:
    categories: dict[str, set[str]] = {}
    id_mapping = {}
    for item in items:
        trader_name = item.trader_name
        if trader_name not in categories:
            categories[trader_name] = set()
        categories[trader_name].add(item.category)
        id_mapping[trader_name] = item.trader_serial

    out_list = []
    for traider_name, category in categories.items():
        traider_dict = {
            'Id': id_mapping[traider_name],
            'Categories': [f'({traider_name}) {i}' for i in category],
            'LicencesRequired': [],
            'CurrenciesAccepted': [],
        }

        out_list.append(traider_dict)

    general_config_path = (
        Path(settings.configs_repo_path) / Path(TRADERS_CONFIGS_FOLDER) / Path(CATEGORY_CONFIG_FILE_NAME)
    )
    await edit_config(general_config_path, 'IDs', out_list)


async def _get_full_traiders_data() -> list[FullTraderSchema]:
    trader_price_table = table_ref(settings.teable_trader_price_db_table)
    traders_table = table_ref(settings.teable_traders_db_table)
    query = f"""
        SELECT
            DENSE_RANK() OVER (ORDER BY t.id) - 1 as trader_serial,
            tp.category,
            tp.item,
            t.name as trader_name,
            tp.item_price,
            tp.item_buy_price,
            tp.max_stock,
            tp.coefficient,
            tp.trade_quantity,
            t.classname,
            t.id as trader_id,
            t.role,
            t.position,
            t.orientation,
            t.clothes
        FROM {trader_price_table} tp
        JOIN {traders_table} t
            ON (tp.trader->>'id')= t.id
        ORDER BY trader_serial, tp.category, tp.item;
    """  # noqa: S608 -- table_ref validates and quotes both identifiers.
    async with session_getter() as session:
        res = await session.execute(text(query))
        return [FullTraderSchema.model_validate(row) for row in res.mappings()]


if __name__ == '__main__':
    import asyncio

    asyncio.run(update_traders_configs())
