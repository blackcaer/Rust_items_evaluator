import asyncio
import types
from enum import Enum

import aiohttp

import eval_helper as helper
from ItemRust import ItemRust
from ItemRustDatabase import ItemRustDatabase


class Modes(Enum):
    EXIT = 0
    EVAL_ITEMS = 1
    EVAL_RCHSHOP = 2
    EVAL_EQ = 3


ITEMDB_FILE = "rustItemDatabase.txt"
MODE = 0


def handle_choices():
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
            MODE = nr

            if MODE == 0:
                exit()

            items_data = get_input()
            update_data(items_data)

            display_items(items_data)

            print()


def get_input():
    # get input
    # format input
    data = None
    if MODE == Modes.EVAL_ITEMS:
        data = helper.get_input_console()
    elif MODE == Modes.EVAL_RCHSHOP:
        data = helper.get_input_rchshop()
    elif MODE == Modes.EVAL_EQ:
        data = helper.get_input_eq()

    return data


async def update_data(items_data):
    # TODO log to file success/failure
    to_fetch = set()
    for item in items_data["items"]:
        item: ItemRust = item
        to_fetch.add({"name": item.name,
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


def display_items(items_data):
    pass


def create_rows(data, *args):
    rows = []
    for arg in args:
        if not (arg is list and len(arg) == 2 and arg[0] is str and arg[1] is types.FunctionType and callable(arg[1])):
            raise ValueError("Incorrect arguments for " + create_rows.__name__)
        rows.append([arg[0], arg[1](data)])
    return rows


async def main():
    # choose rchshop/rcheq/items/coinflips etc
    handle_choices()


if __name__ == "__main__":
    asyncio.run(main())
