import json
from collections import Counter


def _handle_input(lines):
    # Handles formats:
    # <name> $<price>   - returns [{"name": _,"price":_,"quantity":_},...]
    # <name>            - returns [{"name": _,"quantity":_},...]
    #

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
        names_prices = [(entry["name"], entry["price"]) for entry in names_prices]

        # Calculate quantity
        return [{"name": name,
                 "price": price,
                 "quantity": count}
                for (name, price), count in Counter(names_prices).items()]


def get_input_console():
    print("Wklej dane (lub wpisz naciskając Enter po każdej linii,a po wprowadzeniu wszystkich danych \n"
          "naciśnij Enter bez wprowadzania tekstu): ")

    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)

    return _handle_input(lines)


def get_input_rchshop():
    with open('src/rchshop.txt', 'r') as f:
        res = json.load(f)

    return res


def get_input_eq():
    with open('src/inventory.txt', 'r') as f:
        res = json.load(f)
        # paste response from https://rustchance.com/api/account/inventory?refresh=false&flames=false
    tmp = []
    for r in res["items"]:
        obj = {
            "name": r["market_hash_name"],
            "price": r["price"] / 100,
        }
        if obj["price"] == 0:
            continue
        tmp.append(obj)

    tmp = [(entry["name"], entry["price"]) for entry in tmp]

    result = [{"name": name,
               "price": price,
               "quantity": count} for (name, price), count in Counter(tmp).items()]

    return result
