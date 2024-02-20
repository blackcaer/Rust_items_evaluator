import jsonpickle
import ItemRustDatabaseRecord
class ItemRustDatabase:

    def __init__(self, filename="rustItemDatabase.txt"):
        self.filename = filename
        self.records = {}  # should contain ItemRustDatabaseRecords

    def load_database(self):
        # load self.records from file
        pass

    def save_database(self):
        # save self.records to file
        pass

    def update_record(self, itemrust):
        # Replace previous record with new one or create new record
        pass

    def delete_record(self, name):
        # Delete record with given name
        pass

    def has_actual_record(self, name):
        # If the item in the database and has not expired
        pass

    def get_data(self):
        pass