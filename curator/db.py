import sqlite3
import re
import os
import os.path

class DatabaseReadError(Exception): pass
class DatabaseWriteError(Exception): pass

class Database:
    
    def __init__(self,path):
        # Connect to database, initialize table if empty
        try:
            self.db_conn = sqlite3.connect(path)
            self.cur = self.db_conn.cursor()
            try:
                self.cur.execute('select * from wallpapers')
            except:
                self.__init_db_if_empty()                
        except sqlite3.OperationalError as e:
            if e.message == 'attempt to write a readonly database':
                raise DatabaseWriteError()
            elif e.message == 'unable to open database file':
                raise DatabaseReadError()
        
    def __del__(self):
        self.cur.close()
        self.db_conn.commit()
        self.db_conn.close()
        
    def __init_db_if_empty(self):
        self.cur.execute('create table wallpapers (id integer primary key, name text, path text, rej int)')
        self.db_conn.commit()

    def __add(self,files):
        for path in files:
            name = os.path.basename(path)
            # By default all are nonrejected
            rej = 0
            self.cur.execute('insert into wallpapers (name, path, rej) values (?,?,?)',(name,path,rej))
        self.db_conn.commit()
                
    def set_directory(self, dir):
        # Notice that it completely wipes the table!
        self.cur.execute('delete from wallpapers')
        image_regex = re.compile(r".+\.jpg|.+\.png|.+\.gif|.+\.bmp")
        self.__add(filter(lambda file: image_regex.match(file), os.listdir(dir)))

    def get_entry_by_key(self, key):
        self.cur.execute('select name, path, rej from wallpapers where id == ?', key)
        self.cur.fetch()

    def add_by_path(self, path):
        self.__add([path])

    def remove_by_path(self, path):
        self.cur.execute('delete from wallpapers where path == ?', path)
        self.db_conn.commit()

    def select_all_paths(self):
        self.cur.execute('select path from wallpapers')
        self.cur.fetchall()

    def select_all_nonrejects(self):
        self.cur.execute('select id from wallpapers where rej == 0')
        self.cur.fetchall()

    def reject_by_key(self, key):
        self.cur.execute('update wallpapers set rej = 1 where id == ?', key)
        self.db_conn.commit()

    def reject_by_path(self, path):
        self.cur.execute('update wallpaper set rej = 1 where path == ?', path)
        self.db_conn.commit()

    def is_reject_by_key(self, key):
        self.cur.execute('select rej from wallpapers where id == ?', key)
        if self.cur.fetch() == 0:
            return True
        else:
            return False
