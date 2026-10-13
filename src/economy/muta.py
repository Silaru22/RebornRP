import json
from pathlib import Path
from typing import TypedDict
from xml.etree.ElementTree import Element

from defusedxml.ElementTree import fromstring

from src import ValidationError, settings
from src.economy.git_repo import GitRepo
from src.economy.utils import (
    OTHER_CONFIG_PATH,
    atomic_write_text,
    backup_config_file,
    edit_config,
)


class MutantSpawnConfig(TypedDict):
    classnames: list[str]
    spawnMin: int
    spawnMax: int


hardcoded_dict: dict[str, MutantSpawnConfig] = {
    'plotb t1': {'classnames': ['BRDK_Flash'], 'spawnMin': 3, 'spawnMax': 4},
    'plotb t2': {'classnames': ['BRDK_Flash'], 'spawnMin': 4, 'spawnMax': 6},
    'piyavka t1': {'classnames': ['SFP_Piyavka'], 'spawnMin': 1, 'spawnMax': 1},
    'piyavka t2': {'classnames': ['SFP_Piyavka'], 'spawnMin': 2, 'spawnMax': 2},
    'piyavka t3': {'classnames': ['SFP_Piyavka'], 'spawnMin': 3, 'spawnMax': 3},
    'tark t1': {'classnames': ['JVDS_Tark'], 'spawnMin': 1, 'spawnMax': 1},
    'zombie volk t1': {'classnames': ['FC_Animal_WolfShabby'], 'spawnMin': 3, 'spawnMax': 4},
    'zombie volk t2': {'classnames': ['FC_Animal_WolfShabby'], 'spawnMin': 5, 'spawnMax': 7},
    'tushkan t1': {'classnames': ['BRDK_Tushkan'], 'spawnMin': 3, 'spawnMax': 5},
    'cat baun t1': {'classnames': ['SFP_CatBaun_Lor'], 'spawnMin': 1, 'spawnMax': 2},
    'slepie sobaki t1': {
        'classnames': ['BRDK_BlindDog_BROWN_crs', 'BRDK_BlindDog_WHITE_crs', 'BRDK_BlindDog_crs'],
        'spawnMin': 4,
        'spawnMax': 5,
    },
    'slepie sobaki t2': {
        'classnames': ['BRDK_BlindDog_BROWN_crs', 'BRDK_BlindDog_WHITE_crs', 'BRDK_BlindDog_crs'],
        'spawnMin': 6,
        'spawnMax': 8,
    },
    'boar t1': {'classnames': ['JVDS_BOAR'], 'spawnMin': 3, 'spawnMax': 4},
    'boar t2': {'classnames': ['JVDS_BOAR'], 'spawnMin': 5, 'spawnMax': 6},
    'himera t1': {'classnames': ['BRDK_Chimera_crs'], 'spawnMin': 1, 'spawnMax': 1},
    'zombie t1': {
        'classnames': [
            'BRDK_CivZomby_1',
            'BRDK_CivZomby_2',
            'BRDK_CivZomby_3',
            'BRDK_CivZomby_4',
            'BRDK_CivZomby_5',
            'BRDK_CivZomby_6',
        ],
        'spawnMin': 2,
        'spawnMax': 4,
    },
    'zombie vanil t1': {
        'classnames': [
            'BRDK_CivZomby_1',
            'BRDK_CivZomby_2',
            'BRDK_CivZomby_3',
            'BRDK_CivZomby_4',
            'BRDK_CivZomby_5',
            'BRDK_CivZomby_6',
        ],
        'spawnMin': 2,
        'spawnMax': 4,
    },
    'zombie t2': {
        'classnames': [
            'BRDK_CivZomby_1',
            'BRDK_CivZomby_2',
            'BRDK_CivZomby_3',
            'BRDK_CivZomby_4',
            'BRDK_CivZomby_5',
            'BRDK_CivZomby_6',
        ],
        'spawnMin': 4,
        'spawnMax': 6,
    },
    'krisovolk t1': {
        'classnames': [
            'JVDS_Watchman',
            'JVDS_Watchman_v2',
            'JVDS_Watchman_v3',
        ],
        'spawnMin': 3,
        'spawnMax': 4,
    },
    'krisovolk t2': {
        'classnames': [
            'JVDS_Watchman',
            'JVDS_Watchman_v2',
            'JVDS_Watchman_v3',
        ],
        'spawnMin': 5,
        'spawnMax': 8,
    },
    'krisovolk t3': {
        'classnames': [
            'JVDS_Watchman',
            'JVDS_Watchman_v2',
            'JVDS_Watchman_v3',
        ],
        'spawnMin': 8,
        'spawnMax': 10,
    },
    'zombie vanil t2': {
        'classnames': [
            'BRDK_CivZomby_1',
            'BRDK_CivZomby_2',
            'BRDK_CivZomby_3',
            'BRDK_CivZomby_4',
            'BRDK_CivZomby_5',
            'BRDK_CivZomby_6',
        ],
        'spawnMin': 4,
        'spawnMax': 6,
    },
    'zombie seva t3': {
        'classnames': ['BRDK_SevaDolg_zmb'],
        'spawnMin': 1,
        'spawnMax': 1,
    },
    'krovosos t1': {
        'classnames': ['BRDK_Krovosos_1'],
        'spawnMin': 1,
        'spawnMax': 1,
    },
    'krovosos t2': {
        'classnames': ['BRDK_Krovosos_2'],
        'spawnMin': 1,
        'spawnMax': 1,
    },
    'medvedb vanil t1': {
        'classnames': ['animal_ursusarctos'],
        'spawnMin': 1,
        'spawnMax': 1,
    },
    'urus t1': {
        'classnames': ['FC_Animal_BearUrus_M'],
        'spawnMin': 1,
        'spawnMax': 1,
    },
    'snorki t1': {'classnames': ['SMCS_Snork'], 'spawnMin': 3, 'spawnMax': 4},
    'olenb vanil t1': {
        'classnames': ['Animal_OvisAries', 'Animal_OvisAriesF'],
        'spawnMin': 0,
        'spawnMax': 0,
    },
    'himera t2': {'classnames': ['BRDK_Chimera_black_crs'], 'spawnMin': 1, 'spawnMax': 1},
    'controler t1': {'classnames': ['BRDK_Kontroler'], 'spawnMin': 1, 'spawnMax': 1},
    'shipastie t1': {'classnames': ['SFP_Shipastiy'], 'spawnMin': 2, 'spawnMax': 3},
    'poltergaist t1': {'classnames': ['BRDK_Polter'], 'spawnMin': 1, 'spawnMax': 1},
    'psevdo pes t1': {'classnames': ['BRDK_PseudoDog_crs'], 'spawnMin': 1, 'spawnMax': 1},
}


