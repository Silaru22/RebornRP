import discord
from discord import app_commands
from discord.ext.commands import Bot, Context, errors
from discord.ext.commands._types import BotT

from src.common_tools import MissingTechAdminRole
from src.config import settings
from src.economy.cog import EconomyCog
from src.logger import reborn_logger
from src.quents.cog import QuentsCog
from src.server_tools.cog import ServerToolsCog


class MyBot(Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__('/', intents=intents)
        self.tree.on_error = self.on_app_command_error  # type: ignore[method-assign]

    async def setup_hook(self) -> None:
        await self._setup_extensions()

        self.tree.copy_global_to(guild=settings.reborn_guild_obj)
        await self.tree.sync(guild=settings.reborn_guild_obj)

    async def _setup_extensions(self) -> None:
        if settings.enable_questionnaire_commands:
            await self.add_cog(QuentsCog(self))
        if settings.enable_economy_commands:
            await self.add_cog(EconomyCog(self))
        if settings.enable_whitelist_command:
            await self.add_cog(ServerToolsCog(self))

    async def on_command_error(self, context: Context[BotT], exception: errors.CommandError) -> None:
        return await super().on_command_error(context, exception)

    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ) -> None:
        if isinstance(error, MissingTechAdminRole):
            message = str(error)
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(message, ephemeral=True)
            return

        message = 'Команда не выполнена. Ошибка записана в журнал бота.'
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
        reborn_logger.error(
            'Application command failed',
            exc_info=(type(error), error, error.__traceback__),
        )
