import discord

from src.enums import RoleEnum
from src.exceptions import ValidationError


def is_curator(user: discord.Member | discord.User) -> bool:
    if isinstance(user, discord.User):
        msg = 'Вы не находитесь на сервере'
        raise ValidationError(msg)
    curator_roles = [RoleEnum.kurator, RoleEnum.admin, RoleEnum.dev_admin, RoleEnum.iventer]
    return any(user_role.name in curator_roles for user_role in user.roles)


def check_curator_permission(user: discord.Member | discord.User) -> None:
    if not is_curator(user):
        msg = 'Не достаточно прав'
        raise ValidationError(msg)
