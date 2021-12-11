import typing

from ctc import evm
from ctc import spec
from ctc.protocols import balancer_utils

from .. import analytics_spec


async def async_compute_buybacks(
    blocks: list[int], verbose: bool = False
) -> analytics_spec.MetricGroup:

    return {
        'name': 'Buybacks',
        'metrics': [
            compute_tribe_buybacks_usd(blocks)
        ],
    }


def compute_tribe_buybacks_usd(
    blocks: list[int], swaps: typing.Optional[spec.DataFrame] = None
) -> analytics_spec.MetricData:

    # load swaps
    if swaps is None:
        swaps = balancer_utils.get_pool_swaps(
            pool_address='0xc1382fe6e17bcdbc3d35f73f5317fbf261ebeecd'
        )
    swaps = swaps.droplevel('transaction_index').droplevel('log_index')

    # filter tribe buys
    fei = '0x956f47f50a910163d8bf957cf5846d573e7f87ca'
    tribe_buys: typing.Any = swaps[swaps['arg__tokenOut'] == fei]  # type: ignore
    tribe_buys = tribe_buys['arg__amountOut'].map(float) / 1e18
    cummulative_tribe_buys = tribe_buys.cumsum()
    cummulative_tribe_buys = evm.interpolate_block_series(
        start_block=min(blocks),
        pre_fill_value=0,
        series=cummulative_tribe_buys,
        end_block=max(blocks),
    )

    # filter tribe sells
    tribe_sells = swaps[swaps['arg__tokenIn'] == fei]  # type: ignore
    if len(tribe_sells) > 0:
        tribe_sells = tribe_sells['arg__amountIn'].map(float) / 1e18
        cummulative_tribe_sells = tribe_sells.cumsum()
        cummulative_tribe_sells = evm.interpolate_block_series(
            start_block=min(blocks),
            pre_fill_value=0,
            series=cummulative_tribe_sells,
            end_block=max(blocks),
        )

        net_tribe_buys = cummulative_tribe_buys - cummulative_tribe_sells

    else:
        net_tribe_buys = cummulative_tribe_buys

    return {
        'name': 'Buybacks USD',
        'values': [net_tribe_buys[block] for block in blocks],
        'units': 'FEI',
    }

