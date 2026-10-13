import re
from collections.abc import Callable, Iterable
from typing import TypeVar

import discord
from discord import app_commands

from src.enums import RoleEnum
from src.exceptions import ValidationError


class MissingTechAdminRole(app_commands.CheckFailure):
    def __init__(self) -> None:
        super().__init__(f'Команда доступна только роли «{RoleEnum.dev_admin}».')


CommandT = TypeVar('CommandT')


def _normalized_role_name(name: str) -> str:
    return re.sub(r'\s+', '', name).casefold()


def has_named_role(user: discord.Member | discord.User, role_name: str) -> bool:
    if not isinstance(user, discord.Member):
        return False
    expected = _normalized_role_name(role_name)
    return any(_normalized_role_name(role.name) == expected for role in user.roles)


def find_named_role(roles: Iterable[discord.Role], role_name: str) -> discord.Role | None:
    expected = _normalized_role_name(role_name)
    return next(
        (role for role in roles if _normalized_role_name(role.name) == expected),
        None,
    )


def requires_tech_admin() -> Callable[[CommandT], CommandT]:
    async def predicate(interaction: discord.Interaction) -> bool:
        if not has_named_role(interaction.user, RoleEnum.dev_admin):
            raise MissingTechAdminRole
        return True

    return app_commands.check(predicate)


def is_curator(user: discord.Member | discord.User) -> bool:
    if isinstance(user, discord.User):
        msg = 'Вы не находитесь на сервере'
        raise ValidationError(msg)
    curator_roles = [RoleEnum.kurator, RoleEnum.admin, RoleEnum.dev_admin, RoleEnum.iventer]
    return any(has_named_role(user, role_name) for role_name in curator_roles)


def check_curator_permission(user: discord.Member | discord.User) -> None:
    if not is_curator(user):
        msg = 'Не достаточно прав'
        raise ValidationError(msg)
