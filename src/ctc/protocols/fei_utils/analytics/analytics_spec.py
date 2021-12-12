import typing

from ctc import spec


#
# # types
#


class Timescale(typing.TypedDict):
    window_size: str
    interval_size: str


Timestamp = int
Timestamps = list[int]

MetricName = str
MetricSeries = list[float]


class MetricData(typing.TypedDict, total=False):
    values: list[float]
    name: str
    link: str
    units: str


class MetricGroupStrict(typing.TypedDict):
    name: str
    metrics: dict[str, MetricData]


class MetricGroup(MetricGroupStrict, total=False):
    order: list[str]


class AnalyticsPayload(typing.TypedDict):

    # metadata
    version: str
    created_at_timestamp: Timestamp

    # timing data
    n_samples: int
    interval_size: str
    window_size: str
    timestamps: list[Timestamp]
    block_numbers: list[int]

    # metrics
    data: dict[str, MetricGroup]


MetricGroupCreator = typing.Callable[[list[int], bool], MetricGroup]
MetricGroupCreatorCoroutine = typing.Callable[
    [list[int], bool],
    typing.Coroutine[typing.Any, typing.Any, MetricGroup],
]
MultiMetricGroupCreator = typing.Callable[
    [list[int], bool],
    dict[str, MetricGroup],
]
MultiMetricGroupCreatorCoroutine = typing.Callable[
    [list[int], bool],
    typing.Coroutine[typing.Any, typing.Any, dict[str, MetricGroup]],
]


#
# # specific values
#

payload_timescales = [
    {'window_size': '1h', 'interval_size': '1 minute'},  # 60 datapoints
    {'window_size': '24h', 'interval_size': '10 minute'},  # 144 datapoints
    {'window_size': '7d', 'interval_size': '1 hour'},  # 168 datapoints
    {'window_size': '30d', 'interval_size': '1 day'},  # 30 datapoints
    {'window_size': '90d', 'interval_size': '1 day'},  # 90 datapoints
]


class DexPoolMetadata(typing.TypedDict, total=False):
    platform: str
    address: spec.ContractAddress
    other_assets: list[str]
    fei_index: int
    event_name: str


dex_pools: dict[str, DexPoolMetadata] = {
    'uniswap_v2__fei_eth': {
        'platform': 'Uniswap V2',
        'address': '0x94b0a3d511b6ecdb17ebf877278ab030acb0a878',
        'other_assets': ['WETH'],
    },
    'uniswap_v2__fei_tribe': {
        'platform': 'Uniswap V2',
        'address': '0x9928e4046d7c6513326ccea028cd3e7a91c7590a',
        'other_assets': ['TRIBE'],
    },
    'uniswap_v3__fei_usdc_5': {
        'platform': 'Uniswap V3',
        'address': '0x8c54aa2a32a779e6f6fbea568ad85a19e0109c26',
        'other_assets': ['USDC'],
    },
    'uniswap_v3__fei_dai_5': {
        'platform': 'Uniswap V3',
        'address': '0xbb2e5c2ff298fd96e166f90c8abacaf714df14f8',
        'other_assets': ['DAI'],
    },
    'curve__fei_3crv': {
        'platform': 'Curve',
        'address': '0x06cb22615BA53E60D67Bf6C341a0fD5E718E1655',
        'other_assets': ['3crv'],
        'fei_index': 0,
        'event_name': 'TokenExchangeUnderlying',
    },
    'curve__d3': {
        'platform': 'Curve',
        'address': '0xBaaa1F5DbA42C3389bDbc2c9D2dE134F5cD0Dc89',
        'other_assets': ['FRAX', 'alUSD'],
        'fei_index': 1,
        'event_name': 'TokenExchange',
    },
    'saddle__d4': {
        'platform': 'Saddle',
        'address': '0xC69DDcd4DFeF25D8a793241834d4cc4b3668EAD6',
        'other_assets': ['alUSD', 'FRAX', 'LUSD'],
        'fei_index': 1,
    },
    'sushiswap__fei_dpi': {
        'platform': 'Sushi',
        'address': '0x8775aE5e83BC5D926b6277579c2B0d40c7D9b528',
        'other_assets': ['DPI'],
    },
}

