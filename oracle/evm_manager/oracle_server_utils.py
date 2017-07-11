from gcoinbackend import core as gcoincore

from .utils import make_contract_multisig_address
from .models import ContractInfo, StateInfo


def deploy_new_contract(state_multisig_address, contract_address, sender_address, tx_info):
    contract_multisig_address, contract_multisig_script, m = make_contract_multisig_address(
        tx_info['hash'], contract_address)
    state_info = StateInfo.objects.get(multisig_address=state_multisig_address)
    ContractInfo.objects.create(
        state_info=state_info, multisig_address=contract_multisig_address, contract_address=contract_address)


def get_oraclize_info(link, tx_info):
    contract = link.oraclize_contract
    blockhash = tx_info['blockhash']
    block = get_block_info(blockhash)
    if contract.name == 'start_of_block' or contract.name == 'end_of_block':
        return block['height']
    elif contract.name == 'block_confirm_number':
        blocks = get_latest_blocks()
        latest_block_number = blocks[0]['height']
        block_confirmation_count = str(int(latest_block_number) - int(block['height']))
        return block_confirmation_count
    elif contract.name == 'trand_confirm_number':
        return str(tx_info['confirmations'])
    elif contract.name == 'specifies_balance':
        balance = get_address_balance(link.receiver, link.color)
        return balance[link.color]
    elif contract.name == 'issuance_of_asset_transfer':
        license_info = get_license_info(link.color)
        if license_info['owner'] == link.receiver:
            return '1'
        else:
            return '0'
    else:
        print('Exception OC')


def get_block_info(block_hash):
    block = gcoincore.get_block_by_hash(block_hash)
    return block


def get_latest_blocks():
    blocks = gcoincore.get_latest_blocks()
    return blocks


def get_sender_addr(txid, vout):
    try:
        tx = gcoincore.get_tx(txid)
        return tx['vout'][vout]['scriptPubKey']['addresses'][0]
    except:
        print("[ERROR] getting sender address")


def get_address_balance(address, color):
    balance = gcoincore.get_address_balance(address, color)
    return balance


def get_license_info(color):
    info = gcoincore.get_license_info(color)
    return info
