from ubinascii import hexlify

from trezor import ui
from trezor.messages import ButtonRequestType
from trezor.strings import format_amount
from trezor.ui.scroll import Paginated
from trezor.ui.text import Text
from trezor.utils import chunks

from apps.common.confirm import require_confirm, require_hold_to_confirm
from apps.common.layout import split_address

from . import networks
from .address import address_from_bytes


def _address_amount_screen(to_bytes, value, chain_id, token, tx_type):
    if to_bytes:
        to_str = address_from_bytes(to_bytes, networks.by_chain_id(chain_id))
    else:
        to_str = "new contract?"
    text = Text("Confirm sending", ui.ICON_SEND, ui.GREEN, new_lines=False)
    text.bold(format_ethereum_amount(value, token, chain_id, tx_type))
    text.normal(ui.GREY, "to", ui.FG)
    for to_line in split_address(to_str):
        text.br()
        text.mono(to_line)

    return text


async def require_confirm_tx(ctx, to_bytes, value, chain_id, tx_type=None):
    text = _address_amount_screen(to_bytes, value, chain_id, None, tx_type)
    # we use SignTx, not ConfirmOutput, for compatibility with T1
    await require_confirm(ctx, text, ButtonRequestType.SignTx)


async def require_confirm_tx_erc20(ctx, to_bytes, value, chain_id, token, tx_type=None):
    address_amount = _address_amount_screen(to_bytes, value, chain_id, token, tx_type)

    contract = Text("Confirm transaction", ui.ICON_SEND, ui.GREEN, new_lines=False)
    contract.normal(ui.GREY, "Contract:", ui.FG)
    _, contract_address, _, _ = token
    contract_address_hex = "0x" + hexlify(contract_address).decode()
    contract.mono(*split_data(contract_address_hex))

    await require_confirm(
        ctx, Paginated([address_amount, contract]), ButtonRequestType.SignTx
    )


async def require_confirm_fee(
    ctx, spending, gas_price, gas_limit, chain_id, token=None, tx_type=None
):
    text = Text("Confirm transaction", ui.ICON_SEND, ui.GREEN, new_lines=False)
    text.bold(format_ethereum_amount(spending, token, chain_id, tx_type))
    text.normal(ui.GREY, "Gas price:", ui.FG)
    text.bold(format_ethereum_amount(gas_price, None, chain_id, tx_type))
    text.normal(ui.GREY, "Maximum fee:", ui.FG)
    text.bold(format_ethereum_amount(gas_price * gas_limit, None, chain_id, tx_type))
    await require_hold_to_confirm(ctx, text, ButtonRequestType.SignTx)


def split_data(data):
    return chunks(data, 18)


async def require_confirm_data(ctx, data, data_total):
    data_str = hexlify(data[:36]).decode()
    if data_total > 36:
        data_str = data_str[:-2] + ".."
    text = Text("Confirm data", ui.ICON_SEND, ui.GREEN)
    text.bold("Size: %d bytes" % data_total)
    text.mono(*split_data(data_str))
    # we use SignTx, not ConfirmOutput, for compatibility with T1
    await require_confirm(ctx, text, ButtonRequestType.SignTx)


def format_ethereum_amount(value: int, token, chain_id: int, tx_type=None):
    if token:
        _, _, suffix, decimals = token
    else:
        suffix = networks.shortcut_by_chain_id(chain_id, tx_type)
        decimals = 18

    # Don't want to display wei values for tokens with small decimal numbers
    if decimals > 9 and value < 10 ** (decimals - 9):
        suffix = "Wei " + suffix
        decimals = 0

    return "%s %s" % (format_amount(value, decimals), suffix)
