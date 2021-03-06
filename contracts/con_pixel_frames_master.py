import con_pixel_frames
import currency

S = Hash(default_value='')
balances = Hash(default_value=0)

@construct
def seed():
    S['name'] = 'Pixel Frames'
    S['description'] = 'Create, Own and Sell unique pixel animations on the Lamden Blockchain!'
    S['icon_svg'] = "PHN2ZyB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB2aWV3Qm94PSIwIDAgMjQgMjQiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0IiBmaWxsPSJub25lIiByeD0iMCIgcnk9IjAiPjwvcmVjdD48cGF0aCBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGNsaXAtcnVsZT0iZXZlbm9kZCIgZD0iTTEyLjM3MDEgMTQuM0MxMi4yNzAxIDE0LjMgMTIuMTgwMSAxNC4yOCAxMi4wOTAxIDE0LjIzTDIuNjkwMDYgOS4zMjk5OUMyLjQ5MDA2IDkuMjI5OTkgMi4zNzAwNiA5LjAxOTk5IDIuMzcwMDYgOC43OTk5OUMyLjM3MDA2IDguNTc5OTkgMi40OTAwNiA4LjM2OTk5IDIuNjkwMDYgOC4yNjk5OUwxMi4wOTAxIDMuMzY5OTlDMTIuMjYwMSAzLjI3OTk5IDEyLjQ3MDEgMy4yNzk5OSAxMi42NDAxIDMuMzY5OTlMMjIuMDQwMSA4LjI2OTk5QzIyLjI1MDEgOC4zNjk5OSAyMi4zNzAxIDguNTc5OTkgMjIuMzcwMSA4Ljc5OTk5QzIyLjM3MDEgOS4wMTk5OSAyMi4yNTAxIDkuMjI5OTkgMjIuMDUwMSA5LjMyOTk5TDEyLjY1MDEgMTQuMjNDMTIuNTYwMSAxNC4yOCAxMi40NzAxIDE0LjMgMTIuMzcwMSAxNC4zWk00LjI3MDA2IDguNzk5OTlMMTIuMzcwMSAxMy4wMkwyMC40NzAxIDguNzk5OTlMMTIuMzcwMSA0LjU3OTk5TDQuMjcwMDYgOC43OTk5OVpNMTIuMzcgMTcuNUMxMi4yNjk5IDE3LjUgMTIuMTggMTcuNDggMTIuMDkgMTcuNDNMMi42ODk5NSAxMi41M0MyLjM5OTk1IDEyLjM4IDIuMjg5OTUgMTIuMDIgMi40Mzk5NSAxMS43MkMyLjU4OTk1IDExLjQzIDIuOTU5OTUgMTEuMzEgMy4yNDk5NSAxMS40N0wxMi4zNyAxNi4yMkwyMS40OSAxMS40NkMyMS43OCAxMS4zMSAyMi4xNSAxMS40MiAyMi4zIDExLjcxQzIyLjQ1IDEyIDIyLjM0IDEyLjM3IDIyLjA1IDEyLjUyTDEyLjY1IDE3LjQyQzEyLjU1OTkgMTcuNDggMTIuNDcgMTcuNSAxMi4zNyAxNy41Wk0xMi4wOSAyMC42M0MxMi4xOCAyMC42OCAxMi4yNyAyMC43IDEyLjM3IDIwLjdDMTIuNDcgMjAuNyAxMi41NiAyMC42OCAxMi42NSAyMC42MkwyMi4wNSAxNS43MkMyMi4zNCAxNS41NyAyMi40NSAxNS4yIDIyLjMgMTQuOTFDMjIuMTUgMTQuNjIgMjEuNzggMTQuNTEgMjEuNDkgMTQuNjZMMTIuMzcgMTkuNDJMMy4yNDk5NyAxNC42N0MyLjk1OTk3IDE0LjUxIDIuNTg5OTcgMTQuNjMgMi40Mzk5NyAxNC45MkMyLjI3OTk3IDE1LjIxIDIuMzk5OTcgMTUuNTggMi42ODk5NyAxNS43M0wxMi4wOSAyMC42M1ogICIgZmlsbD0iI2ZmNWJiMCI+PC9wYXRoPjwvc3ZnPg=="


@export
def create_thing(thing_string: str, name: str, description: str, meta: dict = {}):
    sender = ctx.caller
    thing_uid = con_pixel_frames.add_thing(thing_string, name, description, meta, sender)
    add_to_balance(sender)
    return thing_uid

@export
def buy_thing(uid: str):
    owner = con_pixel_frames.get_owner(uid)
    sender = ctx.caller
    assert_already_owned(uid, sender)

    price_amount = con_pixel_frames.get_price_amount(uid)
    assert price_amount, uid + ' is not for sale'
    assert price_amount > 0, uid + ' is not for sale'

    price_hold = con_pixel_frames.get_price_hold(uid)
    if price_hold != '':
        assert sender == price_hold, 'this item is being held for ' + price_hold

    # currency.transfer_from(amount: float, to: str, main_account: str)
    currency.transfer_from(price_amount, owner, sender)

    # if the TAU transfer did not take place then this part will not execute as the whole method will fail
    transfer_ownership(uid, sender)

@export
def sell_thing(uid: str, amount: int):
    # make sure the caller owns the item
    assert_ownership(uid, ctx.caller)
    con_pixel_frames.set_price(uid, amount, '')

@export
def sell_thing_to(uid: str, amount: int, hold: str):
    # make sure the caller owns the item
    assert_ownership(uid, ctx.caller)
    con_pixel_frames.set_price(uid, amount, hold)

@export
def give_thing(uid: str, new_owner: str):
    sender = ctx.caller
    # make sure the caller owns the item
    assert_ownership(uid, sender)
    assert_already_owned(uid, new_owner)
    transfer_ownership(uid, new_owner)

@export
def like_thing(uid: str):
    sender = ctx.caller
    assert S['liked', uid, sender] == '', sender + " already liked " + uid
    con_pixel_frames.like_thing(uid)
    S['liked', uid, sender] = True

@export
def prove_ownership(uid: str, code: str):
    sender = ctx.caller
    assert_ownership(uid, sender)
    con_pixel_frames.set_proof(uid, code)

def assert_ownership(uid: str, sender):
    owner = con_pixel_frames.get_owner(uid)
    assert owner == sender, uid + ' not owned by ' + sender

def assert_already_owned(uid: str, sender):
    owner = con_pixel_frames.get_owner(uid)
    assert owner != sender, uid + ' already owned by ' + sender

def transfer_ownership(uid:str, new_owner: str):
    old_owner = con_pixel_frames.get_owner(uid)
    #change ownership to new owner
    con_pixel_frames.set_owner(uid, new_owner)

    # if item was for sale make it no longer for sale
    if con_pixel_frames.get_price_amount(uid) > 0:
        con_pixel_frames.set_price(uid, 0, '')

    #adjust balances
    add_to_balance(new_owner)
    subtract_from_balance(old_owner)

def add_to_balance(holder: str):
    if balances[holder] is None:
        balances[holder] = 1
    else:
        balances[holder] = balances[holder] + 1

def subtract_from_balance(holder: str):
    if balances[holder] is None:
        balances[holder] = 0
    else:
        balances[holder] = balances[holder] - 1