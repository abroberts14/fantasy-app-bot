from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Dict, Optional

import requests
import os 

router = APIRouter()
yacht_endpoint = "http://167.99.4.120:8000/api"
default_app_name = 'draftwarroom-chatbot-'

def handle_request(method: str, url: str, headers: Dict = None, cookies: Dict = None, json: Dict = None):
    response = requests.request(method, url, headers=headers, cookies=cookies, json=json)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to {method} {url}"
        )

    return response

def get_cookies(tokens: Dict):
    return {"access_token_cookie": tokens['access_token'], "csrf_access_token": tokens['csrf_token'], "csrf_refresh_token": tokens['csrf_refresh_token']}

def get_headers(tokens: Dict):
    return {"X-CSRF-TOKEN": tokens["csrf_token"]}

async def get_tokens():
    url = yacht_endpoint + "/auth/login"
    payload = {"username": os.getenv("yacht_username"), "password": os.getenv("yacht_password")}
    headers = {"Content-Type": "application/json"}

    response = handle_request("POST", url, headers=headers, json=payload)

    data = response.json()

    if "access_token" not in data:
        raise HTTPException(
            status_code=500,
            detail="No access token in the response"
        )

    csrf_token = response.cookies.get('csrf_access_token')
    csrf_refresh_token = response.cookies.get('csrf_refresh_token')

    if not csrf_token or not csrf_refresh_token:
        raise HTTPException(
            status_code=500,
            detail="No CSRF token or CSRF refresh token in the response"
        )

    return {"access_token": data["access_token"], "csrf_token": csrf_token, "csrf_refresh_token": csrf_refresh_token}


def filter_app_to_schema(app: Dict):
    return {
        "status": app['State']['Status'] if 'State' in app and 'Status' in app['State'] else None,
        "running": app['State']['Running'] if 'State' in app and 'Running' in app['State'] else None,
        "pid": app['State']['Pid'] if 'State' in app and 'Pid' in app['State'] else None,
        "name": app.get('name')
    }


@router.get("/yacht/templates/{template_id}")
async def get_template(template_id: int, tokens: str = Depends(get_tokens)):
    url = yacht_endpoint + f"/templates/{template_id}"
    cookies = get_cookies(tokens)

    response = handle_request("GET", url, cookies=cookies)

    return response.json()['items'][0]

@router.post("/yacht/apps/deploy")
async def deploy_app(
    new_app: Dict = Body(...),
    tokens: str = Depends(get_tokens),
):
    bot_name = new_app["name"]
    template_id = "2"
    bot_id = new_app["groupme_bot_id"]
    bot_type = "GroupMe"
    league_id = new_app["league_id"]
    url = yacht_endpoint + f"/templates/{template_id}"

    cookies = get_cookies(tokens)
    headers = get_headers(tokens)
    response = handle_request("GET", url, cookies=cookies, headers=headers)

    app = response.json()["items"][0]
    new_app_name = app["name"] + "-" + bot_name

    url = yacht_endpoint + "/apps"
    response = handle_request("GET", url, cookies=cookies)

    existing_apps = response.json()

    for existing_app in existing_apps:
        if existing_app["name"] == new_app_name:
            raise HTTPException(
                status_code=400,
                detail="An app with the same name already exists!"
            )

    new_payload =  {
        "name": new_app_name,
        "image": app["image"],
        "restart_policy": "unless-stopped",
        "command": app["command"] if app["command"] is not None else [],
        "network": "",
        "network_mode": "host",
        "ports": [],
        "volumes": [],
        "env": [
            {
                "name": "BOT_ID",
                "label": "GroupMe Bot ID",
                "default": bot_id
            },
            {
                "name": "BOT_TYPE",
                "label": "Chat Bot Type",
                "default": bot_type
            },
            {
                "name": "LEAGUE_ID",
                "label": "Yahoo League Id",
                "default": league_id
            }
        ],
        "devices": [],
        "labels": [],
        "sysctls": [],
        "cap_add": [],
        "cpus": None,
        "mem_limit": None
    }
    
    url = yacht_endpoint + "/apps/deploy"

    response = handle_request("POST", url, headers=headers, cookies=cookies, json=new_payload)

    url = yacht_endpoint + f"/apps/{new_app_name}"
    response = handle_request("GET", url, cookies=cookies)

    return response.json()


def create_and_deploy_app(
    new_app: Dict = Body(...),
    tokens: str = Depends(get_tokens),
):
    bot_name = new_app["bot_name"]
    template_id = new_app["template_id"]
    bot_id = new_app["BOT_ID"]
    bot_type = new_app["BOT_TYPE"]
    league_id = new_app["LEAGUE_ID"]
    url = yacht_endpoint + f"/templates/{template_id}"

    cookies = get_cookies(tokens)
    headers = get_headers(tokens)
    response = handle_request("GET", url, cookies=cookies, headers=headers)

    app = response.json()["items"][0]
    new_app_name = app["name"] + "-" + bot_name

    url = yacht_endpoint + "/apps"
    response = handle_request("GET", url, cookies=cookies)

    existing_apps = response.json()

    for existing_app in existing_apps:
        if existing_app["name"] == new_app_name:
            raise HTTPException(
                status_code=400,
                detail="An app with the same name already exists!"
            )

    new_payload =  {
        "name": new_app_name,
        "image": app["image"],
        "restart_policy": "unless-stopped",
        "command": app["command"] if app["command"] is not None else [],
        "network": "",
        "network_mode": "host",
        "ports": [],
        "volumes": [],
        "env": [
            {
                "name": "BOT_ID",
                "label": "GroupMe Bot ID",
                "default": bot_id
            },
            {
                "name": "BOT_TYPE",
                "label": "Chat Bot Type",
                "default": bot_type
            },
            {
                "name": "LEAGUE_ID",
                "label": "Yahoo League Id",
                "default": league_id
            }
        ],
        "devices": [],
        "labels": [],
        "sysctls": [],
        "cap_add": [],
        "cpus": None,
        "mem_limit": None
    }
    
    url = yacht_endpoint + "/apps/deploy"

    response = handle_request("POST", url, headers=headers, cookies=cookies, json=new_payload)

    url = yacht_endpoint + f"/apps/{new_app_name}"
    response = handle_request("GET", url, cookies=cookies)

    return response.json()

@router.get("/yacht/apps/{app_name}")
async def get_app(app_name: str, tokens: str = Depends(get_tokens)):
    url = yacht_endpoint + f"/apps/{default_app_name}{app_name}"
    cookies = get_cookies(tokens)

    response = handle_request("GET", url, cookies=cookies)

    return response.json()

@router.get("/yacht/apps")
async def get_apps(app_name: str, tokens: str = Depends(get_tokens)):
    url = yacht_endpoint + f"/apps"
    cookies = get_cookies(tokens)

    response = handle_request("GET", url, cookies=cookies)

    return response.json()