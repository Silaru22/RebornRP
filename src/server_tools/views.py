import discord

from src.server_tools.modals import AddWhitelistModal


class AddWhitelistView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label='Добавить в вайтлист', style=discord.ButtonStyle.green)
    async def add_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button['AddWhitelistView'],  # noqa: ARG002
    ) -> None:
        await interaction.response.send_modal(AddWhitelistModal())
