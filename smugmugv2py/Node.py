from json import dumps
from pprint import pprint


class Node(object):
    def __init__(self, node):
        self.uri = node["Uri"]
        self.description = node["Description"]
        self.name = node["Name"]
        self.url_name = node["UrlName"]
        self.type = node["Type"]
        self.privacy = node["Privacy"]
        self.has_children = node["HasChildren"]

        if self.type == "Album" or self.type == "System Album":
            self.sort_method = node["SortMethod"]
            self.sort_direction = node["SortDirection"]
            if "Uri" in node["Uris"]["Album"]:
                self.album_uri = node["Uris"]["Album"]["Uri"]
            else:
                self.album_uri = node["Uris"]["Album"]
        elif self.type == "Folder":
            self.sort_method = node["SortMethod"]
            self.sort_direction = node["SortDirection"]
            if "Uri" in node["Uris"]["ChildNodes"]:
                self.__child_nodes = node["Uris"]["ChildNodes"]["Uri"]
            else:
                self.__child_nodes = node["Uris"]["ChildNodes"]

    @classmethod
    def get_node(cls, connection, node_uri):
        return cls(connection.get(node_uri)["Node"])

    def get_children(self, connection):
        ret = []

        if self.has_children:
            response = connection.get(self.__child_nodes)
            if 'Node' in response:
                nodes = response["Node"]
                for node in nodes:
                    this_node = Node(node)
                    ret.append(this_node)

        return ret

    def __create_child_node(self, connection, type, name, url, privacy, description):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        params = {
            'Type': type,
            'Name': name,
            'UrlName': url,
            'Privacy': privacy,
        }

        if description:
            params['Description'] = description

        return connection.post(self.__child_nodes, data=dumps(params), headers=headers)

    def create_child_folder(self, connection, name, url, privacy, description=None):
        response = self.__create_child_node(connection, 'Folder', name, url, privacy, description)

        if "Node" not in response["Response"]:
            pprint(response)

        return Node(response["Response"]["Node"])

    def create_child_album(self, connection, name, url, privacy, description=None):
        response = self.__create_child_node(connection, 'Album', name, url, privacy, description)

        if "Node" not in response["Response"]:
            pprint(response)

        return Node(response["Response"]["Node"])

    def delete_node(self, connection):
        return connection.delete(self.uri)

    def change_node(self, connection, changes):
        return connection.patch(self.uri, changes)["Response"]["Node"]

    @staticmethod
    def find_node(connection, root_node, name):
        for node in root_node.get_children(connection):
            if node.url_name == name:
                return node

        return None
