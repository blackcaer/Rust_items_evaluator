import asyncio

import aiohttp
from prettytable import PrettyTable

from ItemRust import ItemRust


async def fetch_and_calc(name):
    i = ItemRust(name)
    await i.update_async()

    return [i.calc_liqval(), i]


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
    # <name> $<price>   - returns {"name": _,"price":_,"quantity":_}
    # <name>            - returns {"name": _,"quantity":_}
    #
    # TODO handle multiple same items, return their quantity
    if ',' in lines[0]:
        raise RuntimeError("DONT USE COMMA")

    def extract_data(line):
        # Extracts data from format <name> $<price>
        items = {}
        parts = line.split('\t')
        if len(parts) == 2:
            name = parts[0].strip()
            price = float(parts[1].replace('$', '').strip())
            items["name"] = name
            items["price"] = price
        else:
            raise AttributeError("Incorrect number of parts in line: " + line)

        return items

    all_lines_have_dollar = True
    lines = [l.strip() for l in lines if l.strip() != ""]
    for l in lines:
        if "$" not in l:
            all_lines_have_dollar = False

    if not all_lines_have_dollar:
        return [{"name": l} for l in lines]
    else:
        return [extract_data(l) for l in lines]


async def main():
    try:
        while True:
            names = []
            values = []

            # names += input("Podaj nazwy przedmiotów oddzielone przecinkami: \n").split(',')

            lines = []

            print("Wklej dane (lub wpisz naciskając Enter po każdej linii,a po wprowadzeniu wszystkich danych \n"
                  "naciśnij Enter bez wprowadzania tekstu): ")

            while True:
                line = input()
                if not line:
                    break
                lines.append(line)

            data = handle_input(lines)
            print(data)
            names = []
            for i in data:
                names.append(i["name"])

            async with aiohttp.ClientSession() as session:
                ItemRust.set_session(session)
                item_fetch_tasks = set()

                # create tasks
                for name in names:
                    task = asyncio.create_task(fetch_and_calc(name))
                    item_fetch_tasks.add(task)

                # gather results, prepare values tab for displaying
                for task in item_fetch_tasks:
                    liqval, curr_item = await task
                    values.append({"name": curr_item.name, "liqval": liqval, "data": curr_item})

                table = PrettyTable(reversesort=True)
                table.field_names = ["name", "price_sm", "per_day", "liq_val", "value", "sp/sm", "% sp/sm"]
                rows = []
                avgdata = {"prices": [], "values": []}  # data for weighted average

                # prepare rows of prettytable
                for r in values:
                    name, liqval, curr_item = r["name"], r["liqval"], r["data"]

                    if curr_item is not None and r["liqval"] is not None and r["data"].all_success:
                        price_sm = curr_item.price_sm / 100
                        perday = curr_item.calc_sales_extrapolated_sm(30)[
                                     "volume"] / 30  # curr_item.sales_sm["30"]["volume"] / 30
                        value = curr_item.calc_value(None)

                        rows.append([name,
                                       price_sm,
                                       round(perday, 2),
                                       round(liqval, 2),
                                       value,
                                       round((curr_item.price_sp / 100) / price_sm, 2),
                                       str(round((curr_item.price_sp / 100) / price_sm * 100 - 100)) + "%"
                                       ])
                        avgdata["prices"].append(price_sm)
                        avgdata["values"].append(value)
                    else:
                        print(r["name"] + " FAILURE")

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


    except Exception as e:
        print("Wywaliło ci program: ", e)
        print("args ", e.args)
        print("__cause__ ", e.__cause__)
        input("")


if __name__ == "__main__":
    asyncio.run(main())
