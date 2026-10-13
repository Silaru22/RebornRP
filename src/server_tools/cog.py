import discord
from discord import app_commands
from discord.ext import commands

from src.common_tools import requires_tech_admin
from src.server_tools.modals import AddWhitelistModal


class ServerToolsCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name='add_white_list', description='Добавить в вайт лист')
    @requires_tech_admin()
    async def add_white_list(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(AddWhitelistModal())
