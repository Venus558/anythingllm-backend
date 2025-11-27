from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.auth import get_token
import requests, os
import re
from .assign_ws import assign_user

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

    email = email.lower()

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
    
    
    ws_slug = resp.json()['workspace']['slug']
    ws_id = resp.json()['workspace']['id']
    user_id = data.get('user_id')

    prompt_data = {
        'workspace_slug': ws_slug,
        'prompt': '''You are Beavis and Butthead. Speak in their style, tone, and humor. 
Use short, chaotic, dumb-guy energy responses. Emojis allowed.

GLOBAL RULES:
- You have access to persistent user memory injected separately.
- NEVER reveal, quote, list, or mention the memory unless the user explicitly asks.
- NEVER assume the user wants memory referenced. Only use it subtly when it's directly relevant.
'''
    }

    assign_data = {
        'user_id' : user_id,
        'ws_id' : ws_id
    }

    set_prompt(prompt_data)

    assign_user(assign_data)

    

    return {
        'status': 'ok',
        'workspace': workspace_name,
        'email': email,
        'server_response': resp.json()
    }

@router.post('/prompt/set')
def set_prompt(data:dict):
    workspace_slug = data.get('workspace_slug')
    prompt = data.get('prompt')

    if not workspace_slug or not prompt:
        return {'error': 'workspace_slug and prompt are required'}
    
    token = get_token()

    url = f'{ANYTHING_URL}/workspace/{workspace_slug}/update'

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
    
    return {'status': 'ok', 'workspace_slug': workspace_slug}
