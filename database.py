import os
import sqlite3
import json
import requests


class Database:
    def __init__(self, main_path, database):
        """main_path - database fold path"""
        if os.path.exists(main_path):
            self.main_path = main_path
        self.database = database

    def new_directory(self, dir_name):
        path = os.path.join(self.main_path, dir_name)

        if os.path.exists(path):
            return 'fold already exist'

        return os.mkdir(path)

    def download_photo(self, user_id, url, photo_name):
        path = os.path.join(f'{self.main_path}', f'{user_id}', f'{photo_name}')
        r = requests.get(url).content
        with open(path, 'wb') as f:
            f.write(r)
        return path

    def photo_database(self, user_id, format="png"):
        path = os.path.join(f'{self.main_path}', f'{user_id}')
        list_of_files = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.split('.')[-1] == format:
                    list_of_files.append(file)
        return list_of_files

    def next_image_number(self, list_of_files, format='png', sep="%"):
        if list_of_files == []:
            return 0
        return (int(max([int('.'.join(i.split('.')[:-1]).split(sep)[-1]) for i in list_of_files])) + 1)

    def get_file(self, user_id: str, file_name: str):
        path = os.path.join(self.main_path, user_id)
        list_of_files = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file == file_name:
                    return file
        return False

    def save_json(self, user_id, json_dict, name_file):
        path = os.path.join(f"{self.main_path}", f"{user_id}", f"{name_file}")
        out_file = open(f"{path}", "w")
        json.dump(json_dict, out_file, indent=6)
        out_file.close()
        return True

    def read_json(self, user_id, name_file):
        path = os.path.join(f'{self.main_path}', f"{user_id}", f"{name_file}")
        file = open(f'{path}')
        data = json.load(file)
        return data

    def sql_create_table(self, table_name: str, columns: list):
        con = sqlite3.connect(f"{self.database}")
        cur = con.cursor()
        # check if table already exist
        res = [i[0] for i in cur.execute(f"""SELECT name FROM sqlite_master WHERE type='table'""").fetchall()]
        if table_name in res:
            return False
        else:
            cur.execute(f"""CREATE TABLE {table_name} ({', '.join([str(i) for i in columns])})""")
            return True

    def get_from_table(self, table_name, columns='*'):
        con = sqlite3.connect(f"{self.database}")
        cur = con.cursor()
        res = [i[0] for i in cur.execute(f"""SELECT name FROM sqlite_master WHERE type='table'""").fetchall()]
        if table_name in res:
            if columns == '*':
                result = [i for i in cur.execute(f"""SELECT {columns} FROM {table_name}""").fetchall()]
                return result
            result = [i for i in cur.execute(
                f"""SELECT {", ".join([str(i) for i in columns])} FROM {table_name}""").fetchall()]
            return result
        else:
            return False

    def sql_insert_into_table(self, table, insert_info: list):
        con = sqlite3.connect(f"{self.database}")
        cur = con.cursor()
        cur.execute(f"""INSERT INTO {table} VALUES ({('?, '*len(insert_info))[:-2]})""", insert_info)
        result = [i for i in cur.execute(f"""SELECT * FROM {table}""")]
        con.commit()
        con.close()
        return result

    def sql_user_token_table(self, user_id, user_token):
        con = sqlite3.connect(f"{self.database}")
        cur = con.cursor()

        param = [user_id, user_token]
        cur.execute(f"""INSERT INTO user_token VALUES (?, ?)""", param)
        result = [i for i in cur.execute(f"""SELECT * FROM user_token""")]
        con.commit()
        con.close()
        return result


if __name__ == '__main__':
    d = Database('database/vk', 'database.db')
    # d.sql_create_table('test_user', ['user_token'])