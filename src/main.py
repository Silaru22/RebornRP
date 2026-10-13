import logging

import discord

from src.bot import MyBot
from src.config import settings

discord.utils.setup_logging(level=logging.INFO, root=True)

bot = MyBot()
bot.run(settings.bot_key.get_secret_value(), log_handler=None)
