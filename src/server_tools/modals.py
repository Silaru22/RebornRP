from typing import Any

import discord

from src.logger import reborn_logger
from src.server_tools.whitelist import WhitelistServise


class AddWhitelistModal(discord.ui.Modal, title='Добавить в whitelist'):
    whitelist_value: discord.ui.TextInput['AddWhitelistModal'] = discord.ui.TextInput(
        label='Введите значение', placeholder='Например: username или ID', required=True, max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        value = self.whitelist_value.value

        result = await WhitelistServise.add_to_whitelist(value)

        if result:
            await interaction.response.send_message(
                f'✅ `{value}` успешно добавлен в whitelist!', ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f'ℹ️ `{value}` уже находится в whitelist.', ephemeral=True
            )

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Item[Any] | None = None,  # noqa: ARG002
        /,
    ) -> None:
        if isinstance(error, (FileNotFoundError, ValueError)):
            await interaction.response.send_message(str(error), ephemeral=True)
            return
        reborn_logger.error(
            'Whitelist modal failed',
            exc_info=(type(error), error, error.__traceback__),
        )
        await interaction.response.send_message(
            'Не удалось обновить whitelist. Ошибка записана в журнал бота.',
            ephemeral=True,
        )
