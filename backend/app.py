from flask import Flask, redirect, request, jsonify, session
from flask_session import Session
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta, timezone
from bot_sequence import execute_sequence
import json
import msal
import os
import secrets


app = Flask(__name__)
app.config.from_object("config.Config")
app.config.update(
    SESSION_TYPE="filesystem",          # store session on server
    SESSION_PERMANENT=False
)

Session(app)
TENANT = "common"  # for personal accounts; use tenant ID for org accounts    
AUTHORITY = f"https://login.microsoftonline.com/{TENANT}"
SCOPES = ["Calendars.ReadWrite"]
FRONTEND_URL = "http://localhost:5173"
REDIRECT_URI = "http://localhost:5000/auth/callback"
TOKEN_CACHE_DIR = "token_cache"

socketio = SocketIO(app, cors_allowed_origins={FRONTEND_URL}, manage_session=True)
pending_states = {}
user_states = {}

SESSION_TIMEOUT = timedelta(minutes=50)

@app.before_request
def enforce_session_rules():
    # If there is no session, do nothing
    if not session:
        return

    now = datetime.now(timezone.utc)

    # First request in this browser session
    if "created_at" not in session:
        session["created_at"] = now
        return

    # Hard timeout check
    if now - session["created_at"] > SESSION_TIMEOUT:
        session.clear()

    
def build_cache(user_id=None):
    cache = msal.SerializableTokenCache()

    if user_id:
        path = f"{TOKEN_CACHE_DIR}/{user_id}.bin"
        if os.path.exists(path):
            cache.deserialize(open(path).read())

    return cache


def save_cache(cache, user_id):
    if cache.has_state_changed:
        with open(f"{TOKEN_CACHE_DIR}/{user_id}.bin", "w") as f:
            f.write(cache.serialize())


def build_msal_app(cache=None):
    return msal.ConfidentialClientApplication(
        app.config["CLIENT_ID"],
        authority=AUTHORITY,
        client_credential=app.config["CLIENT_SECRET"],
        token_cache=cache,
    )

@app.route("/login")
def login():
    state = secrets.token_urlsafe(32)
    pending_states[state] = True

    msal_app = build_msal_app()    

    auth_url = msal_app.get_authorization_request_url(
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
        state=state,
    )
    return redirect(auth_url)

@app.route("/auth/callback")
def call_back():
    code = request.args.get("code")
    state = request.args.get("state")

    if not code or state not in pending_states:
        return "Invalid login attempt", 400

    del pending_states[state]

    cache = build_cache()
    msal_app = build_msal_app(cache)

    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    if "id_token_claims" not in result:
        return jsonify(result), 400

    claims = result["id_token_claims"]
    oid = claims["oid"]
    tid = claims["tid"]

    user_id = f"{oid}.{tid}"
    save_cache(cache, user_id)
    session["user_id"] = user_id

    return redirect(f"{FRONTEND_URL}")
    

@socketio.on("user_message")
def handle_message(data):
    message = data["message"]
    user_id = session.get("user_id")

    if not user_id: 
        emit("auth_required", {"message": "please login"})
        return 

    state = user_states.get(user_id, {})

    state["message"] = f"{state.get("message", "")} \n\n user({user_id}): {message}"

    result = execute_sequence(f"{state["message"]}")
    state["message"] = f"{state["message"]} \n\n bot: {result}"
    user_states[user_id] = state
    emit("bot_message", {"message": result})

if __name__ == "__main__":
    socketio.run(app, port=5000)