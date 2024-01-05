from os.path import dirname, realpath
import sys
from time import sleep
import warnings

import pymysql.cursors

sys.path.insert(0, dirname(dirname(realpath(__file__))))


from Classes.Config import Config


class Mysql:

    @staticmethod
    def connect(host, user, password, database, charset="utf8", nb_try=0, port=3306):
        try:
            return pymysql.connect(host=host, user=user, password=password, charset=charset, cursorclass=pymysql.cursors.DictCursor, database=database, port=port)
        except Exception as e:
            code_erreur = e.args[0]
            print("Exception MYSQL Connect Code : " + str(code_erreur))
            # Connections impossible
            if code_erreur == 2003 or code_erreur == 2013:
                nb_try += 1
                sleep(nb_try * 5)
                return Mysql.get_connection(host, user, password, database, nb_try=nb_try)
          

    @staticmethod
    def get_connection(host=Config.MYSQL_HOST, user=Config.MYSQL_USER, password=Config.MYSQL_PWD, database=Config.MYSQL_DB, nb_try=0):
        return Mysql.connect(host=host, user=user, password=password, database=database, nb_try=0)

    @staticmethod
    def execute_select_array(sql, connection=None, close=True, params=None):
        if connection is None:
            connection = Mysql.get_connection()

        with connection.cursor() as cursor:
            try:
                if params is None:
                    cursor.execute(sql)
                else:
                    cursor.execute(sql, params)
            except Exception as e:
                print("Exception " + str(e))
                if e.args[0] == 1213 or e.args[0] == 1205:  # Deadlock détecté, on reessaie
                    print("C'est un deadlock, on réessaie")
                    return Mysql.execute_select_array(sql=sql, connection=connection, close=close, params=params)
                elif e.args[0] == 2013 or e.args[0] == 2006:  # Connection lost
                    print("C'est une perte de connection, on la réouvre")
                    host = connection.host
                    if host == Config.MYSQL_HOST:
                        connection = Mysql.get_connection()

                    return Mysql.execute_select_array(sql=sql, connection=connection, close=close, params=params)
                else:
                    print("Exception inconnue. Query = " + str(sql))
                    raise e

            results = cursor.fetchall()
        if close:
            connection.close()
        return results

    @staticmethod
    def execute_insert(sql, connection=None, close=True, return_id=False, params=None, ignore_missing_table_error=False):
        """
            params est un tuple permettant de déléguer l'échappement à la librairie pymysql
            sql = "INSERT INTO TABLE_A(COL_A,COL_B) VALUES(%s, %s)"
            params = (value1, value2)
        """
        warnings.simplefilter("ignore")

        if connection is None:
            connection = Mysql.get_connection()

        with connection.cursor() as cursor:
            try:
                if params is None:
                    result = cursor.execute(sql)
                else:
                    result = cursor.execute(sql, params)
                connection.commit()
            except Exception as e:
                print("Exception " + str(e))
                if e.args[0] == 1213 or e.args[0] == 1205:  # Deadlock détecté, on réessaie
                    print("C'est un deadlock, on réessaie")
                    return Mysql.execute_insert(sql=sql, return_id=return_id, connection=connection, close=close, params=params)
                elif e.args[0] == 2013 or e.args[0] == 2006:  # Connection lost
                    print("C'est une perte de connection, on la réouvre")
                    host = connection.host
                    if host == Config.MYSQL_HOST:
                        connection = Mysql.get_connection()

                    return Mysql.execute_insert(sql=sql, return_id=return_id, connection=connection, close=close, params=params)
                elif e.args[0] == 1146 and ignore_missing_table_error:
                    print("La table n'existe pas. Query = " + str(sql))
                    return False
                else:
                    print("Exception inconnue. Query = " + str(sql))
                    raise e

            if not return_id:
                if close:
                    connection.close()
                return result

            cursor.execute("SELECT LAST_INSERT_ID() AS id")
            result_id = cursor.fetchone()
        if close:
            connection.close()
        return result_id.get("id")

    @staticmethod
    def tweet_exists(local_id, connection=None, close=True):
        result = {}
        result["id"] = None

        if connection is None:
            connection = Mysql.get_connection()
        query = "SELECT id FROM tweets WHERE id = '" + str(local_id) + "'"
        social_id = Mysql.execute_select_array(query, connection=connection, close=close)
        if social_id is not None:
            result["id"] = social_id
            return result
        return None