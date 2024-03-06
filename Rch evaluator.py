import asyncio
import aiohttp
import jsonpickle
from prettytable import PrettyTable
from ItemRust import ItemRust
from ItemRustDatabase import ItemRustDatabase
from enum import Enum
import eval_helper as helper
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
    if MODE==Modes.EVAL_ITEMS:
        data = helper.get_input_console()
    elif MODE==Modes.EVAL_RCHSHOP:
        data = helper.get_input_rchshop()
    elif MODE==Modes.EVAL_EQ:
        data = helper.get_input_eq()

    return data


async def update_data(items_data):
    item_fetch_tasks = set()
    for item in items_data["items"]:
        item: ItemRust = item
        item_fetch_tasks.add(asyncio.create_task(item.update_async()))

    for task in item_fetch_tasks:
        await task


def display_items(items_data):
    pass



async def main():
    # choose rchshop/rcheq/items/coinflips etc
    handle_choices()

if __name__ == "__main__":
    asyncio.run(main())