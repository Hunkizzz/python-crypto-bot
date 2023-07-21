import requests
from flask import Flask, request

import config
from tokens import tokens
app = Flask(__name__)


@app.route("/auth")
async def callback_handler():
    code = request.args.get("code")
    state = request.args.get("state")
    session_state = request.args.get("session_state")

    # Exchange the authorization code for an access token
    token_endpoint = f"{config.keycloak_url}/realms/{config.realm}/protocol/openid-connect/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": config.client_id,
        "client_secret": config.client_secret,
        "code": code,
        "redirect_uri": f"{config.app_url}/auth"
    }
    response = requests.post(token_endpoint, data=payload)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        tokens[state] = access_token
        return f"You have been successfully authorized!\n Please close this tab and return to the bot!\n Have a nice day"
    else:
        print(f"Token retrieval failed with status code {response.status_code}")
        return None


def flask_app():
    app.run(host="localhost", port=8005)
