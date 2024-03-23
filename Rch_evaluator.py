import asyncio
import types
from enum import Enum

import aiohttp

import input_helper as in_helper
import display_helper as dp_helper
from ItemRust import ItemRust
from ItemRustDatabase import ItemRustDatabase


class Modes(Enum):
    EXIT = 0
    EVAL_ITEMS = 1
    EVAL_RCHSHOP = 2
    EVAL_EQ = 3


ITEMDB_FILE = "rustItemDatabase.txt"
MODE = 0


async def handle_choices():
    global MODE

    ITEMDB = ItemRustDatabase(ITEMDB_FILE)
    ITEMDB.load_database()

    async with (aiohttp.ClientSession() as session):
        ItemRust.set_session(session)
        ItemRust.set_database(ITEMDB)
        while True:
            print("0. Exit")
            print("1. Evaluate items")
            print("2. Evaluate rchshop")
            nr = input("Provide input:")
            if not nr.isnumeric() or (int(nr) not in [mode.value for mode in Modes]):
                raise ValueError("Bad option")
            MODE = Modes(int(nr))

            if MODE == 0:
                exit()

            data = get_input()
            data["items"] = create_items(data)
            await update_items(data["items"])
            data["items"] = leave_only_success(data["items"])

            display_items(data)

            print()


def leave_only_success(items):
    return [item for item in items if (item is not None and item.all_success)]

def create_items(data):
    items = []
    for item_data in data["items_data"]:
        item = None
        if MODE == Modes.EVAL_RCHSHOP:
            item = ItemRust(item_data["name"],quantity=item_data["quantity"],price_rchshop=item_data["price"])
        elif MODE == Modes.EVAL_EQ:
            item = ItemRust(item_data["name"],quantity=item_data["quantity"])   # TODO: add price and calculating value with eq price (odwrotnosc EF prawdopodobnie)
        elif MODE == Modes.EVAL_ITEMS:
            item = ItemRust(item_data["name"], quantity=item_data["quantity"])
        else:
            raise NotImplementedError("Mode is not implemented (yet)")
        items.append(item)
    return items


def get_input():
    # get input
    # format input
    data = {"items_data" : []}  # items_data - name,price/site price,quantity

    if MODE == Modes.EVAL_ITEMS:
        items_data = in_helper.get_input_console()
    elif MODE == Modes.EVAL_RCHSHOP:
        items_data = in_helper.get_input_rchshop()
    elif MODE == Modes.EVAL_EQ:
        items_data = in_helper.get_input_eq()
    else:
        raise NotImplementedError("Mode is not implemented (yet)")

    data["items_data"] = items_data

    return data


async def update_items(items):
    # TODO log to file success/failure
    to_fetch = list()
    for item in items:
        item: ItemRust = item
        to_fetch.append({"name": item.name,
                      "item": item,
                      "task": asyncio.create_task(item.update_async())
                      })

    for record in to_fetch:
        name, item, task = record["name"], record["item"], record["task"]
        await task
        if item is not None and item.all_success:
            print(f"{name}:  SUCCESS")
        else:
            print(f"{name}:  FAILURE")


def display_items(data):
    if MODE==Modes.EVAL_ITEMS:
        dp_helper.display_eval_items(data["items"])
    else:
        raise NotImplementedError("not implemented display")


#?? delete?
def create_rows(data, *args):
    rows = []
    for arg in args:
        if not (arg is list and len(arg) == 2 and arg[0] is str and arg[1] is types.FunctionType and callable(arg[1])):
            raise ValueError("Incorrect arguments for " + create_rows.__name__)
        rows.append([arg[0], arg[1](data)])
    return rows


async def main():
    # choose rchshop/rcheq/items/coinflips etc
    try:
        await handle_choices()
    finally:
        ItemRust.database.save_database()


if __name__ == "__main__":
    asyncio.run(main())
