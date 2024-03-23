import types
from prettytable import PrettyTable
from ItemRust import ItemRust


def display_eval_items(items):
    table = PrettyTable(reversesort=True)
    rows = []
    avgdata = {"prices": [], "values": []}  # data for weighted average

    # TODO: przygotowac standardowe templatki (z enuma? w klasie? albo na razie w metodzie) do wyswietlania itemow

    def spsm_helper(item):
        if item.price_sp is not None:
            return round(item.price_sp / item.price_sm, 2)

    # prepare rows of prettytable
    for curr_item in items:
        curr_item: ItemRust = curr_item
        (field_names,row)=create_fields_rows(curr_item,
                                             ("name",lambda item: item.name),
                                             ("price_sm",lambda item:item.price_sm/100),
                                             ("liqval",lambda item:round(item.calc_liqval(),2)),
                                             ("value4one",lambda item:item.calc_value(quantity=1)),
                                             ("value",lambda item:item.calc_value()),
                                             ("price_sp",lambda item:item.price_sp/100 if item.price_sp is not None else None),
                                             ("sp/sm",lambda item:round(item.price_sp / item.price_sm, 2) if item.price_sp is not None else None)
                                             )

        rows.append(row)
        table.field_names = field_names
        continue

    for row in rows:
        table.add_row(row)

    print("Sorting by value")
    table.sortby = "value"
    print(table)


def create_fields_rows(data, *args):
    """
    :param data: Object containing all the required data for display functions in args.
    :param args: arg[0] - name of column arg[1]-  Functions creating cell for PrettyTable
    :type args: (str,function)
    :return: Tuple with
    :rtype:
    """
    row = []
    field_names=[]
    for arg in args:
        if not (isinstance(arg, tuple) and
                len(arg) == 2 and
                isinstance(arg[0], str) and
                isinstance(arg[1], types.FunctionType) and
                callable(arg[1])):
            raise ValueError("Incorrect arguments for " + create_fields_rows.__name__)
        #row.append([arg[0], arg[1](data)])
        row.append(arg[1](data))
        field_names.append(arg[0])
    return field_names, row