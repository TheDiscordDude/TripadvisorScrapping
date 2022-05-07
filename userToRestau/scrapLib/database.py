import mysql.connector as mysql
from mysql.connector.cursor_cext import CMySQLCursor


# ------------ CONNECT TO DATABASE ------------

def db_connect() -> tuple:
    """
    Connect to database and return the db and cursor
    :return: a tuple with the db and the cursor
    """
    db = mysql.connect(host='localhost', port='3306', user='root', passwd='', database='tripadvisor')
    cursor = db.cursor()
    return db, cursor


# ------------ VERIFICATIONS ------------

def restaurant_exists_in_database(restau_id: int, cursor: CMySQLCursor) -> bool:
    """
    Checks if the restaurant is already stored in database
    :param restau_id: the Id of the current restaurant
    :param cursor: the db cursor
    :return: a boolean : True if the restaurant is in the database
    """
    condition = "restauid=" + str(restau_id)
    result = get_column_from_table("restauid", "restaurant", cursor, conditions=condition)
    return len(result) > 0


def user_exists_in_database(user_id: str, cursor: CMySQLCursor) -> bool:
    """
    Checks if the current user is already in database
    :param user_id: the Id of the current User
    :param cursor: the db cursor
    :return: a boolean : True if the user is already in the database
    """
    condition = "userid='" + user_id + "'"
    result = get_column_from_table("userid", "user", cursor, conditions=condition)
    return len(result) > 0


def review_exists_in_database(user_id: str, restau_id: int, date, cursor: CMySQLCursor):
    """
    Checks if the current review is in the database
    :param user_id: the id of the author
    :param restau_id: the id of the restaurant
    :param date: the visit date
    :param cursor: the db cursor
    :return: a boolean : True if the review is already in the database
    """
    query = "SELECT reviewid from review WHERE userid=%s AND restauid=%s AND visitdate"
    if date:
        query += "=%s"
        values = (user_id, restau_id, date)
    else:
        query += " is NULL"
        values = (user_id, restau_id)
    cursor.execute(query, values)
    res = cursor.fetchall()
    return len(res) > 0


# ------------ UPLOADS ------------

def upload_restau(infos: dict, db, cursor: CMySQLCursor) -> bool:
    """
    Uploads the restaurants based on his infos
    :param infos: a dictionary containing all the infos of the restaurant
    :param db: the Databse
    :param cursor: the cursor the db
    :return: True if the upload is a sucess
    """
    table = "restaurant"
    query = "INSERT INTO {} (name, restauid, adress, phone, rating, nbreviews) " \
            "VALUES (%s, %s, %s, %s, %s, %s)".format(table)
    values = (infos["name"], infos["id"], infos["address"], infos["phone"], infos["rating"], infos["nbreviews"])
    try:
        cursor.execute(query, values)
        db.commit()
        return True
    except mysql.IntegrityError as e:
        print(str(e))
    except Exception as e:
        print(str(e))
    return False


def upload_user(infos: dict, db, cursor: CMySQLCursor) -> bool:
    """
    Uploads the user based on his infos
    :param infos: a dictionary containing all the infos of the user
    :param db: the Databse
    :param cursor: the cursor the db
    :return: True if the upload is a sucess
    """
    table = "user"
    query = "INSERT INTO {} (userid, joindate, pseudo, location, likes, photos, reviews, description) " \
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)".format(table)
    values = (infos["userid"], infos["joindate"], infos["pseudo"], infos["location"], infos["likes"],
              infos["photos"], infos["reviews"], infos["description"])
    try:
        cursor.execute(query, values)
        db.commit()
        return True
    except mysql.IntegrityError as e:
        print(str(e))
    except Exception as e:
        print(str(e))
    return False


def upload_review(infos: dict, db, cursor: CMySQLCursor) -> bool:
    """
    Uploads the review based on his infos
    :param infos: a dictionary containing all the infos of the review
    :param db: the Databse
    :param cursor: the cursor the db
    :return: True if the upload is a sucess
    """
    table = "review"
    query = "INSERT INTO {} (userid, restauid, rating, title, content, visitdate) " \
            "VALUES (%s, %s, %s, %s, %s, %s)".format(table)
    values = (infos["userid"], infos["restauid"], infos["rating"], infos["title"], infos["content"], infos["visitdate"])
    try:
        cursor.execute(query, values)
        db.commit()
        return True
    except mysql.IntegrityError as e:
        print(str(e))
    except Exception as e:
        print(str(e))
    return False


def update_last_user(restau_id, cursor, db):
    query = "UPDATE t_last_usr SET userid='" + restau_id + "';"
    cursor.execute(query)
    db.commit()


# ------------ UTILS ------------

def get_number_reviews_for_restaurant(restau_id: int, cursor: CMySQLCursor) -> int:
    """
    Get the number of reviews a restaurant has in database
    :param restau_id: the ID of the restaurant
    :param cursor: the db's cursor
    :return: an int
    """
    conditions = "restauid=" + str(restau_id)
    result = get_column_from_table("count(*)", "review", cursor, conditions=conditions)
    result = int(result[0])
    return result


def get_column_from_query(query, cursor: CMySQLCursor, values=None):
    if not values:
        cursor.execute(query)
    else:
        cursor.execute(query, values)
    res = cursor.fetchall()
    res = [j[0] for j in res]
    return res


def get_column_from_table(column: str, table: str, cursor: CMySQLCursor, order_by: str = None, conditions: str = None,
                          limit: int = None) -> list:
    """
    Gets a specific column of a table in database
    :param column: the name of the desired column
    :param table: the name of the table
    :param cursor: the cursor of the database
    :param order_by: (optional) it's the column desired for sorting the results
    :param conditions: (optional) gives the possibility to add conditions to the requests
    :param limit: (optional) it's an int that can be used to limit the number of output
    :return: a list of value contained in the specified column
    """
    query = "SELECT {} from {} ".format(column, table)
    if conditions:
        query += "WHERE {} ".format(conditions)
    if order_by:
        query += "ORDER BY {} ".format(order_by)
    if limit:
        query += "LIMIT {} ".format(str(limit))
    cursor.execute(query)
    res = cursor.fetchall()
    res = [j[0] for j in res]
    return res


def update_restau_link(link: str, db, cursor: CMySQLCursor) -> bool:
    """
    Set the restaurant Link in db from not treated to treated
    :param link: the url
    :param db: the Database
    :param cursor: the cursor of the database
    :return: True nothing went wrong
    """
    table = "linkRestaurants"
    query = "UPDATE linkRestaurants " \
            "SET treated=TRUE " \
            "WHERE url=%s".format(table)
    values = (link,)
    try:
        cursor.execute(query, values)
        db.commit()
        return True
    except mysql.IntegrityError as e:
        print(str(e))
    except Exception as e:
        print(str(e))
    return False
