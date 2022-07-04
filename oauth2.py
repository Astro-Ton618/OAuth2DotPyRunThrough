# https://github.com/google/gmail-oauth2-tools/wiki/OAuth2DotPyRunThrough
import base64
import imaplib
import json
import smtplib
import urllib.parse
from typing import Tuple
from urllib.request import urlopen


GOOGLE_ACCOUNTS_BASE_URL: str = 'https://accounts.google.com'
REDIRECT_URI: str = 'urn:ietf:wg:oauth:2.0:oob'


# **************************************************
def __accounts_url(command: str) -> str:
    return '%s/%s' % (GOOGLE_ACCOUNTS_BASE_URL, command)


def __url_escape(text: str) -> str:
    return urllib.parse.quote(text, safe='~-._')


def __format_url_params(params: dict) -> str:
    param_fragments = []
    for param in sorted(params.items(), key=lambda x: x[0]):
        param_fragments.append('%s=%s' % (param[0], __url_escape(param[1])))
    return '&'.join(param_fragments)


def __generate_permission_url(client_id: str) -> str:
    params = {}
    params['client_id'] = client_id
    params['redirect_uri'] = REDIRECT_URI
    params['scope'] = 'https://mail.google.com/'
    params['response_type'] = 'code'
    return '%s?%s' % (__accounts_url('o/oauth2/auth'),
                      __format_url_params(params))
# **************************************************


# **************************************************
def __accounts_url(command: str) -> str:
    return '%s/%s' % (GOOGLE_ACCOUNTS_BASE_URL, command)


def __authorize_tokens(client_id: str, client_secret: str, authorization_code: str) -> dict:
    params = {}
    params['client_id'] = client_id
    params['client_secret'] = client_secret
    params['code'] = authorization_code
    params['redirect_uri'] = REDIRECT_URI
    params['grant_type'] = 'authorization_code'
    request_url = __accounts_url('o/oauth2/token')

    response = urlopen(request_url, urllib.parse.urlencode(
        params).encode('UTF-8')).read().decode("utf-8")
    return json.loads(response)
# **************************************************


# **************************************************
def __generate_o_auth_2_string(email: str, access_token: str, base64_encode: bool = True) -> str:
    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (email, access_token)
    if base64_encode:
        auth_string = base64.b64encode(bytes(auth_string, encoding='UTF-8'))
    return auth_string
# **************************************************


# **************************************************
def __test_imap_authentication(user: str, auth_string: str):
    # print
    imap_conn = imaplib.IMAP4_SSL('imap.gmail.com')
    imap_conn.debug = 4
    imap_conn.authenticate('XOAUTH2', lambda x: auth_string)
    imap_conn.select('INBOX')
# **************************************************


# **************************************************
def __test_smtp_authentication(user: str, auth_string: str):
    print
    smtp_conn = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_conn.set_debuglevel(True)
    smtp_conn.ehlo('test')
    smtp_conn.starttls()
    smtp_conn.docmd('AUTH', 'XOAUTH2 ' + base64.b64encode(auth_string))
# **************************************************


# **************************************************
def __accounts_url(command):
    return '%s/%s' % (GOOGLE_ACCOUNTS_BASE_URL, command)


def __refresh_token(client_id: str, client_secret: str, refresh_token: str) -> dict:
    params = {}
    params['client_id'] = client_id
    params['client_secret'] = client_secret
    params['refresh_token'] = refresh_token
    params['grant_type'] = 'refresh_token'
    request_url = __accounts_url('o/oauth2/token')

    response = urllib.urlopen(request_url, urllib.urlencode(
        params).encode('UTF-8')).read().decode("utf-8")
    return json.loads(response)
# **************************************************


def generate_permission_url(client_id: str) -> str:
    return __generate_permission_url(client_id)


def authorizing_token(client_id: str, client_secret: str, token: str) -> Tuple[str, str, int]:
    json: dict = __authorize_tokens(client_id, client_secret, token)
    return json['refresh_token'], json['access_token'], json['expires_in']


def creating_authentication_string(access_token: str, email: str) -> str:
    return __generate_o_auth_2_string(email, access_token)


def imap_authentication(email: str, access_token: str):
    __test_imap_authentication(
        email, __generate_o_auth_2_string(email, access_token, False))


def smtp_authentication(email: str, access_token: str):
    __test_smtp_authentication(
        email, __generate_o_auth_2_string(email, access_token, False))


def refresh_token_func(client_id: str, client_secret: str, refresh_token: str) -> Tuple[str, int]:
    json: dict = __refresh_token(client_id, client_secret,  refresh_token)
    return json['access_token'], json['expires_in']
