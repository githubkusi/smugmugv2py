#!/usr/bin/python

from rauth import OAuth1Service, OAuth1Session
from urlparse import urlsplit, urlunsplit, parse_qsl
from urllib import urlencode
from json import loads
import requests
import smugmugv2py 
from pprint import pprint
from os import path

class Connection:
  BASE_URL = '/api/v2'
  UPLOAD_URL = 'https://upload.smugmug.com/'

  __OAUTH_ORIGIN = 'https://secure.smugmug.com'
  __REQUEST_TOKEN_URL = __OAUTH_ORIGIN + '/services/oauth/1.0a/getRequestToken'
  __ACCESS_TOKEN_URL = __OAUTH_ORIGIN + '/services/oauth/1.0a/getAccessToken'
  __AUTHORIZE_URL = __OAUTH_ORIGIN + '/services/oauth/1.0a/authorize'

  __API_ORIGIN = 'https://api.smugmug.com'
  
  __SERVICE = None
  __SESSION = requests.Session()

  def __init__(self, api_key, api_secret):
    if self.__SERVICE is None:
      self.__SERVICE = OAuth1Service(
        name='smugmug-oauth-web-demo',
        consumer_key=api_key,
        consumer_secret=api_secret,
        request_token_url=self.__REQUEST_TOKEN_URL,
        access_token_url=self.__ACCESS_TOKEN_URL,
        authorize_url=self.__AUTHORIZE_URL,
        base_url=self.BASE_URL)

  def add_auth_params(self, auth_url, access=None, permissions=None):
    if access is None and permissions is None:
      return auth_url
    parts = urlsplit(auth_url)
    query = parse_qsl(parts.query, True)
    if access is not None:
      query.append(('Access', access))
    if permissions is not None:
      query.append(('Permissions', permissions))
    return urlunsplit((
      parts.scheme,
      parts.netloc,
      parts.path,
      urlencode(query, True),
      parts.fragment))

  def get_auth_url(self, access=None, permissions=None):
    self.__rt, self.__rts = self.__SERVICE.get_request_token(params={'oauth_callback': 'oob'})

    auth_url = self.add_auth_params(
          self.__SERVICE.get_authorize_url(self.__rt), access=access, permissions=permissions)

    return auth_url

  def get_access_token(self, verifier):
    at, ats = self.__SERVICE.get_access_token(self.__rt, self.__rts, params={'oauth_verifier': verifier})

    return (at, ats)

  def authorise_connection(self, token, token_secret):
    self.__SESSION=OAuth1Session(
            self.__SERVICE.consumer_key,
            self.__SERVICE.consumer_secret,
            access_token=token,
            access_token_secret=token_secret)

  def test_connection(self):
    return self.make_request("!authuser")

  def get(self, uri):
    response=loads(self.__SESSION.get(
          self.__API_ORIGIN + uri,
          headers={'Accept': 'application/json'},
          params={'_verbosity': '1'},
          header_auth=True
        ).text)

    if "Response" in response:
      return response["Response"]
    else:
      raise smugmugv2py.SmugMugv2Exception(response["Message"])

  def post(self, uri, headers=None, data=None, params=None):
      return self.raw_post(self.__API_ORIGIN + uri, headers, data, params)
  
  def raw_post(self, uri, headers=None, data=None):
      addHeaders = {'X-Smug-ResponseType': 'JSON', 'X-Smug-Version': 'v2'}
      fullHeaders= headers.copy()
      fullHeaders.update(addHeaders)
      pprint(fullHeaders)
      response=loads(self.__SESSION.post(
        uri,
        headers=fullHeaders,
        data=data,
        header_auth=True).content)

      return response

  def upload_image(self, filename, album_uri, caption=None, title=None, keywords=None):
    headers = {
      'Content-Type': 'none',
      'X-Smug-AlbumUri': album_uri, 
      'X-Smug-FileName': filename, 
      'Content-Length': path.getsize(filename),
    }
    
    if caption:
      headers['X-Smug-Caption']=caption

    if title:
      headers['X-Smug-Title']=title

    if keywords:
      headers['X-Smug-Keywords']=keywords
      
    with open("focuszetec.jpeg", "rb") as f:
      data = f.read()
      return self.raw_post(self.UPLOAD_URL, data=data, headers=headers)
