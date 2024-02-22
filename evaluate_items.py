import asyncio
import aiohttp
import traceback
from prettytable import PrettyTable
from ItemRust import ItemRust
from collections import Counter
from ItemRustDatabase import ItemRustDatabase

ITEMDB_FILE = "rustItemDatabase.txt"

def weighted_average(data, weights):
    if len(data) != len(weights):
        raise ValueError("Length of data and weights must be the same.")

    products_sum = sum(x * y for x, y in zip(data, weights))
    weights_sum = sum(weights)

    if weights_sum == 0:
        raise ValueError("Sum of weights cannot be zero.")

    return products_sum / weights_sum


def handle_input(lines):
    # Handles formats:
    # <name> $<price>   - returns [{"name": _,"price":_,"quantity":_},...]
    # <name>            - returns [{"name": _,"quantity":_},...]
    #
    # TODO handle multiple same items, return their quantity
    if ',' in lines[0]:
        raise RuntimeError("DONT USE COMMA")

    def extract_data(line):
        # Extracts data from format <name> $<price>

        parts = line.split('\t')
        if len(parts) == 2:
            name = parts[0].strip()
            price = float(parts[1].replace('$', '').strip())
            return {"name": name, "price": price}
        else:
            raise AttributeError("Incorrect number of parts in line: " + line)

    all_lines_have_dollar = True
    lines = [l.strip() for l in lines if l.strip() != ""]
    for line in lines:
        if "$" not in line:
            all_lines_have_dollar = False

    if not all_lines_have_dollar:
        # Calculate quantity
        return [{"name": name,
                 "quantity": count}
                for name, count in Counter(lines).items()]
    else:
        names_prices = [extract_data(line) for line in lines]
        names_prices = [(entry["name"],entry["price"]) for entry in names_prices]

        # Calculate quantity
        return [{"name": name,
                 "price": price,
                 "quantity": count}
                for (name,price), count in Counter(names_prices).items()]


def get_input():
    print("Wklej dane (lub wpisz naciskając Enter po każdej linii,a po wprowadzeniu wszystkich danych \n"
          "naciśnij Enter bez wprowadzania tekstu): ")

    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)

    return handle_input(lines)


async def main():
    try:
        ITEMDB = ItemRustDatabase(ITEMDB_FILE)
        ITEMDB.load_database()
        async with aiohttp.ClientSession() as session:
            ItemRust.set_session(session)
            ItemRust.set_database(ITEMDB)

            while True:
                records = get_input()
                item_fetch_tasks = set()
                items = []

                # create tasks
                for record in records:
                    itemrust = ItemRust(name=record["name"], quantity=record["quantity"])
                    items.append(itemrust)
                    item_fetch_tasks.add(
                        asyncio.create_task(itemrust.update_async()))

                # gather results, prepare values tab for displaying
                for task in item_fetch_tasks:
                    await task

                table = PrettyTable(reversesort=True)
                table.field_names = ["name", "price_sm", "per_day (extr)", "liq_val", "value","value4one", "sp/sm", "% sp/sm"]
                rows = []
                avgdata = {"prices": [], "values": []}  # data for weighted average

                # prepare rows of prettytable
                for curr_item in items:
                    name = curr_item.name
                    liqval = curr_item.calc_liqval()

                    if curr_item is not None and liqval is not None and curr_item.all_success:
                        price_sm = curr_item.price_sm / 100
                        perday = curr_item.calc_sales_extrapolated_sm(30)[
                                     "volume"] / 30  # curr_item.sales_sm["30"]["volume"] / 30
                        value = curr_item.calc_value(None)
                        value4one = curr_item.calc_value(quantity=1)

                        rows.append([str(curr_item.quantity) + " " + name,
                                     price_sm,
                                     round(perday, 1),
                                     round(liqval, 2),
                                     value,
                                     value4one,
                                     round((curr_item.price_sp / 100) / price_sm, 2),
                                     str(round((curr_item.price_sp / 100) / price_sm * 100 - 100)) + "%"
                                     ])
                        for _ in range(curr_item.quantity):
                            avgdata["prices"].append(price_sm)
                            avgdata["values"].append(value)
                    else:
                        print(name + " FAILURE")

                for row in rows:
                    table.add_row(row)

                print("Sorting by sp/sm")
                table.sortby = "sp/sm"
                print(table)

                print("Sorting by value")
                table.sortby = "value"
                print(table)

                # display weighted average
                try:
                    wavg = round(weighted_average(data=avgdata["values"], weights=avgdata["prices"]), 2)
                except ValueError as e:
                    print("ERROR: " + str(e.args[0]))
                else:
                    print("Weighted average " + str(wavg))

                print()
                print()
    finally:
        if ItemRust.database is not None:
            print("Saving database")
            ItemRust.database.save_database()
    """except Exception as e:
        print("Unexpected error: ", str(e.args[0]), " ", e.__cause__)
        traceback.print_exc()
        input(" ")"""


if __name__ == "__main__":
    asyncio.run(main())
