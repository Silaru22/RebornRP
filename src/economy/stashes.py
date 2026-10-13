import asyncio
import xml.etree.ElementTree as ET

import aiofiles
from defusedxml.minidom import parseString
from sqlalchemy import text

from src.config import settings
from src.db import session_getter
from src.economy.schemas import StashesSchema, StashLootSchema
from src.teable.sql import table_ref


async def create_stashsearch_xml() -> None:
    stash_table = table_ref(settings.teable_stash_db_table)
    stash_loot_table = table_ref(settings.teable_stash_loot_db_table)
    stash_query = f"""
        SELECT
            tier, chancetoappear, chancetoloot, minspawncount, maxspawncount,
            mintimetoresetsearched, maxtimetoresetsearched, mintooldmg, maxtooldmg
        FROM {stash_table}
    """  # noqa: S608 -- table_ref validates and quotes the identifier.
    async with session_getter() as session:
        res = await session.execute(text(stash_query))
    stashes_data = [StashesSchema.model_validate(row) for row in res.mappings()]

    loot_query = f"""
        SELECT tier, item, trade_quantity
        FROM {stash_loot_table}
    """  # noqa: S608 -- table_ref validates and quotes the identifier.
    async with session_getter() as session:
        res = await session.execute(text(loot_query))
    lootitems_data = [StashLootSchema.model_validate(row) for row in res.mappings()]

    root = ET.Element('stashsearch', log='false')

    for stash in stashes_data:
        stashes_elem = ET.SubElement(
            root,
            'stashes',
            tier=stash.tier,
            chancetoappear=stash.chancetoappear,
            chancetoloot=stash.chancetoloot,
            minspawncount=stash.minspawncount,
            maxspawncount=stash.maxspawncount,
            mintimetoresetsearched=stash.mintimetoresetsearched,
            maxtimetoresetsearched=stash.maxtimetoresetsearched,
            mintooldmg=stash.mintooldmg,
            maxtooldmg=stash.maxtooldmg,
        )

        await add_lootitems_for_tier(stashes_elem, lootitems_data, stash.tier)

        async with aiofiles.open('test.xml', 'w') as f:
            await f.write(prettify_xml(root))


async def add_lootitems_for_tier(
    stashes_elem: ET.Element, lootitems_data: list[StashLootSchema], tier: str
) -> None:
    for loot_record in lootitems_data:
        if loot_record.tier.title == tier:
            classname = loot_record.item.title

            quantity = 1 if loot_record.trade_quantity is None else loot_record.trade_quantity

            ET.SubElement(stashes_elem, 'lootitem', name=classname, min=str(quantity))


def prettify_xml(elem: ET.Element) -> str:
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = parseString(rough_string)
    return reparsed.toprettyxml(indent='\t')


if __name__ == '__main__':
    asyncio.run(create_stashsearch_xml())
