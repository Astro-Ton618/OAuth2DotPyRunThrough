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


def generate_permission_url(client_id: str) -> str:
    params: dict = {}
    params['client_id'] = client_id
    params['redirect_uri'] = REDIRECT_URI
    params['scope'] = 'https://mail.google.com/'
    params['response_type'] = 'code'

    param_fragments: list = []
    for param in sorted(params.items(), key=lambda x: x[0]):
        param_fragments.append('%s=%s' % (
            param[0], urllib.parse.quote(param[1], safe='~-._')))
    formated_url_params: str = '&'.join(param_fragments)

    return '%s?%s' % ('%s/%s' % (GOOGLE_ACCOUNTS_BASE_URL, 'o/oauth2/auth'), formated_url_params)


def generate_token_authorization(client_id: str, client_secret: str, authorization_code: str) -> Tuple[str, str, int]:
    params: dict = {}
    params['client_id'] = client_id
    params['client_secret'] = client_secret
    params['code'] = authorization_code
    params['redirect_uri'] = REDIRECT_URI
    params['grant_type'] = 'authorization_code'
    request_url: str = '%s/%s' % (GOOGLE_ACCOUNTS_BASE_URL, 'o/oauth2/token')

    response: dict = urlopen(request_url, urllib.parse.urlencode(
        params).encode('UTF-8')).read().decode("utf-8")
    json_response: dict = json.loads(response)
    return json_response['refresh_token'], json_response['access_token'], json_response['expires_in']


def generate_o_auth_2_string(email: str, access_token: str, base64_encode: bool = True) -> str:
    auth_string: str = 'user=%s\1auth=Bearer %s\1\1' % (email, access_token)
    if base64_encode:
        auth_string: str = base64.b64encode(
            bytes(auth_string, encoding='UTF-8'))
    return auth_string


def imap_authentication(email: str, access_token: str) -> None:
    o_auth2_argument: str = generate_o_auth_2_string(
        email, access_token, False)
    imap_conn: imaplib.IMAP4_SSL = imaplib.IMAP4_SSL('imap.gmail.com')
    imap_conn.debug = 4
    imap_conn.authenticate('XOAUTH2', lambda x: o_auth2_argument)
    imap_conn.select('INBOX')


def smtp_authentication(email: str, access_token: str) -> None:
    o_auth2_argument: str = generate_o_auth_2_string(
        email, access_token, False)
    smtp_conn: smtplib.SMTP = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_conn.set_debuglevel(True)
    smtp_conn.ehlo('test')
    smtp_conn.starttls()
    smtp_conn.docmd('AUTH', 'XOAUTH2 ' + ''.join(chr(x)
                    for x in bytearray(base64.b64encode(bytes(o_auth2_argument, encoding='UTF-8')))))


def refresh_token_func(client_id: str, client_secret: str, refresh_token: str) -> Tuple[str, int]:
    params: dict = {}
    params['client_id'] = client_id
    params['client_secret'] = client_secret
    params['refresh_token'] = refresh_token
    params['grant_type'] = 'refresh_token'
    request_url = '%s/%s' % (GOOGLE_ACCOUNTS_BASE_URL, 'o/oauth2/token')

    response: dict = urlopen(request_url, urllib.parse.urlencode(
        params).encode('UTF-8')).read().decode("utf-8")
    json_response: dict = json.loads(response)
    return json_response['access_token'], json_response['expires_in']
