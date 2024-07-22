import os

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


def redirect_to_strava_authentication() -> str:
    auth_uri = "https://www.strava.com/oauth/authorize"
    redirect_uri = "http://localhost:8501"
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "approval_prompt": "force",
        "scope": "activity:read_all",
    }
    params_str = "&".join(f"{key}={val}" for key, val in params.items())
    auth_url = f"{auth_uri}?{params_str}"
    return auth_url


def request_strava_access_token(code: str) -> requests.Response:
    token_url = "https://www.strava.com/oauth/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    return response


def request_athlete_activities(access_token: str) -> requests.Response:
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(activities_url, headers=headers)
    return response


def main():
    st.title("Strava Analysis Tool")

    st.link_button("Retrieve Data", url=redirect_to_strava_authentication())

    # st.text(st.session_state)

    if st.query_params.get("code", None):
        st.session_state["code"] = st.query_params["code"]
        st.query_params.clear()
        st.rerun()

    if "code" not in st.session_state:
        return

    if "refresh_token" not in st.session_state:
        response = request_strava_access_token(st.session_state["code"])

        if not response.status_code == 200:
            st.text(f"Autorization failed!: {response}")
            return

        st.session_state["refresh_token"] = response.json().get("refresh_token")
        st.session_state["access_token"] = response.json().get("access_token")
        st.rerun()

    if "athlete_activities_json" not in st.session_state:
        response = request_athlete_activities(st.session_state["access_token"])

        if not response.status_code == 200:
            st.text(f"Falied to retrieve athlete activities: {response}")
            return

        st.session_state["athlete_activities_json"] = response.json()

    data = pd.DataFrame(st.session_state["athlete_activities_json"])
    st.dataframe(data=data)


if __name__ == "__main__":
    main()
