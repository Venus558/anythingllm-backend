from fastapi import APIRouter
from dotenv import load_dotenv
import os
import requests
from .auth import get_token
from .workspace import create_workspace

load_dotenv()

ANYTHING_URL = os.getenv('ANYTHINGLLM_URL')

router = APIRouter(prefix='/users', tags=['users'])

@router.post('/create')
def create_user(data:dict):
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return {'error': 'email and password are required'}
    
    token = get_token()

    url = f'{ANYTHING_URL}/admin/users/new'

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    payload = {
        'bio': '.',
        'dailyMessageLimit': 10,
        'password': password,
        'role': 'default',
        'username': email
    }

    resp = requests.post(url, json=payload, headers=headers)

    if resp.status_code != 200:
        return {'status': 'error', 'detail': resp.text}
    


    user_id =  resp.json()['user']['id']

    
    workspace_payload = {'email' : email, 'user_id':user_id}

    create_workspace(workspace_payload)
    
    return {
        'status': 'ok',
        'email': email,
        'server_response': resp.json()
    }

