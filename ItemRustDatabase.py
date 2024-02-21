import jsonpickle
import json
import os
from ItemRustDatabaseRecord import ItemRustDatabaseRecord
class ItemRustDatabase:

    def __init__(self, filename="rustItemDatabase.txt"):
        self.filename = filename
        self.records: dict[str, ItemRustDatabaseRecord] = {}

    def load_database(self):
        """ Load self.records from file"""
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                data = jsonpickle.decode(file.read())
            self.records = data
        else:
            print(f"File '{self.filename}' does not exist.")

    def save_database(self):
        """ Save self.records to file"""
        with open(self.filename, 'w') as f:
            # json.dump(obj_to_save, f)
            json_data = jsonpickle.encode(self.records)
            f.write(json_data)

    def update_record(self, itemrust):
        """ Replace previous record with new one or create new record"""
        self.records[itemrust.name] = ItemRustDatabaseRecord(itemrust)

    def delete_record(self, name):
        """ Delete record with given name whether it exists or not"""
        self.records.pop(name, None)

    def has_actual_record(self, name):
        """ If the item in the database and has not expired"""
        return name in self.records and not self._is_record_expired(name)

    def _is_record_expired(self, name):
        """ Is record with given name expired.
        Raises AttributeError if name is not in database."""
        if name not in self.records:
            raise AttributeError("Key '"+name+"' is not in database")
        # TODO implement
        return False

    def assign_data_to(self, itemrust):
        """ Assigns data from database to itemrust.
        Raises AttributeError if itemrust is not in database"""
        if itemrust.name not in self.records:
            raise AttributeError("Key '" + itemrust.name + "' is not in database")
        self.records[itemrust.name].assign_data_to(itemrust)