from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests
import time

# Loads in Admin bot credentials
# Sends Request to Server
# Saves and caches the JWT
# Provide Reusable Function the rest of automation service can use

load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])

ANYTHING_URL = os.getenv("ANYTHINGLLM_URL")
BOT_USERNAME = os.getenv("BOT_USERNAME")
BOT_PASSWORD = os.getenv("BOT_PASSWORD")


_cached_token = None
_token_expires_at = 0


class LoginResponse(BaseModel):
    token: str
    expires_in: int
    username: str

def login_admin_bot():
    # Login and store JWT
    global _cached_token, _token_expires_at

    url = f'{ANYTHING_URL}/request-token'
    
    payload = {
        'username': BOT_USERNAME,
        'password': BOT_PASSWORD
    }

    print(f'[AUTH] Logging in bot: {BOT_USERNAME}')

    resp = requests.post(url, json=payload)

    if resp.status_code != 200:
        print('[AUTH ERROR] Could not login:', resp.text)
        raise Exception('Admin bot login failed')
    
    data = resp.json()


    token = data.get('token')
    user = data.get('user', {})


    # token valid for 30. Adjust as needed (maybe change this bc why would admin want to be logged in for 30 days?)

    expires_in = 30 * 24 * 60 * 60
    _cached_token = token
    _token_expires_at = time.time() + expires_in

    print('[AUTH] Bot authenticated succesfully.')
    return LoginResponse(
        token=token,
        expires_in=expires_in,
        username=user.get('username', BOT_USERNAME)
    )


def get_token():
    # return cached JWT or re-login if expired
    global _cached_token, _token_expires_at

    if not _cached_token or time.time() > _token_expires_at:
        print('[AUTH] Token missing or expired. Re-authenticating')
        login_admin_bot()

    return _cached_token



@router.get("/bot-status")
def test_login():
    # test endpoint to verify login works
    token=get_token()
    return {'authenticated':True, 'bot': BOT_USERNAME, 'status': 'ok'}
