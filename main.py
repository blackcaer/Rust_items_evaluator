import asyncio
import json
import traceback

import aiohttp
import jsonpickle
from prettytable import PrettyTable

from ItemRust import ItemRust
from ItemRustDatabase import ItemRustDatabase


# start_time = time.time()
# end_time = time.time()
# execution_time = end_time - start_time
# print(name, " took ", round(execution_time, 3), " sec")

async def fetch_and_calc(name):
    itemrust = ItemRust(name)
    await itemrust.update_async()
    return [itemrust.calc_liqval(), itemrust]


def rch_shop_to_tab():
    with open('rchshop.txt', 'r') as f:
        res = json.load(f)

    # TODO only for tests
    res = res[:5]
    # res = [{"name": "Weapon Barrel", "price": 13.53, "quantity": 2}]

    return res


def show_table(values):
    values = [r for r in values
              if r["data"] is not None and r["value"] is not None and r["data"].all_success]

    table = PrettyTable()
    table.field_names = ["name", "per_day", "price", "liq_val", "val"]
    for r in values:
        price_sm = r["data"].price_sm / 100
        perday = r["data"].sales_sm["30"]["volume"] / 30
        val2 = round(r["value"] * price_sm ** (1 / 2), 2)
        table.add_row([r["name"], round(perday, 2), price_sm, round(r["value"], 2), val2])

    table.sortby = "val"
    table.reversesort = True
    print(table)


def show_table_rchshop(values):
    values = [r for r in values
              if r["data"] is not None and r["liqval"] is not None and r["data"].all_success]

    table = PrettyTable(reversesort=True)
    table.field_names = ["name", "quantity", "% sm/rch", "shop price",
                         "steam price", "sold/day", "liq_val", "value", "sp/sm", "% sp/sm"]

    for record in values:
        itemrust = record["data"]
        price_sm = record["data"].price_sm / 100
        price_rch = record["rch_price"]
        liqval = round(record["liqval"], 2)
        perday = round(record["data"].sales_sm["30"]["volume"] / 30, 0)
        # EF = round((price_sm / price_rch)**2,2)

        value = itemrust.calc_value(price_rch)  # round(EF*liqval*price_sm ** (1 / 2),2)

        # TODO filtering (do it right xd)
        # if price_sm<0.7 or perday<14:# or (price_sm<12 and liqval<1):
        #    continue

        table.add_row([record["name"],
                       record["quantity"],
                       str(round(price_sm / price_rch * 100 - 100)) + "%",
                       price_rch,
                       price_sm,
                       perday,
                       liqval,
                       value,
                       round((itemrust.price_sp / 100) / price_sm, 2),
                       str(round((itemrust.price_sp / 100) / price_sm * 100 - 100)) + "%"
                       ])

    # print("sort by value:")
    # table.sortby = "value"
    # print(table)

    print("sort by value:")
    table.sortby = "value"
    print(table)

    print("sort by sp/sm:")
    table.sortby = "sp/sm"
    print(table)


async def rch_shop_all():
    TEST = 0
    SAVE_FOR_TEST = 1  # Saves data if TEST is False
    shop = rch_shop_to_tab()

    item_fetch_tasks = set()
    values = []

    async with aiohttp.ClientSession() as session:
        ItemRust.set_session(session)
        obj_to_save = list()

        if TEST:
            with open('tmp_shop_data.json', 'r') as file:
                loaded_test_data = jsonpickle.decode(file.read())
            print("Loaded test data (from one of previous fetches)")

            async def placeholder(x):
                return x

            for r in loaded_test_data:
                task = asyncio.create_task(placeholder(r[0]))
                item_fetch_tasks.add((task, r[1], r[2]))

        else:
            for item in shop:
                name, rch_price, quantity = item.values()
                task = asyncio.create_task(fetch_and_calc(name))
                item_fetch_tasks.add((task, rch_price, quantity))

        # Normalny przebieg programu z fetchowaniem:
        for task, rch_price, quantity in item_fetch_tasks:
            tmp = await task
            obj_to_save.append([tmp, rch_price, quantity])
            liqval = tmp[0]
            itemrust = tmp[1]
            values.append({"name": itemrust.name,
                           "rch_price": rch_price,
                           "quantity": quantity,
                           "liqval": liqval,
                           "data": itemrust})

        if SAVE_FOR_TEST:
            with open('tmp_shop_data.json', 'w') as f:
                # json.dump(obj_to_save, f)
                json_data = jsonpickle.encode(obj_to_save)
                f.write(json_data)

        show_table_rchshop(values)

        input("")


async def main():
    try:
        global database
        database = ItemRustDatabase()

        await rch_shop_all()

        return 0
        names = ["Weapon barrel", "Legacy kevlar kilt", "Tempered AK47", "Alien Red", "Cloth", "Frostbite",
                 "Neon Stone Storage", "Gingerbread Double Door", "Raven", "Sacrificial Mask", "Box from Hell",
                 "Doors to a Fairy Tale"]
        names = ["Weapon barrel", "Legacy kevlar kilt", "Tempered AK47"]
        # names = ["Weapon barrel"]

        values = []

        item_fetch_tasks = set()
        async with aiohttp.ClientSession() as session:
            ItemRust.set_session(session)
            i = ItemRust("Weapon barrel")

            for name in names:
                task = asyncio.create_task(fetch_and_calc(name))
                item_fetch_tasks.add(task)

            for task in item_fetch_tasks:
                tmp = await task
                liqval = tmp[0]
                itemrust = tmp[1]
                values.append({"name": itemrust.name, "value": liqval, "data": itemrust})

            show_table(values)

            input("")

    except Exception as e:
        print("Unexpected error: ", str(e.args[0]), " ", e.__cause__)
        traceback.print_exc()
        input(" ")


"""
    if res.success:
        print(res.data)
    else:
        print("ERROR: ")
        print(res.errors)
"""

if __name__ == "__main__":
    asyncio.run(main())

# <3
