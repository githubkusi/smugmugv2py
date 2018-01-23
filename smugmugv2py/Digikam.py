import MySQLdb as Mdb


class Digikam:
    def __init__(self):
        self.bla = 'hello'

    @staticmethod
    def get_connection_and_cursor(user, passwd, db, host='localhost'):
        con = Mdb.connect(host, user, passwd, db)

        cursor = con.cursor()
        return con, cursor

    @staticmethod
    def get_url_path(cursor, image_id):
        query = """
        select Albums.relativePath, Images.name from Images, Albums 
        where Images.id = %{:d} and 
        Albums.id = Images.album 
        """.format(image_id)
        cursor.execute(query)
        return cursor.fetchone()

    @staticmethod
    def get_unsynced_image_id(cursor):
        query = """
        SELECT Images.Id
        FROM Images
        LEFT JOIN PhotoSharing ON PhotoSharing.imageid = Images.id
        WHERE PhotoSharing.imageid IS NULL
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        images_id = [x[0] for x in rows]
        return images_id

    @staticmethod
    def split_folder_album(path):
        s = path.split('/')
        folders = s[0:-1]
        album = s[-1]
        return folders, album


