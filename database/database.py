import sqlite3

from .table import Table


class Database:
    def __init__(self, database_name):
        self.name = database_name
        self.db = sqlite3.connect(database_name)
        self.schemas = {
            "Users": [
                ["userID", "char(32)", "PRIMARY KEY", "NOT NULL"],
                ["firstName", "char(256)", "NOT NULL"],
                ["lastName", "char(256)", "NOT NULL"],
                ["email", "char(256)", "NOT NULL"],
                ["publicKey", "text", "NOT NULL"],
                ["frozen", "int(1)", "NOT NULL"],
            ]
        }

    def __getitem__(self, table_name):
        if not (table_name in self.get_table_names()):
            return None
        table = Table(self, table_name, self.schemas[table_name])
        return table

    def execute_only(self, statement):
        self.db.cursor().execute(statement)

    def execute(self, statement):
        cur = self.db.cursor()
        return cur.execute(statement)

    def has_table(self, table_name):
        sql = f'select * from sqlite_schema where name = "{table_name}" and type = "table";'
        for i in self.execute(sql):
            return True
        return False

    def get_table_names(self):
        sql = 'select name from sqlite_schema where type = "table";'
        return [i[0] for i in self.execute(sql)]

    def drop_table(self, table_name):
        self.execute_only(f'drop table {table_name}')

    def force_reset(self):
        tables = self.get_table_names()
        for table in tables:
            self.drop_table(table)
        for table in self.schemas.keys():
            fields = self.schemas[table]
            self.execute_only(f"create table {table} ({','.join([' '.join(i) for i in fields])})")

    def commit(self):
        self.db.commit()

    def close(self):
        self.db.close()

    def reconnect(self):
        try:
            self.db.close()
        except Exception:
            pass
        self.db = sqlite3.connect(self.name)
