import re
from typing import Any

import discord
from discord import ui

from src import teable
from src.common_tools import find_named_role
from src.enums import RoleEnum
from src.exceptions import NotFoundError, ValidationError
from src.quents.schemas import QuentRecordCreateSchema, StatusEnum
from src.teable.repository import Tables


class KventaModal(ui.Modal, title='Одобрение квенты'):
    steam_id: ui.TextInput['KventaModal'] = ui.TextInput(
        label='Steam ID',
        placeholder='Введите числовой Steam ID',
        required=True,
        max_length=50,
    )
    nickname: ui.TextInput['KventaModal'] = ui.TextInput(
        label='Позывной (Латиница)',
        placeholder='Позывной персонажа',
        required=True,
        max_length=50,
    )
    character_name: ui.TextInput['KventaModal'] = ui.TextInput(
        label='Имя персонажа',
        placeholder='Имя и фамилия персонажа',
        required=True,
        max_length=50,
    )
    birth_date: ui.TextInput['KventaModal'] = ui.TextInput(
        label='Дата рождения персонажа',
        placeholder='Например: 12.04.1998',
        required=True,
        max_length=50,
    )
    quent_link: ui.TextInput['KventaModal'] = ui.TextInput(
        label='Ссылка на квенту (Google Документ)',
        style=discord.TextStyle.paragraph,
        placeholder='https://docs.google.com/...',
        required=True,
        max_length=500,
    )

    def __init__(self, approve_view: discord.ui.View) -> None:
        super().__init__()
        self.approve_view = approve_view

    async def on_submit(self, interaction: discord.Interaction) -> None:
        guild, user = await self._check_dm_message(interaction)

        await self._validate_data()
        quent_channel = await self._create_quent_channel(guild, user)

        await self._save_quent(user, quent_channel.id)
        await self._send_quent_message(quent_channel, user)

        await interaction.response.send_message(
            'Спасибо! Администрация проверит вашу заявку в ближайшее время',
            ephemeral=True,
        )

    async def _check_dm_message(
        self, interaction: discord.Interaction
    ) -> tuple[discord.Guild, discord.Member]:
        guild = interaction.guild
        user = interaction.user
        if not isinstance(guild, discord.Guild):
            msg = 'Сообщение должно быть отправлено на дискорд сервере'
            raise ValidationError(msg)

        if not isinstance(user, discord.Member):
            msg = 'Сообщение должно быть отправлено на дискорд сервере'
            raise ValidationError(msg)

        return guild, user

    async def _validate_data(self) -> None:
        steam_id = self.steam_id.value
        if not steam_id.isdigit():
            msg = 'Steam ID должен содержать только цифры'
            raise ValidationError(msg)

        if len(steam_id) != 17:  # noqa: PLR2004    17 is a lenght of SteamId64
            msg = 'Steam id указан не правильно'
            raise ValidationError(msg)

        if re.fullmatch(r'[a-zA-Z]+', self.nickname.value) is None:
            msg = 'Позывной должен содержать только Латинские буквы'
            raise ValidationError(msg)

        if not self.quent_link.value.startswith('https://docs.google.com'):
            msg = 'Ссылка дожна быть на Google Документ'
            raise ValidationError(msg)

    async def _save_quent(self, user: discord.Member, channel_id: int) -> None:
        quent = QuentRecordCreateSchema(
            nickname=self.nickname.value,
            character_name=self.character_name.value,
            birth_date=self.birth_date.value,
            quent_link=self.quent_link.value,
            status=StatusEnum.created.value,
            steam_id=self.steam_id.value,
            discord_slug=user.name,
            discord_id=str(user.id),
            discord_channel_id=str(channel_id),
        )

        await teable.create_record(Tables.users(), quent.model_dump())

    async def _create_quent_channel(
        self, guild: discord.Guild, user: discord.Member
    ) -> discord.TextChannel:
        category = await self._get_quent_category(guild)
        channel_permissions = await self._get_channel_permission(guild, user)

        return await guild.create_text_channel(
            name=f'квента-{user.name}', overwrites=channel_permissions, category=category
        )

    async def _get_quent_category(self, guild: discord.Guild) -> discord.CategoryChannel:
        category_name = 'Квентовая'
        category = discord.utils.get(guild.categories, name=category_name)
        if category is None:
            msg = 'Category not found'
            raise NotFoundError(msg)
        return category

    async def _get_channel_permission(
        self, guild: discord.Guild, user: discord.User | discord.Member
    ) -> dict[Any, discord.PermissionOverwrite]:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            ),
        }

        staff_roles = [RoleEnum.kurator, RoleEnum.admin, RoleEnum.dev_admin, RoleEnum.iventer]
        for role_name in staff_roles:
            role = find_named_role(guild.roles, role_name)
            if role is None:
                msg = 'Права доступа настроены не правильно!'
                raise ValidationError(msg)
            overwrites[role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            )
        return overwrites

    async def _send_quent_message(
        self, quent_channel: discord.TextChannel, user: discord.Member
    ) -> None:
        embed = discord.Embed(
            title='Квента',
            color=discord.Color.green(),
        )
        embed.add_field(name='Пользователь', value=user.mention, inline=False)
        embed.add_field(name='Позывной', value=self.nickname.value, inline=False)
        embed.add_field(name='Имя персонажа', value=self.character_name.value, inline=False)
        embed.add_field(name='Дата рождения', value=self.birth_date.value, inline=False)
        embed.add_field(name='Квента', value=self.quent_link.value, inline=False)

        await quent_channel.send(embed=embed, view=self.approve_view)

    # https://github.com/Rapptz/discord.py/issues/9816
    async def on_error(  # type: ignore
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        if isinstance(error, ValidationError):
            await interaction.response.send_message(str(error), ephemeral=True)
            return None

        return await super().on_error(interaction, error)
