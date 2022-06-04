from __future__ import annotations

import asyncio
import typing

import toolsql

from ctc import spec
from ... import schema_utils
from . import erc20_metadata_schema_defs


async def async_upsert_erc20_metadata(
    address: spec.Address,
    symbol: str | None = None,
    decimals: int | None = None,
    upsert: bool = True,
    network: spec.NetworkReference | None = None,
    *,
    conn: toolsql.SAConnection,
) -> None:

    # construct row
    row = {
        'address': address.lower(),
        'symbol': symbol,
        'decimals': decimals,
    }
    row = {k: v for k, v in row.items() if v is not None}

    # get upsert option
    if upsert:
        upsert_option: toolsql.ConflictOption | None = 'do_update'
    else:
        upsert_option = None

    # get table name
    table = schema_utils.get_table_name('erc20_metadata', network=network)

    # insert data
    toolsql.insert(
        conn=conn,
        table=table,
        row=row,
        upsert=upsert_option,
    )


async def async_upsert_erc20_metadatas(
    metadatas: typing.Sequence[erc20_metadata_schema_defs.ERC20Metadata],
    network: spec.NetworkReference | None = None,
    *,
    conn: toolsql.SAConnection,
) -> None:
    coroutines = [
        async_upsert_erc20_metadata(conn=conn, network=network, **metadata)
        for metadata in metadatas
    ]
    await asyncio.gather(*coroutines)


async def async_select_erc20_metadata(
    address: spec.Address,
    network: spec.NetworkReference | None = None,
    *,
    conn: toolsql.SAConnection,
) -> erc20_metadata_schema_defs.ERC20Metadata | None:
    table = schema_utils.get_table_name('erc20_metadata', network=network)
    return toolsql.select(
        conn=conn,
        table=table,
        row_id=address.lower(),
        row_count='at_most_one',
        row_format='dict',
        return_count='one',
    )


async def async_select_erc20_metadatas(
    addresses: typing.Sequence[spec.Address],
    network: spec.NetworkReference | None = None,
    *,
    conn: toolsql.SAConnection,
) -> typing.Sequence[erc20_metadata_schema_defs.ERC20Metadata | None] | None:

    table = schema_utils.get_table_name('erc20_metadata', network=network)
    results = toolsql.select(
        conn=conn,
        table=table,
        row_ids=[address.lower() for address in addresses],
    )

    # package into output
    results_by_address = {result['address']: result for result in results}

    return [results_by_address.get(address) for address in addresses]


async def async_delete_erc20_metadata(
    address: spec.Address,
    network: spec.NetworkReference | None = None,
    *,
    conn: toolsql.SAConnection,
) -> None:
    table = schema_utils.get_table_name('erc20_metadata', network=network)
    toolsql.delete(table=table, conn=conn, row_id=address.lower())


async def async_delete_erc20s_metadata(
    addresses: typing.Sequence[spec.Address],
    network: spec.NetworkReference | None = None,
    *,
    conn: toolsql.SAConnection,
) -> None:
    table = schema_utils.get_table_name('erc20_metadata', network=network)
    toolsql.delete(
        table=table,
        conn=conn,
        row_ids=[address.lower() for address in addresses],
    )