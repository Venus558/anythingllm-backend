from fastapi import APIRouter
from dotenv import load_dotenv
import os
import requests
from .auth import get_token

load_dotenv()

ANYTHING_URL = os.getenv('ANYTHINGLLM_URL')

router = APIRouter(prefix='/users', tags=['users'])

@router.post('/assign_ws')
def assign_user(data:dict):
    ws_id = data.get('ws_id')
    user_id = data.get('user_id')

    if not ws_id or not user_id:
        return {'error': 'ws_id and user_id are required'}
    
    token = get_token()

    url = f'{ANYTHING_URL}/admin/workspaces/{ws_id}/update-users'

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    payload = {
        'userIds': [user_id]
    }

    resp = requests.post(url, json=payload, headers=headers)

    if resp.status_code != 200:
        return {'status': 'error', 'detail': resp.text}
    
    return {
        'status': 'ok',
        'ws_id': ws_id,
        'user_id': user_id,
        'server_response': resp.json()
    }