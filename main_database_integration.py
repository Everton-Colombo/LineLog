import sqlite3
import pickle
import datetime

connection = sqlite3.connect("Main.sqlite", detect_types=sqlite3.PARSE_DECLTYPES)
connection.execute("CREATE TABLE IF NOT EXISTS products ("      # Creates Products table
                   "_id INTEGER PRIMARY KEY NOT NULL, "
                   "name TEXT NOT NULL UNIQUE, "
                   "quantity INTEGER NOT NULL, "
                   "cost INTEGER NOT NULL, "                    # Cost in cents
                   "retailPrice INTEGER NOT NULL, "             # Retail Price in cents
                   "creationDate TIMESTAMP NOT NULL)")

connection.execute("CREATE TABLE IF NOT EXISTS costumers ("     # Creates Costumers table
                   "_id INTEGER PRIMARY KEY NOT NULL, "
                   "name TEXT NOT NULL, "
                   "phoneNumber TEXT, "
                   "email TEXT, "
                   "dateOfBirth INTEGER NOT NULL, "             # Dumps of datetime.date class
                   "gender TEXT NOT NULL, "
                   "creationDate TIMESTAMP NOT NULL)")

connection.execute("CREATE TABLE IF NOT EXISTS salesHistory ("  # Creates SalesHistory table
                   "_id INTEGER PRIMARY KEY NOT NULL, "
                   "costumer INTEGER NOT NULL, "                # _id of the costumer
                   "UTCTime TIMESTAMP NOT NULL, "
                   "items INTEGER NOT NULL, "                   # Dumps of List class - [[item, quantity], []...]
                   "totalPrice INTEGER NOT NULL,"               # Total price in cents
                   "totalProfit INTEGER NOT NULL, "             # Total profit in cents
                   "paymentMethod INTEGER NOT NULL)")           # 1: cash, 2: debit, 3: credit

connection.execute("CREATE TABLE IF NOT EXISTS itemHistory ("   # Creates Item History table
                   "item INTEGER NOT NULL, "                    # _id of the Item
                   "UTCTime TIMESTAMP NOT NULL, "
                   "quantity INTEGER NOT NULL, "                # + for entries and - for sales
                   "sale INTEGER, "                             # _id of the Sale (only for quantity < 0)
                   "PRIMARY KEY (UTCTime, item))")              # Set primary key to be UTCTime and item


def _exists(table: str, column: str, value) -> bool:
    """

    :param table: Name of the table
    :param column: Name of the column to be searched
    :param value: Value to be searched
    :return: True if it exists, otherwise False
    :rtype: bool
    """

    result = connection.execute("SELECT {0} FROM {1} WHERE ({0} = ?)".format(column, table), (value,)).fetchone()

    return True if result else False


def _current_time() -> datetime.datetime:
    """
    A simple method that returns the current time in UTC.

    :rtype: datetime.datetime
    """
    return datetime.datetime.utcnow()


def register_item_movement(item: int, quantity: int, time: datetime.datetime = None, sale: int = None):
    """
        Register an item's movement to the database. If set to None,
    the time parameter defaults to _current_time() as time cannot be
    set to None into the database.
        This function does not check if the the item exists neither if
    the item's quantity in the database is valid for the operation. Therefore,
    only use this function after checking for those things as this function
    will insert an entry into the database even if those conditions are not
    were not met.

    :param item: The item which has moved
    :param quantity: How much the item moved
    :param time: When the item moved
    :param sale: Did it move in a sale? If so, which one?
    :rtype: None
    """

    connection.execute("INSERT INTO itemHistory (item, UTCTime, quantity, sale) VALUES (?, ?, ?, ?)",
                       (item, time if time else _current_time(), quantity, sale))
    connection.commit()


def new_product(name: str, quantity: int, cost: int, retail_price: int):
    """
        Adds a new product to the database. All cost values must
    be in cents.
        This function does check if the product passed has the
    same name as any other product already in the database and
    wont do anything if there's already a product with the same
    name.

    :param name: Name of the new product
    :param quantity: Start quantity of the new product
    :param cost: Cost of the product
    :param retail_price: Retail price of the product
    :rtype: None
    """

    if not _exists('products', 'name', name):
        cur = connection.execute("INSERT INTO products (name, quantity, cost, retailPrice, creationDate) "
                                 "VALUES (?, ?, ?, ?, ?)",
                                 (name, quantity, cost, retail_price, datetime.date.today()))
        if quantity:
            register_item_movement(cur.lastrowid, quantity)
        connection.commit()


def delete_product(id_: int):
    """
        Deletes a product only if its not been sold yet. (If it has,
    this function will return 1, else None.

    :param id_:
    :return:
    """

    for receipt in connection.execute("SELECT items FROM salesHistory").fetchall():
        items_list = pickle.loads(receipt[0])
        for item in items_list:
            if item[0] == id_:
                return 1
    connection.execute("DELETE FROM products WHERE _id = ?", (id_,))
    connection.commit()


