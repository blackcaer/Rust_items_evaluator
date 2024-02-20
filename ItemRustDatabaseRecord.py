import ItemRust
import time


class ItemRustDatabaseRecord:
    """ Encapsulates data of ItemRust for ItemRustDatabase class"""
    def __init__(self,itemrust):
        self.name = None
        self.iteminfo = None
        self.price_sm = None
        self.pricehistory_sm = None
        self.sale_offers_sm = None
        self.price_sp = None
        self.pricehistory_sp = None
        self.sales_histogram_sp = None
        self.timestamp = None

        self.save_data(itemrust)

    def save_data(self,itemrust):
        if not itemrust.all_success:
            raise RuntimeError("Itemrust all_success is false")

        self.name = itemrust.name
        self.iteminfo = itemrust.iteminfo

        self.price_sm = itemrust.price_sm
        self.pricehistory_sm = itemrust.pricehistory_sm
        self.sale_offers_sm = itemrust.sale_offers_sm

        self.price_sp = itemrust.price_sp
        self.pricehistory_sp = itemrust.pricehistory_sp
        self.sales_histogram_sp = itemrust.sales_histogram_sp

        self.timestamp = time.time()