from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.auth import get_token
import requests, os
import re

router = APIRouter(prefix='/workspace', tags=['workspace'])

ANYTHING_URL = os.getenv("ANYTHINGLLM_URL")
HELPER_URL = os.getenv('HELPER_URL')

def workspace_name_from_email(email:str):
    email = email.lower()
    safe = re.sub(r'[^A-Za-z0-9]+', '_', email)
    return f'{safe}_workspace'

@router.post('/create')
def create_workspace(data:dict):
    # create a new workspace on the server

    email = data.get('email')

    if not email:
        return {'error': 'email is required'}

    workspace_name = workspace_name_from_email(email)

    token=get_token()

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'

    }

    url = f'{ANYTHING_URL}/workspace/new'
    
    resp = requests.post(url, json={'name':workspace_name}, headers=headers)

    if resp.status_code != 200:
        return {
            'status': 'error',
            'detail': resp.text

        }
    
    
    ws_id = resp.json()['workspace']['slug']

    prompt_data = {
        'workspace_id': ws_id,
        'prompt': 'Respond Like Beavis and Butthead. You can use emojis and respond quickly!'
    }

    set_prompt(prompt_data)

    return {
        'status': 'ok',
        'workspace': workspace_name,
        'email': email,
        'server_response': resp.json()
    }

@router.post('/prompt/set')
def set_prompt(data:dict):
    workspace_id = data.get('workspace_id')
    prompt = data.get('prompt')

    if not workspace_id or not prompt:
        return {'error': 'workspace_id and prompt are required'}
    
    token = get_token()

    url = f'{ANYTHING_URL}/workspace/{workspace_id}/update'

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    payload = {
        "chatProvider": "default",
        "chatMode": "chat",
        "openAiPrompt": prompt,
        "openAiHistory": 20,
        "openAiTemp": 0.7,
        'queryRefusalResponse': 'N/A'
        }

    resp = requests.post(url, json=payload, headers=headers)

    if resp.status_code != 200:
        return {'status': 'error', 'detail': resp.text}
    
    return {'status': 'ok', 'workspace_id': workspace_id}
