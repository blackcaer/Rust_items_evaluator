class ItemRustDatabase:

    def __init__(self, ):
        self.items = {}  # should contain ItemRust

    def make_item(self, name, data):
        return {"name": name, "data": data}

    def add(self, name, data):
        self.items.update(self.make_item(name, data))
