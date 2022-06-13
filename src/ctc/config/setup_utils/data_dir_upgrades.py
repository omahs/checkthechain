from __future__ import annotations

import os
import shutil
import typing
from typing_extensions import TypedDict, Literal

import toolcli

from ctc import config


if typing.TYPE_CHECKING:

    class DataDirSpec(TypedDict, total=False):
        # for now, only specifieds entries in root data dir
        files: list[str]  # list of expected file paths
        directories: list[str]  # list of expected directory paths
        directory_contents: typing.Mapping[
            str, typing.Sequence[str]
        ]  # list of items in each directory

    DataSpecVersion = Literal['0.2.0', '0.3.0']


data_spec_order: list[DataSpecVersion] = [
    '0.2.0',
    '0.3.0',
]

data_dir_specs: typing.Mapping[DataSpecVersion, DataDirSpec] = {
    '0.2.0': {
        'files': [],
        'directories': [],
    },
    '0.3.0': {
        'files': [
            'directory_version',
        ],
        'directories': [
            'dbs',
            'logs',
            'evm',
        ],
        'directory_contents': {
            'logs': ['rpc', 'db'],
        },
    },
}


def get_data_dir_version(data_dir: str | None = None) -> DataSpecVersion:
    if data_dir is None:
        data_dir = config.get_data_dir()

    version_file = os.path.join(data_dir, 'directory_version')

    if not os.path.isfile(version_file):
        return '0.2.0'
    else:
        with open(version_file, 'r') as f:
            version = f.read()
        if version in data_spec_order:
            return version
        else:
            raise Exception('unknown data_spec_version: ' + str(version))


def fully_migrate_data_dir(data_dir: str | None = None) -> None:

    if data_dir is None:
        data_dir = config.get_data_dir()

    # detect current version
    current_version = get_data_dir_version()
    latest_version = data_spec_order[-1]
    if current_version == latest_version:
        print('data_dir already fully migrated')
        return

    # gather all migrate functions
    migrate_functions = {
        '0.3.0': migrate_data_dir__0_2_0__to__0_3_0,
    }

    # perform each upgrade function sequentially
    index = data_spec_order.index(current_version)
    steps = data_spec_order[index + 1 :]
    for step in steps:
        migrate_functions[step](data_dir=data_dir)


def migrate_data_dir__0_2_0__to__0_3_0(
    data_dir: str,
    delete_old_data: bool = True,
    confirm_delete: bool = False,
) -> None:

    data_dir_spec = data_dir_specs['0.3.0']

    # create version file
    version_file = os.path.join(data_dir, 'directory_version')
    print('creating new version indicator file:', version_file)
    with open(version_file, 'w') as f:
        f.write('0.3.0')

    # create new directories
    for relpath in data_dir_spec['directories']:
        dirpath = os.path.join(data_dir, relpath)
        print('creating directory:', dirpath)
        os.makedirs(dirpath, exist_ok=True)

    # delete old files
    if delete_old_data:
        to_delete = []
        for item in os.listdir(data_dir):
            if (
                item not in data_dir_spec['directories']
                and item not in data_dir_spec['files']
            ):
                to_delete.append(item)
            elif (
                item in data_dir_spec['directories']
                and item in data_dir_spec['directory_contents']
            ):
                directory_contents = data_dir_spec['directory_contents'][item]
                for subitem in os.listdir(os.path.join(data_dir, item)):
                    if subitem not in directory_contents:
                        to_delete.append(os.path.join(item, subitem))
        if len(to_delete) > 0:
            if not confirm_delete:
                print()
                print('the following files and directories are not used in ctc 0.3.0:')
                for item in sorted(to_delete):
                    print('-', item)
                print()
                if not toolcli.input_yes_or_no('delete these items? '):
                    raise Exception(
                        'migration unfinished, must delete old files'
                    )

            for path in to_delete:
                path = os.path.join(data_dir, path)
                if os.path.isfile(path) or os.path.islink(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    raise Exception('cannot process path: ' + str(path))
