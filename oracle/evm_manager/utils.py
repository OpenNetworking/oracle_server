try:
    from Crypto.Hash import keccak

    def sha3_256(x):
        return keccak.new(digest_bits=256, data=x).digest()
except:
    import sha3 as _sha3

    def sha3_256(x):
        return _sha3.keccak_256(x).digest()
import os
import json
import rlp
import copy
from rlp.utils import decode_hex, ascii_chr
from binascii import hexlify, unhexlify
from gcoin import b58check_to_hex, hex_to_b58check
from .decorators import retry
from gcoinbackend import core as gcoincore
from .exceptions import TxNotFoundError, TxUnconfirmedError


def is_numeric(x):
    return isinstance(x, int)


def to_string(value):
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return bytes(value, 'utf-8')
    if isinstance(value, int):
        return bytes(str(value), 'utf-8')


def wallet_address_to_evm(address):
    address = b58check_to_hex(address)
    return address


def evm_address_to_wallet(evm_address, magicbyte=0):
    address = hex_to_b58check(evm_address, magicbyte=magicbyte)
    return address


def get_evm_balance(multisig_address, address):
    contract_path = os.path.dirname(os.path.abspath(__file__)) + '/../states/' + multisig_address

    user_evm_address = wallet_address_to_evm(address)
    try:
        with open(contract_path.format(multisig_address=multisig_address), 'r') as f:
            content = json.load(f)
            account = content['accounts'][user_evm_address]
            amount = account['balance']
            return amount
    except Exception as e:
        print(e)
        return {}


def mk_contract_address(sender, nonce):
    if nonce is None:
        nonce = 0
    return sha3(rlp.encode([normalize_address(sender), nonce]))[12:]


def make_contract_address(multisig_address, sender_address):
    nonce = get_nonce(multisig_address, sender_address)
    nonce = nonce if nonce else 0
    contract_address_byte = mk_contract_address(wallet_address_to_evm(sender_address), nonce)
    contract_address = hexlify(contract_address_byte).decode("utf-8")
    return contract_address


def normalize_address(x, allow_blank=False):
    if is_numeric(x):
        return int_to_addr(x)
    if allow_blank and x in {'', b''}:
        return b''
    if len(x) in (42, 50) and x[:2] in {'0x', b'0x'}:
        x = x[2:]
    if len(x) in (40, 48):
        x = decode_hex(x)
    if len(x) == 24:
        assert len(x) == 24 and sha3(x[:20])[:4] == x[-4:]
        x = x[:20]
    if len(x) != 20:
        raise Exception("Invalid address format: %r" % x)
    return x


def int_to_addr(x):
    o = [b''] * 20
    for i in range(20):
        o[19 - i] = ascii_chr(x & 0xff)
        x >>= 8
    return b''.join(o)


sha3_count = [0]


def sha3(seed):
    sha3_count[0] += 1
    return sha3_256(to_string(seed))


def get_nonce(multisig_address, sender_address):
    sender_evm_address = wallet_address_to_evm(sender_address)
    contract_path = os.path.dirname(os.path.abspath(__file__)) + '/../states/' + multisig_address
    with open(contract_path, 'r') as f:
        content = json.load(f)
        if sender_evm_address in content['accounts']:
            return content['accounts'][sender_evm_address]['nonce']


def get_tx_info(tx_or_hash):
    tx = get_tx(tx_or_hash) if isinstance(tx_or_hash, str) else tx_or_hash
    tx_hash = tx.get('txid') or tx.get('hash')
    blockhash = tx.get('blockhash') or tx.get('block_hash')
    confirmations = tx.get('confirmations') or tx.get('confirmation')
    typ = tx.get('type')
    time = int(tx.get('time'))
    vins = _process_vins(tx)
    vouts = _process_vouts(tx)
    op_return = None if typ == 'NORMAL' else _process_op_return(tx)
    data = {}
    data['hash'] = tx_hash
    data['type'] = typ
    data['time'] = time
    data['vins'] = vins
    data['vouts'] = vouts
    data['blockhash'] = blockhash
    data['op_return'] = op_return
    data['confirmations'] = confirmations
    return data


def _process_vouts(tx):
    tx = copy.deepcopy(tx)
    vouts = (tx.get('vout') or tx.get('vouts'))
    for vout in vouts:
        vout['address'] = vout.get('address')
        vout['address'] = vout['address'] if vout['address'] is not None else \
            (vout.get('scriptPubKey').get('addresses') or '')
        vout['address'] = vout['address'] if isinstance(vout['address'], str) else vout['address'][0]
        vout['amount'] = vout.get('value') if vout.get('value') is not None else vout.get('amount')
        vout['amount'] = int(vout['amount'])
        vout['color'] = int(vout['color'])
        vout['n'] = int(vout['n'])
        del vout['scriptPubKey']
        try:
            del vout['value']
        except:
            pass
    return vouts


def _process_vins(tx):
    tx = copy.deepcopy(tx)
    vins = tx.get('vin') or tx.get('vins')
    for vin in vins:
        vin['vout'] = int(vin.get('vout'))
        vin['tx_hash'] = vin.get('txid') or vin.get('tx_id') or vin.get('tx_hash')
        delete_field = ['txid', 'tx_id', 'address', 'color', 'amount', 'scriptSig', 'sequence']
        for field in delete_field:
            try:
                del vin[field]
            except:
                pass
    return vins


def _process_op_return(tx):
    vouts = tx.get('vout') or tx.get('vouts')
    for vout in vouts:
        if int(vout['color']) == 0:
            op_return = vout['scriptPubKey'] if isinstance(vout['scriptPubKey'], str) else \
                vout['scriptPubKey']['asm'][10:]
            begin = op_return.find('7b')
            data = unhexlify(op_return[begin:])
            data = data.decode('utf-8')
            data = json.loads(data)
            multisig_address = data.get('multisig_address')
            if data.get('source_code'):
                is_deploy = True
                contract_address = None
                bytecode = data.get('source_code')
            elif data.get('function_inputs_hash'):
                is_deploy = False
                contract_address = data.get('contract_address')
                bytecode = data.get('function_inputs_hash')
    data = {}
    data['hex'] = op_return
    data['bytecode'] = bytecode
    data['is_deploy'] = is_deploy
    data['multisig_address'] = multisig_address
    data['contract_address'] = contract_address
    return data


@retry(10)
def get_tx(tx_hash, confirmations=0):
    tx = gcoincore.get_tx(tx_hash)
    if tx is None:
        raise TxNotFoundError
    tx_confirmations = tx.get('confirmations') or 0
    if tx_confirmations < confirmations:
        raise TxUnconfirmedError
    return tx


def get_sender_address(tx_or_hash):
    tx = get_tx(tx_or_hash) if isinstance(tx_or_hash, str) else tx_or_hash
    vins = tx.get('vin') or tx.get('vins')
    if vins[0].get('address') is not None:
        return vins[0].get('address')
    else:
        vins = _process_vins(tx)
        last_tx = get_tx(vins[0]['tx_hash'])
        address = _process_vouts(last_tx)[vins[0]['vout']]['address']
        return address


def get_multisig_address(tx_or_hash):
    tx = get_tx(tx_or_hash) if isinstance(tx_or_hash, str) else tx_or_hash
    if tx.get('type') == 'NORMAL':
        sender_address = get_sender_address(tx)
        multisig_address = sender_address if sender_address[0] == '3' else None
        return multisig_address
    elif tx.get('type') == 'CONTRACT':
        multisig_address = _process_op_return(tx).get('multisig_address')
        return multisig_address
    else:
        return None
