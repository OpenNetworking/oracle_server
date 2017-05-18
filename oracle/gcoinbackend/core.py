
"""
Functions for interacting with Gcoin
"""
from django.conf import settings
from django.utils.module_loading import import_string


_backend = None


def get_gcoin_backend():
    global _backend
    if not _backend:
        path = getattr(settings, 'GCOIN_BACKEND', 'gcoinbackend.backends.base.BaseGcoinBackend')
        print(path)
        klass = import_string(path)
        _backend = klass()
    return _backend


def get_address_balance(address, color_id=None, min_conf=0):
    backend = get_gcoin_backend()
    return backend.get_address_balance(address, color_id, min_conf)


def get_address_utxos(address):
    backend = get_gcoin_backend()
    return backend.get_address_utxos(address)


def get_license_info(color_id):
    backend = get_gcoin_backend()
    return backend.get_license_info(color_id)


def issue_license(alliance_member_address, to_address, color_id, license_info):
    backend = get_gcoin_backend()
    return backend.issue_license(alliance_member_address, to_address, color_id, license_info)


def mint_color_zero(alliance_member_address):
    backend = get_gcoin_backend()
    return backend.mint_color_zero(alliance_member_address)


def mint(mint_address, amount, color_id):
    backend = get_gcoin_backend()
    return backend.mint(mint_address, amount, color_id)


def send(from_address, to_address, amount, color_id):
    backend = get_gcoin_backend()
    return backend.send(from_address, to_address, amount, color_id)


def get_tx(tx_hash):
    backend = get_gcoin_backend()
    return backend.get_tx(tx_hash)


def get_txs_by_address(address, starting_after=None, since=None, tx_type=None):
    backend = get_gcoin_backend()
    return backend.get_txs_by_address(address, starting_after, since, tx_type)


def get_block_by_hash(block_hash):
    backend = get_gcoin_backend()
    return backend.get_block_by_hash(block_hash)


def get_latest_blocks():
    backend = get_gcoin_backend()
    return backend.get_latest_blocks()


def send_contract_tx(from_address, tx):
    backend = get_gcoin_backend()
    return backend.send_contract_tx(from_address, tx)


def subscribe_tx_notification(tx_hash, confirmation_count, callback_url):
    backend = get_gcoin_backend()
    return backend.subscribe_tx_notification(tx_hash, confirmation_count, callback_url)


def subscribe_address_notification(address, callback_url):
    backend = get_gcoin_backend()
    return backend.subscribe_address_notification(address, callback_url)
