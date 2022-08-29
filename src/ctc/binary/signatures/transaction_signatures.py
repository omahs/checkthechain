from __future__ import annotations

from ctc import spec
from .. import hashes
from .. import rlp_coding
from . import secp256k1_utils
from . import signature_creation
from . import signature_recovery
from . import vrs_utils


unsigned_transaction_keys = (
    'nonce',
    'gas_price',
    'gas_limit',
    'to',
    'value',
    'data',
)

legacy_transaction_keys = (
    'nonce',
    'gas_price',
    'gas',
    'to',
    'value',
    'input',
    'v',
    'r',
    's',
)

eip1559_transaction_keys = [
    'chain_id',
    'nonce',
    'max_priority_fee_per_gas',
    'max_fee_per_gas',
    'gas',
    'to',
    'value',
    'input',
    'access_list',
    'v',
    'r',
    's',
]

#
# # tranaction serialization
#


def serialize_unsigned_transaction(
    unsigned_transaction: spec.UnsignedTransaction,
    chain_id: int | None,
) -> spec.PrefixHexData:
    as_list = [unsigned_transaction[key] for key in unsigned_transaction_keys]  # type: ignore
    if chain_id is not None:
        as_list.append(chain_id)
        as_list.append(0)
        as_list.append(0)
    return rlp_coding.rlp_encode(as_list)


def serialize_signed_transaction(
    transaction: spec.SignedTransaction,
) -> spec.PrefixHexData:

    # get serialized key list
    if transaction['type'] == '0x0':
        keys = legacy_transaction_keys
        prefix = '0x'
    elif transaction['type'] == '0x2':
        keys = eip1559_transaction_keys
        prefix = '0x02'
    else:
        raise Exception('unknown transaction type: ' + transaction['type'])

    # get list of fields
    as_list = [transaction[key] for key in keys]  # type: ignore

    # encode as rlp
    return prefix + rlp_coding.rlp_encode(as_list, 'raw_hex')


#
# # transaction signing
#

def sign_transaction(
    transaction: spec.UnsignedTransaction,
    *,
    private_key: str,
    chain_id: int | None,
) -> tuple[int, int, int]:
    message = serialize_unsigned_transaction(transaction, chain_id=chain_id)
    return signature_creation.sign_data_message(
        message=message,
        private_key=private_key,
        chain_id=chain_id,
        mode='eth_sign',
    )


def get_transaction_sender(
    transaction: spec.Transaction,
    signature: spec.Data,
) -> spec.Address:
    """
    adapted from https://github.com/ethereum/pyethereum/blob/ecb14c937a0b6cb0a0dc4f06be3a88e6d53dcce3/ethereum/transactions.py#L68
    """

    if 'from' in transaction:
        return transaction['from']

    v, r, s = vrs_utils.unpack_vrs(signature)

    # encode transaction data
    if r == 0 and s == 0:
        # null address
        return '0x' + '0' * 40
    elif v in (27, 28):
        chain_id = None
    elif v >= 37:
        chain_id = vrs_utils.vrs_to_network_id(v=v, r=r, s=s)
        if chain_id is None:
            raise Exception('could not parse chain_id')
        v = v - chain_id * 2 - 8
        assert v in (27, 28)
    else:
        raise Exception('invalid v value')
    if r >= secp256k1_utils.N or s >= secp256k1_utils.N or r == 0 or s == 0:
        raise Exception('invalid signature values')

    # get public key
    rlp_transaction = serialize_unsigned_transaction(
        transaction,  # type: ignore
        chain_id=chain_id,
    )
    message_hash = hashes.keccak(rlp_transaction)
    public_key = signature_recovery.get_signer_public_key(
        message_hash=message_hash,
        v=v,
        r=r,
        s=s,
    )

    # convert public key to address
    sender = '0x' + hashes.keccak(public_key)[-40:]
    return sender


#
# # transaction hashing
#

def is_transaction_signed(transaction) -> bool:
    return (
        transaction.get('v') is not None
        and transaction.get('r') is not None
        and transaction.get('s') is not None
    )


def get_transaction_hash(transaction):
    if is_transaction_signed(transaction):
        serialized = serialize_signed_transaction(transaction)
    else:
        serialized = serialize_unsigned_transaction(transaction)
    return hashes.keccak(serialized)