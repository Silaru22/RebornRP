from enum import StrEnum
from typing import Any

import discord
from pydantic import BaseModel


class StatusEnum(StrEnum):
    created = 'Создана'
    approved = 'Одобрена'
    dead = 'РПК'


class QuentRecordCreateSchema(BaseModel):
    nickname: str
    status: StatusEnum
    steam_id: str
    quent_link: str
    birth_date: str
    discord_slug: str
    discord_id: str
    discord_channel_id: str
    character_name: str


class QuentRecordSchema(QuentRecordCreateSchema):
    id: str

    @classmethod
    def from_teable_record(cls, record: dict[str, Any]) -> 'QuentRecordSchema':
        return cls.model_validate({'id': record['id'], **record['fields']})


def get_init_quent_message() -> discord.Embed:
    embed = discord.Embed(
        title='📜 Инструкция для новых игроков',
        description=(
            'Добро пожаловать на наш проект!Чтобы начать играть, выполни несколько простых шагов:'
        ),
        color=discord.Color.dark_blue(),
    )
    embed.add_field(
        name='1️⃣ Ознакомься с Лором и Правилами проекта',
        value="""
                    Прежде чем создавать персонажа, важно понять мир, в котором ты окажешься, и правила поведения в нем. Это поможет тебе лучше вжиться в роль и избежать недоразумений.

                    [Лор](https://docs.google.com/document/d/1kjrqeavgb_jW-nY1-wJL6SngPVtm4GasXatON6voAn8/edit?tab=t.0)
                    [Правила проекта](https://docs.google.com/document/d/1nvuB6u2ZEcFrScBD6WcQkGbDQIs1evR6LZZKOIwV8-c/edit?tab=t.0#heading=h.ew864oasviwk)
                    """,  # noqa: E501
        inline=False,
    )
    embed.add_field(
        name='2️⃣ Подать анкету вашего персонажа с помощью автоматизированной формы',
        value="""
                    Расскажи нам о том, кого ты хочешь отыгрывать. Заполни все поля формы внимательно и творчески — от этого зависит твой будущий игровой опыт.

                    *Кнопка для подачи анкеты находится ниже этого сообщения.*
                    """,  # noqa: E501
        inline=False,
    )
    embed.add_field(
        name='3️⃣ Подписаться на актуальную коллекцию модификаций в Steam',
        value="""
                    Для корректной работы сервера и доступа ко всему контенту необходимо подписаться на нашу [коллекцию](https://steamcommunity.com/sharedfiles/filedetails/?id=3528585373) модов.
                    """,  # noqa: E501
        inline=False,
    )
    embed.add_field(
        name='4️⃣ Присоединиться к серверу',
        value="""
                    Когда анкета будет одобрена, а моды загружены, ты сможешь войти в игру. Используй для этого следующие данные:

                    **IP-адрес:** 109.173.108.217:2302
                    """,  # noqa: E501
        inline=False,
    )
    return embed
