import json

import discord

from src import reborn_logger, teable
from src.common_tools import check_curator_permission
from src.enums import TargetChannels
from src.exceptions import ValidationError
from src.quents.modals import KventaModal
from src.quents.schemas import QuentRecordSchema, StatusEnum
from src.teable.repository import Tables


class DeleteQuestionnaireView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(
        label='Да', style=discord.ButtonStyle.danger, custom_id='quent:channel_delete_confirm'
    )
    async def confirm(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button['DeleteQuestionnaireView'],  # noqa: ARG002
    ) -> None:
        check_curator_permission(interaction.user)

        await interaction.response.edit_message(content='Канал будет удалён...')
        await self._delete_ticket_channel(interaction)

    async def _delete_ticket_channel(self, interaction: discord.Interaction) -> None:
        if not isinstance(interaction.channel, discord.TextChannel):
            msg = 'Не верный тип канала'
            raise ValidationError(msg)

        await interaction.channel.delete(
            reason=f'Квента {interaction.channel.name} удалена пользователем {interaction.user}'
        )

    @discord.ui.button(
        label='Нет', style=discord.ButtonStyle.secondary, custom_id='quent:channel_delete_cancel'
    )
    async def cancel(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button['DeleteQuestionnaireView'],  # noqa: ARG002
    ) -> None:
        check_curator_permission(interaction.user)

        await interaction.response.edit_message(content='Удаление отменено.')

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Item['DeleteQuestionnaireView'],
    ) -> None:
        if isinstance(error, ValidationError):
            await interaction.response.send_message(str(error), ephemeral=True)
            return None

        return await super().on_error(interaction, error, item)


class QuentSubmitView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(
        label='Одобрить квенту', style=discord.ButtonStyle.success, custom_id='quent:approve'
    )
    async def approve_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button['QuentSubmitView'],  # noqa: ARG002
    ) -> None:
        check_curator_permission(interaction.user)
        guild, user = await self._check_dm_message(interaction)

        quent_record = await self._get_user_quent_record(interaction)
        quent_record = await self._update_status(quent_record.id)

        await self._log_to_discord(guild, user, quent_record)
        await self._change_player_nickname(guild, quent_record)

        await interaction.response.send_message(
            content='Квента одобрена и сохранена. Удалить этот канал?', view=DeleteQuestionnaireView()
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

    async def _get_user_quent_record(self, interaction: discord.Interaction) -> QuentRecordSchema:
        filter_query = json.dumps(
            {
                'conjunction': 'and',
                'filterSet': [
                    {
                        'fieldId': 'discord_channel_id',
                        'operator': 'is',
                        'value': str(interaction.channel_id),
                    },
                    {'fieldId': 'status', 'operator': 'is', 'value': 'Создана'},
                ],
            }
        )
        response = await teable.get_records(
            table_id=Tables.users(),
            params={'filter': filter_query},
        )
        records = response.json()['records']
        if len(records) == 0:
            msg = 'Квента не найдена в базе!'
            raise ValidationError(msg)

        return QuentRecordSchema.from_teable_record(records[0])

    async def _update_status(self, quent_record_id: str) -> QuentRecordSchema:
        response = await teable.update_record(
            Tables.users(), quent_record_id, {'status': StatusEnum.approved.value}
        )
        return QuentRecordSchema.from_teable_record(response.json())

    async def _log_to_discord(
        self, guild: discord.Guild, user: discord.Member, quent_data: QuentRecordSchema
    ) -> None:
        admin_log_channel = discord.utils.get(guild.text_channels, name=TargetChannels.quents)

        if admin_log_channel is None:
            msg = 'Ошибка при логировании, не найден канал администрации'
            raise ValidationError(msg)

        embed = discord.Embed(
            title=f'Одобрена квента игрока {quent_data.nickname}',
            description=f'Модератор: {user.mention}',
            color=discord.Color.green(),
        )
        reborn_logger.info(quent_data)
        embed.add_field(name='Пользователь', value=f'<@{quent_data.discord_id}>', inline=False)
        embed.add_field(name='Steam ID', value=quent_data.steam_id, inline=False)
        embed.add_field(name='Позывной', value=quent_data.nickname, inline=False)
        embed.add_field(name='Имя персонажа', value=quent_data.character_name, inline=False)
        embed.add_field(name='Квента', value=quent_data.quent_link, inline=False)
        await admin_log_channel.send(embed=embed)

    async def _change_player_nickname(self, guild: discord.Guild, quent_data: QuentRecordSchema) -> None:
        user = await guild.fetch_member(int(quent_data.discord_id))
        await user.edit(nick=quent_data.nickname)

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Item['QuentSubmitView'],
    ) -> None:
        if isinstance(error, ValidationError):
            await interaction.response.send_message(str(error), ephemeral=True)
            return None

        return await super().on_error(interaction, error, item)


class InitQuentView(discord.ui.View):
    def __init__(self, *, persistent: bool = True) -> None:
        super().__init__(timeout=None)
        self.persistent = persistent

    @discord.ui.button(
        label='Подать квенту', style=discord.ButtonStyle.success, custom_id='quent:create'
    )
    async def add_quent(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button['InitQuentView'],  # noqa: ARG002
    ) -> None:
        await interaction.response.send_modal(KventaModal(QuentSubmitView()))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        reborn_logger.info(
            f'[{interaction.user.id}] {interaction.user.name} Press on button to create quent ticket'
        )
        filter_query = json.dumps(
            {
                'conjunction': 'and',
                'filterSet': [
                    {'fieldId': 'status', 'operator': 'isAnyOf', 'value': ['Создана', 'Одобрена']},
                    {'fieldId': 'discord_id', 'operator': 'is', 'value': str(interaction.user.id)},
                ],
            }
        )
        response = await teable.get_records(
            table_id=Tables.users(),
            params={'filter': filter_query},
        )
        users_quents = response.json()['records']

        if len(users_quents) > 0:
            msg = 'Вы имеете более 1 заявки на квенту или активного персонажа'
            await interaction.response.send_message(msg, ephemeral=True)
            return False

        return True
