import sqlite3
import re
import os
import os.path

class CurateDatabaseReadError(Exception): pass
class CurateDatabaseWriteError(Exception): pass

class CurateDatabase:
    
    def __init__(path):
        # Connect to database, initialize table if empty
        try:
            self.db_conn = sqlite3.connect(path)
            self.cur = db_conn.cursor()
            cur.execute('select * from wallpapers')
            if self.cur.fetchall() == []:
                self.init_db_if_empty()
        except OperationalError as e:
            if e.message == 'attempt to write a readonly database':
                raise CurateDatabaseWriteError()
            elif e.message == 'unable to open database file':
                raise CurateDatabaseReadError()
        
    def __del__():
        self.cur.close()
        self.db_conn.commit()
        self.db_conn.close()
        
    def init_db_if_empty():
        self.cur.execute('create table wallpapers (id integer primary key, name text, path text, rej int)')
        self.db_conn.commit()

    def add(files):
        for path in files:
            name = os.path.basename(path)
            rej = 0
            self.cur.execute('insert into wallpapers (name, path, rej) values (?,?,?)',(name,path,rej))
        self.db_conn.commit()
                
    def set_directory(dir):
        # Notice that it completely wipes the table!
        self.cur.execute('delete * from wallpapers')
        image_regex = re.compile(r".+\.jpg|.+\.png|.+\.gif|.+\.bmp")
        self.add(filter(lambda file: image_regex.match(file), os.listdir(dir)))

    def get_entry_by_key(key):
        self.cur.execute('select name, path, rej from wallpapers where id == ?', key)
        self.cur.fetch()

    def select_all_nonrejects():
        self.cur.execute('select name, path, rej from wallpapers where rej == 0')
        self.cur.fetchall()

    def reject_by_key(key):
        self.cur.execute('update wallpaper set rej = 1 where id == ?', key)
        self.db_conn.commit()
