from enum import StrEnum


class RoleEnum(StrEnum):
    kurator = 'Куратор'
    admin = 'Администратор'
    dev_admin = 'Тех. администратор'
    iventer = 'Ивентолог'


class TargetChannels(StrEnum):
    quents = '🟩квенты'