def new_costumer(name: str, date_of_birth: datetime.date, gender: int, phone_number: str = None, email: str = None):
    """
        Adds a new costumer to the database.

    :param name: str
    :param date_of_birth: datetime.date
    :param gender: int 0 for men and 1 for women
    :param phone_number: str
    :param email: str
    :rtype: None
    """

    connection.execute("INSERT INTO costumers (name, phoneNumber, email, dateOfBirth, gender, creationDate) "
                       "VALUES (?, ?, ?, ?, ?, ?)",
                       (name, phone_number, email, pickle.dumps(date_of_birth), gender, datetime.date.today()))
    connection.commit()


def delete_costumer(id_: int):
    """
        Deletes a costumer only if the costumer has no history. (If it does,
    the function returns 1, else None.

    :param id_:
    :return:
    """

    echeck = connection.execute("SELECT * FROM salesHistory WHERE costumer = ?", (id_,)).fetchone()
    if echeck:
        return 1
    else:
        connection.execute("DELETE FROM costumers WHERE _id = ?", (id_,))
        connection.commit()


def register_sale(items: list, costumer_id: int, payment_method: int):
    """
        Registers a new sale to the database. There's no need to pass
    the total price of the sale neither the total profit of the sale as
    this function takes care of those things for you.
        This functions does not check if the products passed exist neither
    if the costumer_id passed is valid. Therefore, only use this function
    after checking for those things as this function does not handle any
    exceptions that could possibly be raised.

    :param items: list of lists of ints
    :param costumer_id: int
    :param payment_method: Either cash, debit or credit
    :rtype: None
    """

    curr_time = _current_time()     # Stores current time so that all entries have the same time

    total_price = 0     # Initializes total price
    total_profit = 0    # Initializes total profit

    for item in items:  # First loop to calculate total price and total profit, also to update product quantity
        query = connection.execute("SELECT retailPrice, cost, quantity FROM products WHERE (products._id = ?)",
                                   (item[0],))
        row = query.fetchone()                                      # Gets first value to calculate on
        total_price += row[0] * item[1]                             # Calculates total price
        total_profit += (row[0] * item[1]) - (row[1] * item[1])     # Calculates total profit

        connection.execute("UPDATE products SET quantity = ? WHERE (_id = ?)",
                           (row[2] - item[1], item[0]))                             # Updates quantity on database

    cursor = connection.cursor()        # This cursor is created only to be used in sale_id = cursor.lastrowid
    cursor.execute("INSERT INTO salesHistory (costumer, UTCTime, items, totalPrice, totalProfit, paymentMethod)"
                   " VALUES (?, ?, ?, ?, ?, ?)",
                   (costumer_id, curr_time, pickle.dumps(items), total_price, total_profit, payment_method))
    # Inserts sale in db

    sale_id = cursor.lastrowid                                              # Gets this sale's id
    for item in items:
        register_item_movement(item[0], -item[1], curr_time, sale_id)       # Registers each item's movement

    connection.commit()     # Commit changes


def edit_product(product_id: int, column: str, value):
    """
        Edits a product on WHERE name = product_name. (name can only be
    edited if it's unique)

    :param product_id: ID of the product
    :param column: What column of products to edit?
    :param value: (str or int) New value.
    :returns: 1 (int) if the name already exists. Otherwise, None
    :rtype: None or int
    """

    if not _exists('products', 'name', value)\
            if column is "name" else True:   # Checks for exists if column is name (continuation of previous line)
        connection.execute("UPDATE products SET {} = ? WHERE (_id = ?)".format(column), (value, product_id))
        connection.commit()
    else:
        return 1    # Returns 1 if the name already exists in another entry. This is useful for displaying error
                    # messages later on.


def edit_costumer(costumer_id: str, column: str, value):
    """
        Edits any costumer's information on WHERE _id = costumer_id. (_id cannot be edited)

    :param costumer_id: _id of the costumer
    :param column: Column to be edited
    :param value: New value
    :rtype: None
    """

    connection.execute("UPDATE costumers SET {} = ? WHERE (_id = ?)".format(column), (value, costumer_id))
    connection.commit()


if __name__ == "__main__":
    # new_product("Coca Cola", 3, 200, 300)
    # new_costumer("Tim", datetime.date(1995, 2, 15), "Male", "+1 (547) 698-5421", "tim@mail.com")
    # register_sale([[1, 2]], 1)
    # new_product("Chocolate X", 5, 100, 500)
    # new_product("Azeite Oliva", 15, 650, 1200)
    # new_costumer("Paulo", datetime.date(1995, 2, 15), "Male", "+9544", "paulo@bol.com.br")
    # new_costumer("Carol", datetime.date(1995, 2, 15), "Female", "+9544", "carol95@bol.com.br")
    # register_sale([[2, 2], [3, 5]], 2)
    # register_sale([[2, 3], [3, 10]], 3)
    connection.close()

