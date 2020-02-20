import sqlite3
import helpers

connection = None  # database connection


# setup connection to sqlite3 database
def create_connection(db_file):
    global connection
    if connection is None:
        try:
            connection = sqlite3.connect(db_file)

            # check if table with links exist
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='links';")

            # if table links not exist create table links
            if cursor.fetchone() is None:
                cursor.execute("CREATE TABLE links (link text UNIQUE);")
                connection.commit()

        except Exception as e:
            helpers.write_to_log("Catch from db.create_connection()\n" + str(e))
            connection.close()


# check if links exists in db
# return True or False
def check_link(link):
    global connection
    is_link_exists = True
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT link FROM links WHERE link='" + link + "'")

        # if link not exist add it to db
        if cursor.fetchone() is None:
            is_link_exists = False
        return is_link_exists

    except Exception as e:
        helpers.write_to_log("Catch from db.check_link()\n" + str(e))
        connection.close()


# added record with ynet news link to database
# return True if added and False if not added
def add_link_to_db(link):
    global connection
    is_link_added = check_link(link)
    try:
        cursor = connection.cursor()

        # if link not exist add it to db
        if is_link_added is False:
            cursor.execute("INSERT INTO links VALUES('" + link + "')")
            connection.commit()
    except Exception as e:
        helpers.write_to_log("Catch from db.add_link_to_db()\n" + str(e))
        connection.close()
