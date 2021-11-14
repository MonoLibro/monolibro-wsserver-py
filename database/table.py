class Table:
    def __init__(self, db, table_name, schema):
        self.db = db
        self.table_name = table_name
        self.schema = schema

    def get_primary_key(self):
        keys = []
        for field in self.schema:
            if "PRIMARY KEY" in field[2:]:
                keys.append(field[0])
        return keys

    def __getitem__(self, keys):
        try:
            if type(keys) == dict:
                conditions = []
                for column in keys.keys():
                    value = keys[column]
                    conditions.append(f"{column} = '{value}'")
                return self.db.execute(f"select * from {self.table_name} where {' and '.join(conditions)};")
            else:
                primary_key = self.get_primary_key()[0]
                return self.db.execute(f'select * from {self.table_name} where {primary_key} = "{keys}"')
        except Exception:
            return []

    def __delitem__(self, keys):
        try:
            if type(keys) == dict:
                conditions = []
                for column in keys.keys():
                    value = keys[column]
                    conditions.append(f"{column} = '{value}'")
                return self.db.execute(f"delete from {self.table_name} where {' and '.join(conditions)};")
            else:
                primary_key = self.get_primary_key()[0]
                return self.db.execute(f'delete from {self.table_name} where {primary_key} = "{keys}"')
        except Exception:
            pass

    def insert(self, values):
        values = [f"'{i}'" for i in values]
        values_str = ", ".join(values)
        self.db.execute(f"insert into {self.table_name} values ({values_str})")
