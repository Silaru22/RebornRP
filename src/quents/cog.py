import discord
from discord import app_commands
from discord.ext import commands

from src.common_tools import requires_tech_admin
from src.exceptions import ValidationError
from src.quents.schemas import get_init_quent_message
from src.quents.views import DeleteQuestionnaireView, InitQuentView, QuentSubmitView


class QuentsCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.add_view(InitQuentView())
        self.bot.add_view(QuentSubmitView())
        self.bot.add_view(DeleteQuestionnaireView())

    @app_commands.command(name='init_quent_button', description='Отправить кнопку для создания квенты')
    @requires_tech_admin()
    @app_commands.guild_only
    async def init_quent_button(self, interaction: discord.Interaction) -> None:
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            msg = 'Не верный тип канала'
            raise ValidationError(msg)
        await channel.send('', view=InitQuentView(), embed=get_init_quent_message())
        await interaction.response.send_message('Complete!', ephemeral=True)
