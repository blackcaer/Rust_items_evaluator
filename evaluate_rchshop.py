import asyncio
import json
import traceback
import aiohttp
import jsonpickle
from prettytable import PrettyTable
from ItemRust import ItemRust
from ItemRustDatabase import ItemRustDatabase
import time
from collections import Counter

ITEMDB_FILE = "rustItemDatabase.txt"



async def fetch_and_calc(name):
    itemrust = ItemRust(name)
    await itemrust.update_async()
    return [itemrust.calc_liqval(), itemrust]


def rch_shop_to_tab():
    with open('src/rchshop.txt', 'r') as f:
        res = json.load(f)

    # TODO only for tests
    #res = res[:5]
    # res = [{"name": "Weapon Barrel", "price": 13.53, "quantity": 2}]

    return res

def eq_to_tab():
    with open('src/inventory.txt', 'r') as f:
        res = json.load(f)

    tmp = []
    for r in res:
        obj = {
            "name": r["market_hash_name"],
            "price": r["price"]/100,
        }
        if obj["price"] == 0:
            continue
        tmp.append(obj)

    tmp = [(entry["name"],entry["price"]) for entry in tmp]

    result = [{"name": name,
             "price": price,
             "quantity": count} for (name, price), count in Counter(tmp).items()]

    return result

def show_table_rchshop(values):
    rows = []
    values = [r for r in values
              if r["data"] is not None and r["liqval"] is not None and r["data"].all_success]

    table = PrettyTable(reversesort=True)
    table.field_names = ["name", "quantity", "% sm/rch", "shop price",
                         "steam price", "perday (extr)", "liq_val", "value","valNoEF", "sp/sm", "% sp/sm"]

    fromDB=0
    for record in values:
        itemrust = record["data"]
        price_sm = record["data"].price_sm / 100
        price_rch = record["rch_price"]
        liqval = round(record["liqval"], 2)
        perday = round(itemrust.calc_sales_extrapolated_sm(30)[
                                 "volume"] / 30,1) #round(record["data"].sales_sm["30"]["volume"] / 30, 0)
        # EF = round((price_sm / price_rch)**2,2)

        value = itemrust.calc_value(price_rch)  # round(EF*liqval*price_sm ** (1 / 2),2)
        value_no_EF = itemrust.calc_value()

        # TODO filtering (do it right xd)
        # if price_sm<0.7 or perday<14:# or (price_sm<12 and liqval<1):
        #    continue
        price_sp = itemrust.price_sp
        if price_sp is not None:
            spsm = round((price_sp / 100) / price_sm, 2)
            percentspsm = str(round((price_sp / 100) / price_sm * 100 - 100))
        else:
            spsm, percentspsm = "None", "None"

        rows.append([record["name"],
                     record["quantity"],
                     str(round(price_sm / price_rch * 100 - 100)) + "%",
                     price_rch,
                     price_sm,
                     perday,
                     liqval,
                     value,
                     value_no_EF,
                     str(spsm),
                     str(percentspsm) + "%"
                     ])
        if itemrust.fromDB:
            fromDB+=1

    for row in rows:
        table.add_row(row)
    # print("sort by value:")
    # table.sortby = "value"
    # print(table)

    print("sort by sp/sm:")
    table.sortby = "sp/sm"
    print(table)

    print("sort by value:")
    table.sortby = "value"
    print(table)

    print("sort by valNoEF:")
    table.sortby = "valNoEF"
    print(table)



    print(f"Total different items: {len(values)}, fromDB: {fromDB}")


async def rch_shop_all(ITEMDB):
    TEST = 0
    SAVE_FOR_TEST = 0  # Saves data if TEST is False
    EQ_MODE=1
    shop = rch_shop_to_tab()
    if EQ_MODE:
        shop=eq_to_tab()

    item_fetch_tasks = set()
    rows = []


    async with aiohttp.ClientSession() as session:
        ItemRust.set_session(session)
        ItemRust.set_database(ITEMDB)
        obj_to_save = list()

        start_time = time.time()


        if TEST:
            with open('src/tmp_shop_data.json', 'r') as file:
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
            rows.append({"name": itemrust.name,
                           "rch_price": rch_price,
                           "quantity": quantity,
                           "liqval": liqval,
                           "data": itemrust})

        if SAVE_FOR_TEST:
            with open('src/tmp_shop_data.json', 'w') as f:
                # json.dump(obj_to_save, f)
                json_data = jsonpickle.encode(obj_to_save)
                f.write(json_data)

        end_time = time.time()
        execution_time = end_time - start_time
        print("Updating items took ", round(execution_time, 3), " sec")

        show_table_rchshop(rows)

        input("")


async def main():
    try:
        ITEMDB = ItemRustDatabase(ITEMDB_FILE)
        ITEMDB.load_database()

        await rch_shop_all(ITEMDB)

    except Exception as e:
        print("Unexpected error: ", str(e.args[0]), " ", e.__cause__)
        traceback.print_exc()
        input(" ")
    finally:
        ItemRust.database.save_database()


if __name__ == "__main__":
    asyncio.run(main())

# <3
