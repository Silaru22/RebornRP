from pathlib import Path

import aiofiles

from src.config import settings


class WhitelistServise:
    @staticmethod
    async def add_to_whitelist(value: str) -> bool:
        clean_value = value.strip()
        if not clean_value or '\n' in clean_value or '\r' in clean_value:
            msg = 'Значение whitelist содержит недопустимые символы'
            raise ValueError(msg)

        file_path = Path(settings.whitelist_path)

        # Если файла нет — ошибка
        if not file_path.is_file():
            msg = f'Файл не найден: {file_path}'
            raise FileNotFoundError(msg)

        # Читаем содержимое, чтобы понять нужен ли перенос строки
        async with aiofiles.open(file_path, encoding='utf-8') as f:
            content = await f.read()

        existing_values = {line.strip() for line in content.splitlines()}
        if clean_value in existing_values:
            return False

        needs_newline = len(content) > 0 and not content.endswith('\n')

        # Добавляем новую строку
        async with aiofiles.open(file_path, mode='a', encoding='utf-8') as f:
            if needs_newline:
                await f.write('\n')
            await f.write(clean_value)

        return True
