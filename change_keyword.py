#!/usr/bin/python3

from smugmugv2py import Connection, User, Node, Album, AlbumImage, Image, SmugMugv2Exception
from sys import stdout, stdin
from os import linesep, path
from pprint import pprint
from test_setup import api_key, api_secret, token, secret
from datetime import datetime
from json import dumps
from requests import exceptions


def do_indent(indent):
    for x in range(0, indent):
        stdout.write(" ")


def print_album(node, indent):
    album = Album.get_album(connection, node.album_uri)
    stdout.write(", " + str(album.image_count) + " images")
    images = album.get_images(connection)
    for image in images:
        do_indent(indent + 1)
        print(image.filename + " - " + image.caption)


def print_node(node, indent):
    do_indent(indent)
    stdout.write("'" + node.name + "' (" + node.type + ") - " + node.privacy)
    if node.type == "Album":
        print_album(node, indent)
    print()
    children = node.get_children(connection)
    for child in children:
        print_node(child, indent + 1)


def get_authorized_connection(api_key, api_secret, token, secret):

    if not api_key or not api_secret:
        raise Exception('API key and secret are required. see test_setup.py')

    connection = Connection(api_key, api_secret, user_agent="Test user agent/2.4")

    if not token or not secret:
        auth_url = connection.get_auth_url(access="Full", permissions="Modify")

        print("Visit the following URL and retrieve a verification code:%s%s" % (linesep, auth_url))

        stdout.write('Enter the six-digit code: ')
        stdout.flush()
        verifier = stdin.readline().strip()

        at, ats = connection.get_access_token(verifier)

        print("Token: " + at)
        print("Secret: " + ats)

        token = at
        secret = ats

    connection.authorise_connection(token, secret)

    return connection


def get_root_node(conn):
    user = User.get_authorized_user(conn)
    print("User: " + user.nickname + " (" + user.name + ")")

    return Node.get_node(conn, user.node)


def get_image_uris(images):
    image_uris = []
    for image in images:
        image_uris.append(image.uri)

    return image_uris


def get_all_image_uris(conn, node):
    image_uris = []
    for child_node in node.get_children(conn):
        if child_node.type == "Album":
            album = Album.get_album(conn, child_node.album_uri)
            images = album.get_images(conn)
            image_uris = image_uris + get_image_uris(images)

    return image_uris


def get_some_image_uris(conn, node):
    image_uris = []
    for child_node in node.get_children(conn):
        if child_node.type == "Album":
            album = Album.get_album(conn, child_node.album_uri)
            images = album.get_images(conn)
            image_uris = image_uris + get_image_uris(images)
            return image_uris


def main():
    connection = get_authorized_connection(api_key, api_secret, token, secret)
    node = get_root_node(connection)

    image_uris = get_some_image_uris(connection, node)
    print(image_uris)

    a = Image.get_image(connection, image_uris[0])
    d = {"Keywords" : "eins"}
    b = a.change_image(connection, d)
    print(b)


if __name__ == "__main__":
    main()