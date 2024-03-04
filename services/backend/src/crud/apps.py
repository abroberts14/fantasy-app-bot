from fastapi import  HTTPException, Depends, Body
from src.schemas.bots import BotInSchema    
from src.database.models import Apps, Bots 
from src.schemas.apps import AppOutSchema
from typing import List, Dict, Optional
from datetime import datetime
from dateutil.parser import isoparse
from src.routes import oauth
from src.crud import bots
import requests
import os 

yacht_endpoint = "http://167.99.4.120:8000/api"
default_app_name = 'draftwarroom-chatbot-'

backend_url = os.getenv('BACKEND_URL', 'https://api.draftwarroom.com')

def handle_request(method: str, url: str, headers: Dict = None, cookies: Dict = None, json: Dict = None):
    response = requests.request(method, url, headers=headers, cookies=cookies, json=json)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to {method} {url}"
        )

    return response

def get_cookies(tokens):
    return {
        "access_token_cookie": tokens.get('access_token'),
        "csrf_access_token": tokens.get('csrf_token'),
        "csrf_refresh_token": tokens.get('csrf_refresh_token')
    }

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

def filter_app_to_full_schema(app: Dict):
    print('dict update')
    return {
        "name": app.get('name'),
        "status": app['State']['Status'] if 'State' in app and 'Status' in app['State'] else None,
        "running": app['State']['Running'] if 'State' in app and 'Running' in app['State'] else None,
        "paused": app['State']['Paused'] if 'State' in app and 'Paused' in app['State'] else None,
        "restarting": app['State']['Restarting'] if 'State' in app and 'Restarting' in app['State'] else None,
        "oom_killed": app['State']['OOMKilled'] if 'State' in app and 'OOMKilled' in app['State'] else None,
        "dead": app['State']['Dead'] if 'State' in app and 'Dead' in app['State'] else None,
        "pid": app['State']['Pid'] if 'State' in app and 'Pid' in app['State'] else None,
        "exit_code": app['State']['ExitCode'] if 'State' in app and 'ExitCode' in app['State'] else None,
        "error": app['State']['Error'] if 'State' in app and 'Error' in app['State'] else None,
        "started_at": app['State']['StartedAt'] if 'State' in app and 'StartedAt' in app['State'] else None,
        "finished_at": app['State']['FinishedAt'] if 'State' in app and 'FinishedAt' in app['State'] else None,
    }

async def get_app(app_id: int):
    db_app = await AppOutSchema.from_queryset_single(Apps.get(id=app_id)) 
    await update_one_app(db_app.name)
    return await AppOutSchema.from_queryset_single(Apps.get(id=app_id))


async def get_apps(user_id: int = None):
    await update_all_apps()
    if user_id:
        # Fetch bots for a specific user
        return await AppOutSchema.from_queryset(Apps.filter(user_id=user_id))
    else:
        # Fetch all bots (for admins in the future)
        return await AppOutSchema.from_queryset(Apps.all())

async def update_one_app(app_name: str):
    # Fetch all the applications
    app_info = await _get_app(app_name)
    print(app_info)
    filtered_app_info = filter_app_to_full_schema(app_info)
    # Fetch the corresponding record from the database if it exists
    app_record = await Apps.get_or_none(name=filtered_app_info['name'])
    # If the record exists, update it
    if app_record is not None:
        # Update the record with the new info
        # update database with updated info about the apps/containers
        app_record.status = filtered_app_info['status'] if filtered_app_info['status'] is not None else app_record.status
        app_record.running = filtered_app_info['running'] if filtered_app_info['running'] is not None else app_record.running
        app_record.paused = filtered_app_info['paused'] if filtered_app_info['paused'] is not None else app_record.paused
        app_record.restarting = filtered_app_info['restarting'] if filtered_app_info['restarting'] is not None else app_record.restarting
        app_record.oom_killed = filtered_app_info['oom_killed'] if filtered_app_info['oom_killed'] is not None else app_record.oom_killed
        app_record.dead = filtered_app_info['dead'] if filtered_app_info['dead'] is not None else app_record.dead
        app_record.pid = filtered_app_info['pid'] if filtered_app_info['pid'] is not None else app_record.pid
        app_record.exit_code = filtered_app_info['exit_code'] if filtered_app_info['exit_code'] is not None else app_record.exit_code
        app_record.error = filtered_app_info['error'] if filtered_app_info['error'] is not None else app_record.error
        app_record.started_at = isoparse(filtered_app_info['started_at']) if filtered_app_info['started_at'] is not None else app_record.started_at
        app_record.finished_at = isoparse(filtered_app_info['finished_at']) if filtered_app_info['finished_at'] is not None else app_record.finished_at
        # Save the updated record to the database
        await app_record.save()

        # Add the updated record to the list
        return await AppOutSchema.from_tortoise_orm(app_record)


