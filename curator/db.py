import sqlite3
import re
import os
import os.path

class DatabaseReadError(Exception): pass
class DatabaseWriteError(Exception): pass

class Database:
    """
    Class to abstract the connection to the database.

    To add wallpapers, use add_wallpaper(path)
    To hide wallpapers, use hide_wallpaper(path)

    To update the database, use update()
    To re-initialize the database, use reinitialize()
    """
    IMAGE_REGEX = re.compile(r".+\.jpg|.+\.png|.+\.gif|.+\.bmp")
    def __init__(self, directory, path = ":memory:"):
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
        self.directory = directory

    def __del__(self):
        self.cur.close()
        self.db_conn.commit()
        self.db_conn.close()

    def __init_db_if_empty(self):
        """
        Recreate the database table.
        """
        self.cur.execute(("create table wallpapers"
                          "(path text, rej integer)"))
        self.db_conn.commit()

    def __get_files_in_directory(self, directory):
        """
        Helper function which scans the given directory and returns a set
        of files.
        """
        files = set()
        for file in os.path.os.listdir(directory):
            file = os.path.join(directory, file)
            if os.path.isdir(file) and self.recurse_subdirectories:
                files.union(self.__get_files_in_directory(file))
            if os.path.islink(file):
                return
            if os.path.isfile(file):
                if Database.IMAGE_REGEX.match(file):
                    files.add(file)
        return files

    def _remove_wallpaper(self, path):
        """
        Remove a file from the database

        You oughtn't mess with this directly
        """
        self.cur.execute("delete from wallpapers where path = ?", (path,))
        self.db_conn.commit()

    def reinitialize(self, directory = None):
        """
        Re-initialize the database. Wipe out existing table and rescan.
        The argument provides a new directory.

        Hide statuses are lost.
        """
        self.cur.execute('delete from wallpapers')
        if directory:
            self.directory = directory
        self.update()

    def add_wallpaper(self, path, visible = True):
        """
        Adds the given wallpaper to the database.
        """
        self.cur.execute("insert into wallpapers (path, rej) values (?,?)",
                         (path,0))
        self.db_conn.commit()

    def hide_wallpaper(self, path):
        """
        Marks a wallpaper as hidden.
        """
        self.cur.execute("update wallpapers set rej = 1 where path == ?",
                         (path,))
        self.db_conn.commit()

    def get_all_wallpapers(self, visible = None):
        """
        Returns a list of all wallpapers in the database.
        If passed visible = True, restrict to visible wallpapers.
        If passed visible = False, restrict to hidden wallpapers.
        """
        if visible == None:
            self.cur.execute('select path from wallpapers')
        elif visible == True:
            self.cur.execute("select path from wallpapers where rej = 0")
        elif visible == False:
            self.cur.execute("select path from wallpapers where rej = 1")
        return map(lambda tup: tup[0], self.cur.fetchall())

    def is_in(self, path):
        """
        Returns True if the given wallpaper is in the database, and False
        otherwise.
        """
        self.cur.execute("select path from wallpapers where path = ?",
                         (path,))
        if self.cur.fetchone():
            return True
        else:
            return False

    def is_hidden(self, path):
        """
        Returns True if the given wallpaper is hidden, and False otherwise.
        """
        self.cur.execute("select rej from wallpapers where path = ?",
                                  (path,))
        if hidden == (0,):
            return True
        else:
            return False

    def update(self):
        """
        Set the database to update. It will compare the current directory state
        with the database, and add and remove entries as appropriate.

        Entries which are added are marked as shown by default.
        """
        # FIX: this is probably inefficient (but it's kinda idiomatic)
        files = self.__get_files_in_directory(self.directory)
        old_files = set(self.get_all_wallpapers())
        adds = files.difference(old_files)
        removes = old_files.difference(files)
        for file in adds:
            self.add_wallpaper(file)
        for file in removes:
            self.__remove_wallpaper(file)
