import os
from flask import Flask, redirect, request
import requests

app = Flask(__name__)

# ============================================================
# CONFIG
# ============================================================

CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")

# ONLY THIS DISCORD ACCOUNT IS ALLOWED
ALLOWED_DISCORD_ID = "1538963396064575591"

WEBSITE_URL = "https://voidkii.github.io/anaisha-website-2.0/"

DISCORD_API = "https://discord.com/api/v10"


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():
    return "Anaisha Discord Auth is online! ♡"


# ============================================================
# LOGIN
# ============================================================

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


# ============================================================
# CALLBACK
# ============================================================

@app.route("/callback")
def callback():

    code = request.args.get("code")

    if not code:
        return "No authorization code received.", 400

    # --------------------------------------------------------
    # Exchange code for access token
    # --------------------------------------------------------

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

    access_token = token_data.get("access_token")

    if not access_token:
        return "No access token received.", 400

    # --------------------------------------------------------
    # Get Discord user
    # --------------------------------------------------------

    user_response = requests.get(
        f"{DISCORD_API}/users/@me",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    if user_response.status_code != 200:
        return "Could not get Discord profile.", 400

    user = user_response.json()

    user_id = user.get("id")

    # --------------------------------------------------------
    # CHECK USER ID
    # --------------------------------------------------------

    if user_id != ALLOWED_DISCORD_ID:

        return """
        <html>
        <head>
            <title>Access Denied</title>
            <style>
                body {
                    background: #0b0b0f;
                    color: white;
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding-top: 120px;
                }

                h1 {
                    color: #ff6b81;
                }

                p {
                    color: #aaa;
                }
            </style>
        </head>

        <body>

            <h1>♡ Wrong Discord Account</h1>

            <p>
                This website is connected to a private Discord account.
            </p>

        </body>
        </html>
        """, 403

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    print(
        "Discord connected successfully:",
        user.get("username"),
        user.get("id")
    )

    # Send them back to the website
    return redirect(
        WEBSITE_URL + "?discord=connected"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
