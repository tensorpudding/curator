import os
import os.path
import re

import sqlite3

from . import thumbnail

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
                self.__execute('select * from wallpapers')
            except:
                self.__init_db_if_empty()                
        except sqlite3.OperationalError as e:
            if e.message == 'attempt to write a readonly database':
                raise DatabaseWriteError()
            elif e.message == 'unable to open database file':
                raise DatabaseReadError()

        self.directory = directory
        self.thumbnailer = thumbnail.ThumbnailGenerator()

    def __execute(self, sql_string, parameters = None):
        """
        Execute the given SQL query with the given parameters, then commit.
        """
        if parameters:
            self.cur.execute(sql_string, parameters)
        else:
            self.cur.execute(sql_string)
        self.db_conn.commit()

    def __fetchone(self, sql_string, parameters = None):
        """
        Execute the given SQL, fetch a single result.
        """
        if parameters:
            self.cur.execute(sql_string, parameters)
        else:
            self.cur.execute(sql_string)
        return self.cur.fetchone()

    def __fetchall(self, sql_string, parameters = None):
        """
        Execute the given SQL, fetch all matching results.
        """
        if parameters:
            self.cur.execute(sql_string, parameters)
        else:
            self.cur.execute(sql_string)
        return self.cur.fetchall()

    def __init_db_if_empty(self):
        """
        Recreate the database table.
        """
        self.__execute("create table wallpapers " +
                       "(path text, hide integer, thumb text)")

    def __get_files_in_directory(self, directory):
        """
        Helper function which scans the given directory and returns a set
        of files.
        """
        files = set()
        for file in os.path.os.listdir(directory):
            file = os.path.join(directory, file)
            if os.path.isdir(file):
                files.union(self.__get_files_in_directory(file))
            if os.path.islink(file):
                return
            if os.path.isfile(file):
                if Database.IMAGE_REGEX.match(file):
                    files.add(file)
        return files

    def reinitialize(self, directory = None):
        """
        Re-initialize the database. Wipe out existing table and rescan.
        The argument provides a new directory.

        Hide statuses are lost.
        """
        self.__execute('delete from wallpapers')
        if directory:
            self.directory = directory
        self.update()

    def hide_wallpaper(self, path):
        """
        Marks a wallpaper as hidden.
        """
        self.__execute("update wallpapers set hide = 1 where path == ?",
                           (path,))

    def get_thumbnail(self, path):
        """
        Get a thumbnail from the given wallpaper.
        """
        pass

    def get_all_wallpapers(self, visible = None):
        """
        Returns a list of all wallpapers in the database.
        If passed visible = True, restrict to visible wallpapers.
        If passed visible = False, restrict to hidden wallpapers.
        """
        if visible == None:
            paths = self.__fetchall('select path from wallpapers')
        elif visible == True:
            paths = self.__fetchall("select path from wallpapers where hide = 0")
        elif visible == False:
            paths = self.__fetchall("select path from wallpapers where hide = 1")
        return map(lambda tup: tup[0], paths)

    def is_in(self, path):
        """
        Returns True if the given wallpaper is in the database, and False
        otherwise.
        """
        if self.__fetchone("select path from wallpapers where path = ?",
                           (path,)):
            return True
        else:
            return False

    def is_hidden(self, path):
        """
        Returns True if the given wallpaper is hidden, and False otherwise.
        """
        if self.__fetchone("select hide from wallpapers where path = ?",
                           (path,)) == (1,):
            return True
        else:
            return False

    def update(self):
        """
        Set the database to update. It will compare the current directory state
        with the database, and add and remove entries as appropriate.

        Entries which are added are marked as shown by default.
        """
#        pass
#         # FIX: this is probably inefficient (but it's kinda idiomatic)
        files = self.__get_files_in_directory(self.directory)
        old_files = set(self.get_all_wallpapers())
        adds = files.difference(old_files)
        removes = old_files.difference(files)
        for file in adds:
            self.__execute("insert into wallpapers (path, hide, thumb)" +
                           " values (?, ?, ?)", (file,0,"foo"))
        for file in removes:
            self.__execute("delete from wallpapers where path = ?", (file,))
#            self.thumbnailer.delete(path)
        for file in files:
            self.thumbnailer.update(file, self.get_thumbnail(file))