async def update_all_apps():
    # Fetch all the applications
    apps = await _get_apps()

    # Initialize a list to hold the updated records
    updated_apps = []

    # Loop through the applications
    for app_info in apps:
        filtered_app_info = filter_app_to_full_schema(app_info)
        # Fetch the corresponding record from the database if it exists
        app_record = await Apps.get_or_none(name=filtered_app_info['name'])
        print('made')
        # If the record exists, update it
        if app_record is not None:
            # Update the record with the new info
            # update database with updated info about the apps/containers
            app_record.status = filtered_app_info['status'] if filtered_app_info['status'] is not None else app_record.status
            app_record.running = filtered_app_info['running'] if filtered_app_info['running'] is not None else app_record.running
            app_record.paused = filtered_app_info['paused'] if filtered_app_info['paused'] is not None else app_record.paused
            app_record.restarting = filtered_app_info['restarting'] if filtered_app_info['restarting'] is not None else app_record.restarting
            app_record.oom_killed = filtered_app_info['oom_killed'] if filtered_app_info['oom_killed'] is not None else app_record.oom_killed
            app_record.dead = filtered_app_info['dead'] if filtered_app_info['dead'] is not None else app_record.dead
            app_record.pid = filtered_app_info['pid'] if filtered_app_info['pid'] is not None else app_record.pid
            app_record.exit_code = filtered_app_info['exit_code'] if filtered_app_info['exit_code'] is not None else app_record.exit_code
            app_record.error = filtered_app_info['error'] if filtered_app_info['error'] is not None else app_record.error
            app_record.started_at = isoparse(filtered_app_info['started_at']) if filtered_app_info['started_at'] is not None else app_record.started_at
            app_record.finished_at = isoparse(filtered_app_info['finished_at']) if filtered_app_info['finished_at'] is not None else app_record.finished_at
            # Save the updated record to the database
            await app_record.save()

            # Add the updated record to the list
            updated_apps.append(await AppOutSchema.from_tortoise_orm(app_record))

    # Return the list of updated records
    return updated_apps

