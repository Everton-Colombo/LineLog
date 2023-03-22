import sqlite3
import pickle
from cryptography.fernet import Fernet
from os.path import isfile

if not isfile('usrkey.frnt'):                               # Generates a key if it does not exist
    with open('usrkey.frnt', 'wb') as file:
        pickle.dump(Fernet.generate_key(), file)


_key = None
with open('usrkey.frnt', 'rb') as file:
    _key = pickle.load(file)


connection = sqlite3.connect("Outer.sqlite")
connection.execute("CREATE TABLE IF NOT EXISTS users ("
                   "username TEXT PRIMARY KEY NOT NULL, "
                   "token INTEGER NOT NULL, "
                   "name TEXT NOT NULL, "
                   "role TEXT NOT NULL, "
                   "authority INTEGER NOT NULL)")


def _exists(table: str, column: str, value):
    """

        :param table: Name of the table
        :param column: Name of the column to be searched
        :param value: Value to be searched
        :return: True if it exists, otherwise False
        :rtype: bool
        """

    result = connection.execute("SELECT {0} FROM {1} WHERE ({0} = ?)".format(column, table), (value,)).fetchone()

    return True if result else False


def validate_user(user: str, password: str) -> int:
    """
        A simple function to check the credentials given. It may return
    one out of three values each time it's executed:
        ++ (1) If the credentials are all correct;
        ++ (-1) If either the username or the password given is blank
        ++ (-2) If the username given does not exist in the database
        ++ (-3) If the password given is incorrect

    :param user: str, username of the user
    :param password: str, password of the user
    :rtype: int
    """
    # 1: all good; -1: invalid user/password; -2: user doesnt exist; -3: incorrect password
    if user and password:
        if _exists("users", "username", user):
            token = pickle.loads(connection.execute("SELECT token FROM users WHERE (username = ?)",
                                                    (user,)).fetchone()[0])

            return 1 if Fernet(_key).decrypt(token) == password.encode('utf-8') else -3
        else:
            return -2
    else:
        return -1


def new_user(username: str, password: str, name: str, role: str, authority: int):
    """
        Creates a new user. This function does check for things like
    username existence and valid parameters.
        This function will return one of 3 values:
        ++ (1) If everything went alright
        ++ (-1) If the username already exists
        ++ (-2) If one or more fields is/are invalid(s)

    :param username:
    :param password:
    :param name:
    :param role:
    :param authority:
    :rtype: int
    """

    # 1: all good; -1: username exists; -2 invalid fields
    if username and password and name and role and authority:
        if not _exists("users", "username", username):
            f = Fernet(_key)
            token = f.encrypt(bytes(password.encode('utf-8')))

            connection.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                               (username, pickle.dumps(token), name, role, authority))
            connection.commit()
            return 1
        else:
            return -1
    else:
        return -2


def get_user_info(user: str):
    """
        Gets all the needed information from a user and returns
    it as a list:

        Ex.:
            [name, role, authority]
            ['Jake Klein', 'General Manager', 1]

    :param user:
    :rtype: tuple
    """
    return connection.execute("SELECT name, role, authority FROM users WHERE (username = ?)", (user,)).fetchone()


if __name__ == "__main__":
    # new_user("everton", "erc", "Everton Colombo", "Principal", 2)
    pass
