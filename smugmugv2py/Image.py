from iso8601 import parse_date


class Image(object):
    def __init__(self, image):
        self.uri = image["Uri"]
        self.title = image["Title"]
        self.caption = image["Caption"]
        self.keywords = image["Keywords"]
        self.filename = image["FileName"]
        self.archived_size = image["ArchivedSize"]
        self.image_key = image["ImageKey"]
        self.last_updated = parse_date(image["LastUpdated"]).replace(tzinfo=None)

    @classmethod
    def from_album_image(cls, image):
        image["Uri"] = image["Uris"]["Image"]
        return cls(image)

    @classmethod
    def get_image(cls, connection, image_uri):
        return cls(connection.get(image_uri)["Image"])

    @staticmethod
    def delete_image(connection, image_uri):
        return connection.delete(image_uri)

    @staticmethod
    def change_image(connection, image_uri, changes):
        return Image(connection.patch(image_uri, changes)["Response"]["Image"])