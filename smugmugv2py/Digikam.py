import MySQLdb as Mdb


class Digikam:
    def __init__(self):
        self.bla = 'hello'

    @staticmethod
    def get_connection_and_cursor(params):
        con = Mdb.connect(
            host=params.host,
            user=params.user,
            passwd=params.password,
            db=params.database)

        cursor = con.cursor()
        return con, cursor

    @staticmethod
    def get_url_path(cursor, image_id):
        query = """
        select relativePath from Images, Albums 
        where Images.id = %{:d} and 
        Albums.id = Images.album 
        """.format(image_id)
        cursor.execute(query)
        relative_path = cursor.fetchall()

        # remove first slash
        return relative_path[1:]



