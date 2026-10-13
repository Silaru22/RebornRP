import json

import discord
from discord import app_commands
from discord.ext import commands

from src.common_tools import requires_tech_admin
from src.economy.muta import MutantConfig
from src.economy.traders import update_traders_configs
from src.economy.update_item_list import insert_classnames


class EconomyCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name='update_classnames')
    @requires_tech_admin()
    async def add_classnames(self, interaction: discord.Interaction, file: discord.Attachment) -> None:
        await interaction.response.defer(ephemeral=True)
        file_bytes = await file.read()
        server_items = json.loads(file_bytes.decode())
        if not isinstance(server_items, dict):
            msg = 'Ожидался JSON-объект вида {"classname": "Название"}'
            raise TypeError(msg)

        await insert_classnames(server_items)
        await interaction.edit_original_response(content='Успешно')

    @app_commands.command(name='update_traders')
    @requires_tech_admin()
    async def update_traders(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        await update_traders_configs()
        await interaction.edit_original_response(content='Успешно. Трейдеры обновлены')

    @app_commands.command(name='update_muta')
    @requires_tech_admin()
    async def update_mutants(self, interaction: discord.Interaction, file: discord.Attachment) -> None:
        await interaction.response.defer(ephemeral=True)
        file_bytes = await file.read()
        file_data = file_bytes.decode()

        config = MutantConfig()

        await config.create_mutant_configs(file_data)
        await interaction.edit_original_response(content='Успешно')
