from pathlib import Path

import discord
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = Path(__file__).parent.parent / '.env'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=DOTENV, env_file_encoding='utf-8')

    bot_key: SecretStr
    reborn_guild_id: int

    @property
    def reborn_guild_obj(self) -> discord.Object:
        return discord.Object(id=self.reborn_guild_id)

    teable_db_host: str
    teable_db_port: int
    teable_db_user: str
    teable_db_password: SecretStr
    teable_db_db: str

    teable_token: SecretStr
    teable_api_url: str = 'http://127.0.0.1:3000/api'
    teable_db_schema: str = ''
    teable_users_table_id: str = ''
    teable_items_table_id: str = ''
    teable_trader_price_table_id: str = ''
    teable_items_db_table: str = 'items'
    teable_traders_db_table: str = 'traders'
    teable_trader_price_db_table: str = 'trader_price'
    teable_stash_db_table: str = 'stash'
    teable_stash_loot_db_table: str = 'stash_loot'

    configs_repo_path: str
    ssh_key_path: str

    whitelist_path: str
    config_backup_path: str = 'D:\\MyServer\\Backups\\reborn_bot'

    config_git_push_enabled: bool = False
    config_git_remote: str = 'origin'
    config_git_branch: str = 'main'

    # Keep commands that write DayZ files disabled until their data mappings and
    # target paths have been verified against the migrated Teable base.
    enable_questionnaire_commands: bool = False
    enable_economy_commands: bool = False
    enable_whitelist_command: bool = False


settings = Settings()
