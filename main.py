# https://developers.google.com/gmail/imap
from fastapi import FastAPI

from oauth2 import (generate_permission_url,
                    generate_token_authorization, generate_o_auth_2_string, imap_authentication, smtp_authentication, refresh_token_func)

# Add your client id and client secret
CLIENT_ID: str = ''
CLIENT_SECRET: str = ''

app: FastAPI = FastAPI()


# http://localhost:8080/get_url
@app.get('/get_url')
async def get_url() -> dict:
    url: str = generate_permission_url(CLIENT_ID)
    return {'url': url}


# http://localhost:8080/authorize_token?token=[]
@app.get('/authorize_token')
async def authorize_token(token: str) -> dict:
    refresh_token, access_token, access_token_expiration_seconds = generate_token_authorization(
        CLIENT_ID, CLIENT_SECRET, token)

    return {
        'refresh_token': refresh_token,
        'access_token': access_token,
        'access_token_expiration_seconds': access_token_expiration_seconds,
    }


# http://localhost:8080/get_auth_str?access_token=[]&email=[]
@app.get('/get_auth_str')
async def get_auth_str(access_token: str, email: str) -> dict:
    o_auth2_argument: str = generate_o_auth_2_string(
        access_token, email)
    return {'o_auth2_argument': o_auth2_argument}


# http://localhost:8080/imap?access_token=[]&email=[]
@app.get('/imap')
async def imap(access_token: str, email: str) -> dict:
    imap_authentication(email, access_token)
    return{'': ''}


# http://localhost:8080/smtp?access_token=[]&email=[]
@app.get('/smtp')
async def smtp(access_token: str, email: str) -> dict:
    smtp_authentication(email, access_token)
    return{'': ''}


# http://localhost:8080/refresh_token?refresh_token_req=[]
@app.get('/refresh_token')
async def refresh_token(refresh_token_req: str) -> dict:
    access_token, access_token_expiration_seconds = refresh_token_func(
        CLIENT_ID, CLIENT_SECRET, refresh_token_req)
    return {
        'access_token': access_token,
        'access_token_expiration_seconds': access_token_expiration_seconds,
    }