MUTANT_FOLDER = 'MPG_Spawner'
POINTS_FOLDER = 'Points'
CONFIG_FILE_NAME = 'Config.json'

POINTS_FOLDER_PATH = Path(settings.configs_repo_path) / Path(MUTANT_FOLDER) / Path(POINTS_FOLDER)
CONFIG_FOLDER_PATH = Path(settings.configs_repo_path) / Path(MUTANT_FOLDER) / Path(CONFIG_FILE_NAME)


class MutantConfig:
    def __init__(self) -> None:
        self.point_id = 1
        self.file_names: list[str] = []

    async def create_mutant_configs(self, economy_file_data: str) -> None:
        try:
            tree = fromstring(economy_file_data)
            self._validate_tree(tree)
            self.point_id = 1
            self.file_names = []

            git_repo = None
            if settings.config_git_push_enabled:
                git_repo = GitRepo(settings.configs_repo_path, settings.ssh_key_path)

            hand_made_configs = await self._delete_generated_and_get_handmade(POINTS_FOLDER_PATH)
            self.file_names = self.file_names + hand_made_configs

            for territory_type in tree.findall('.//territory-type'):
                await self._create_point_config(territory_type)

            await edit_config(CONFIG_FOLDER_PATH, 'pointsConfigs', self.file_names)
            await self._update_xml(economy_file_data)
            if git_repo is not None:
                git_repo.add_changes()
                if git_repo.commit_changes('Update Mutant Configs'):
                    git_repo.push_changes(
                        settings.config_git_remote,
                        settings.config_git_branch,
                    )
        except Exception as error:
            msg = 'Возникли проблемы, конфиги не были применены'
            raise ValidationError(msg) from error

    def _validate_tree(self, tree: Element) -> None:
        territory_types = tree.findall('.//territory-type')
        if not territory_types:
            msg = 'В XML не найдено ни одного territory-type'
            raise ValidationError(msg)

        for territory_type in territory_types:
            if territory_type.get('name') is None:
                msg = 'В territory-type отсутствует обязательный атрибут name'
                raise ValidationError(msg)
            for territory in territory_type.findall('territory'):
                self._get_mutant_config(territory.get('name'))
                for zone in territory.findall('zone'):
                    self._validate_zone(zone)

    @staticmethod
    def _validate_zone(zone: Element) -> None:
        if any(zone.get(attribute) is None for attribute in ('x', 'z', 'r')):
            msg = 'В zone отсутствует один из атрибутов x, z или r'
            raise ValidationError(msg)

    async def _create_point_config(self, territory_type: Element) -> None:
        territory_type_name = territory_type.get('name')
        if territory_type_name is None:
            msg = 'Unexpected error'
            raise ValidationError(msg)
        territories = []

        for territory in territory_type.findall('territory'):
            muta_class = self._get_mutant_config(territory.get('name'))

            for zone in territory.findall('zone'):
                x = zone.get('x')
                z = zone.get('z')
                r = zone.get('r')

                position = f'{x} 0.0 {z}'

                territory_data = {
                    'pointId': self.point_id,
                    'isDebugEnabled': 0,
                    'isDisabled': 0,
                    'showVisualisation': 0,
                    'notificationTitle': f'Pos {self.point_id}',
                    'notificationTextEnter': '',
                    'notificationTextExit': '',
                    'notificationTextSpawn': '',
                    'notificationTextWin': '',
                    'notificationTime': 8,
                    'notificationIcon': 'set:dayz_inventory image:electricity',
                    'triggerDependencies': [],
                    'triggerDependenciesAnyOf': 0,
                    'triggersToEnableOnEnter': [],
                    'triggersToEnableOnFirstSpawn': [],
                    'triggersToEnableOnWin': [],
                    'triggersToEnableOnLeave': [],
                    'triggerPosition': position,
                    'triggerDebugColor': 'red',
                    'triggerRadius': r,
                    'triggerHeight': '',
                    'triggerWidthX': '',
                    'triggerWidthY': '',
                    'triggerFirstDelay': '180',
                    'triggerCooldown': '600-1800',
                    'triggerSafeDistance': 50.0,
                    'triggerEnterDelay': 0,
                    'triggerCleanupOnLeave': 0,
                    'triggerCleanupOnLunchTime': 0,
                    'triggerCleanupImmersive': 0,
                    'triggerCleanupDelay': 0,
                    'triggerInactiveResetDelay': 0,
                    'triggerWorkingTime': '0-24',
                    'triggerDisableOnWin': 0,
                    'triggerDisableOnLeave': 0,
                    'spawnPositions': [position],
                    'spawnRadius': 15.0,
                    'spawnMin': muta_class['spawnMin'],
                    'spawnMax': muta_class['spawnMax'],
                    'spawnCountLimit': 0,
                    'spawnLoopInside': 0,
                    'spawnQueueDelay': 0,
                    'spawnList': muta_class['classnames'],
                    'clearDeathAnimals': 0,
                    'clearDeathZombies': 0,
                    'mappingData': [],
                }

                territories.append(territory_data)
                self.point_id += 1

        file_name = territory_type_name
        self.file_names.append(file_name)

        POINTS_FOLDER_PATH.mkdir(parents=True, exist_ok=True)
        output_path = POINTS_FOLDER_PATH / Path(territory_type_name).with_suffix('.json')
        if output_path.exists():
            backup_config_file(output_path)
        await atomic_write_text(
            output_path,
            json.dumps(territories, indent=4, ensure_ascii=False),
        )

    @staticmethod
    def _get_mutant_config(npc_class_name: str | None) -> MutantSpawnConfig:
        if npc_class_name is None:
            msg = 'В territory отсутствует обязательный атрибут name'
            raise ValidationError(msg)
        npc_key = npc_class_name.lower()
        if npc_key not in hardcoded_dict:
            msg = f'Не прописан данный тип: {npc_key}'
            raise ValidationError(msg)
        return hardcoded_dict[npc_key]

    async def _delete_generated_and_get_handmade(self, folder: Path) -> list[str]:
        """Returns list of handmade configs"""
        hand_made_configs = []

        folder = Path(folder)
        for item in folder.iterdir():
            if item.is_file():
                if item.name.endswith('_hnd.json'):
                    hand_made_configs.append(item.stem)
                elif item.suffix == '.json':
                    backup_config_file(item)
                    item.unlink()
        return hand_made_configs

    async def _update_xml(self, file_data: str) -> None:
        OTHER_CONFIG_PATH.mkdir(parents=True, exist_ok=True)
        await atomic_write_text(OTHER_CONFIG_PATH / 'project.xml', file_data)