async def create_and_deploy_app(
    bot_id: str,
    bot: BotInSchema = Body(...),
    edit: bool = False,  # New optional parameter
):
    bot_name = bot.name
    template_id = "2"
    bot_groupme_id = bot.groupme_bot_id
    bot_type = "GroupMe"
    league_id = bot.league_id
    
    for feature in bot.features:
        print(f"Feature: {feature.global_feature.name}, Enabled: {feature.enabled}")

    feature_env_vars = ",".join(
        feature.global_feature.name.upper() for feature in bot.features if feature.enabled
    )

    print(bot_name, bot_groupme_id, bot_type, league_id)
    url = yacht_endpoint + f"/templates/{template_id}"
    print(url)
    tokens = await get_tokens()
    cookies = get_cookies(tokens)
    headers = get_headers(tokens)
    response = handle_request("GET", url, cookies=cookies, headers=headers)
    rsp = response.json()
    print(rsp)
    app = rsp["items"][0]
    new_app_name = app["name"] + "-" + bot_name

    url = yacht_endpoint + "/apps"
    response = handle_request("GET", url, cookies=cookies)

    existing_apps = response.json()
    app_id = None
    for existing_app in existing_apps:
        if existing_app["name"] == new_app_name:
            if edit:
                app_id = existing_app["Id"]
                break
            raise HTTPException(
                status_code=400,
                detail="An app with the same name already exists!"
            )

    new_payload = {
        "name": new_app_name,
        "image": app["image"],
        "restart_policy": "none",
        "command": app["command"] if app["command"] is not None else [],
        "network": "",
        "network_mode": "host",
        "ports": [],
        "volumes": [],
        "env": [
            {"name": "BOT_ID", "label": "GroupMe Bot ID", "default": bot_groupme_id},
            {"name": "BOT_TYPE", "label": "Chat Bot Type", "default": bot_type},
            {"name": "LEAGUE_ID", "label": "Yahoo League Id", "default": league_id},
            {"name": "FEATURE_ENV_VARS", "label": "Feature Environment Variables", "default": feature_env_vars},
            {"name": "BACKEND_URL", "label": "Backend API", "default": backend_url},

        ],
        "devices": [],
        "labels": [],
        "sysctls": [],
        "cap_add": [],
        "cpus": None,
        "mem_limit": None,
    }
    is_private = bot.private
    if is_private:
        user_id = await bots.get_bot_user_id(bot_id)  # Replace with the actual token ID
        print(user_id)
        token_data = await oauth.get_oauth_token_by_id(user_id)
        new_payload["env"].extend([
            {"name": "access_token", "label": "Access Token", "default": token_data["access_token"]},
            {"name": "refresh_token", "label": "Refresh Token", "default": token_data["refresh_token"]},
            {"name": "token_time", "label": "Token Time", "default": token_data["expires_in"]}
            # {"name": "consumer_key", "label": "Consumer Key", "default": os.getenv('YAHOO_CONSUMER_KEY')},
            # {"name": "consumer_secret", "label": "Consumer Secret", "default": os.getenv('YAHOO_CONSUMER_SECRET')}
        ])
    if edit:
        new_payload["edit"] = True
        new_payload["id"] = app_id
    print(new_payload)

    # Only create a new app if not in edit mode
    url = yacht_endpoint + "/apps/deploy"
    response = handle_request("POST", url, headers=headers, cookies=cookies, json=new_payload)

    url = yacht_endpoint + f"/apps/{new_app_name}"
    response = handle_request("GET", url, cookies=cookies)
    app_filtered = filter_app_to_schema(response.json())


    if edit:
        # Update the existing Apps record
        app_obj = await Apps.get(name=new_app_name)
        for key, value in app_filtered.items():
            setattr(app_obj, key, value)
        await app_obj.save()
    else:
        # Create a new Apps record
        app_obj = await Apps.create(**app_filtered)    
    bot_obj = await Bots.get(id=bot_id)
    bot_obj.app = app_obj
    await bot_obj.save()

    return await AppOutSchema.from_tortoise_orm(app_obj)

async def perform_app_action(app_name: str, action: str):
    url = yacht_endpoint + f"/apps/actions/{app_name}/{action}"
    tokens = await get_tokens()
    cookies = get_cookies(tokens)
    print('Sending request to perform action' + action + ' on app ' + app_name)
    response = handle_request("GET", url, cookies=cookies)
    print('Seent request to perform action complete')
    if response.status_code != 200:
        raise Exception(f"Request to {url} failed with status code {response.status_code}. Response: {response.text}")
    print('Request to perform action complete')
    return response.json()

async def _delete_stop_and_kill_app(app_name: str):
    actions = ['stop', 'remove']

    for action in actions:
        print(f"Performing action {action} on app {app_name}")
        response = await perform_app_action(app_name, action)
        print(f"Response for action {action}: {response}")

    return "Actions performed successfully"

async def delete_entire_app(app_name: str):
    # Call perform_multiple_actions
    await _delete_stop_and_kill_app(app_name)
    print('Deleted app' + app_name)
    # Delete the app from the database
    deleted_app_count = await Apps.filter(name=app_name).delete()
    print('Fetched deleted app count' + str(deleted_app_count))
    if not deleted_app_count:
        raise HTTPException(status_code=500, detail=f"Failed to delete associated App {app_name}")

    return "App deleted successfully"

async def _get_app(app_name: str):

    url = yacht_endpoint + f"/apps/{app_name}"
    tokens = await get_tokens()
    cookies = get_cookies(tokens)
    response = handle_request("GET", url, cookies=cookies)
    app_filtered = filter_app_to_schema(response.json())

    return response.json()

async def _get_apps():
    url = yacht_endpoint + f"/apps"
    tokens = await get_tokens()
    cookies = get_cookies(tokens)

    response = handle_request("GET", url, cookies=cookies)
    apps = response.json()
    return response.json()

