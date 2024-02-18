class ItemRustDatabase:

    def __init__(self, ):
        self.items = {}  # should contain ItemRust

    def add(self, name, data):
        self.items.update(self.make_item(name, data))

    def load(self):
        pass

    def update(self):
        pass