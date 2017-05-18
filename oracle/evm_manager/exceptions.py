class MultisigNotFoundError(Exception):
    pass


class ContractNotFoundError(Exception):
    pass


class OssError(Exception):
    pass


class TxNotFoundError(Exception):
    pass


class TxUnconfirmedError(Exception):
    pass


class DoubleSpendingError(Exception):
    pass


class UnsupportedTxTypeError(Exception):
    pass
