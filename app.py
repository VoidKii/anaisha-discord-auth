import os
from flask import Flask, redirect, request, jsonify
import requests

app = Flask(__name__)

CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")

DISCORD_API = "https://discord.com/api/v10"


@app.route("/")
def home():
    return "Anaisha Discord Auth is online! ♡"


@app.route("/login")
def login():
    discord_url = (
        "https://discord.com/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={requests.utils.quote(REDIRECT_URI, safe='')}"
        "&scope=identify"
    )

    return redirect(discord_url)


@app.route("/callback")
def callback():
    code = request.args.get("code")

    if not code:
        return "No authorization code received.", 400

    token_response = requests.post(
        f"{DISCORD_API}/oauth2/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
    )

    if token_response.status_code != 200:
        return "Discord authorization failed.", 400

    token_data = token_response.json()

    user_response = requests.get(
        f"{DISCORD_API}/users/@me",
        headers={
            "Authorization": f"Bearer {token_data['access_token']}"
        },
    )

    if user_response.status_code != 200:
        return "Could not get Discord profile.", 400

    user = user_response.json()

    return jsonify({
        "message": "Discord connected successfully! ♡",
        "username": user.get("username"),
        "id": user.get("id"),
        "avatar": user.get("avatar")
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
