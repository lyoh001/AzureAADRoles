import logging
import os

import azure.functions as func
import requests


def get_graph_api_token():
    oauth2_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    oauth2_body = {
        "client_id": os.environ["GRAPH_CLIENT_ID"],
        "client_secret": os.environ["GRAPH_CLIENT_SECRET"],
        "grant_type": "client_credentials",
        "scope": "https://graph.microsoft.com/.default",
    }
    oauth2_url = (
        f"https://login.microsoftonline.com/{os.environ['TENANT_ID']}/oauth2/v2.0/token"
    )
    try:
        return requests.post(
            url=oauth2_url, headers=oauth2_headers, data=oauth2_body
        ).json()["access_token"]

    except requests.exceptions.RequestException as e:
        raise SystemExit(e)


def get_api_headers(token):
    return {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
    }


def main(mytimer: func.TimerRequest) -> None:
    logging.info("******* Starting the function *******")
    graph_api_headers = get_api_headers(get_graph_api_token())
    try:
        logging.info(
            requests.post(
                url=os.environ["LOGIC_APP_URL"],
                json={"message": roles},
            )
            if (
                roles := "<br><br>".join(
                    f"{role.get('displayName')}:<br>  - {users}"
                    for role in requests.get(
                        url="https://graph.microsoft.com/v1.0/directoryRoles",
                        headers=graph_api_headers,
                    ).json()["value"]
                    if (
                        users := "<br>  - ".join(
                            upn
                            for user in requests.get(
                                url=f"https://graph.microsoft.com/v1.0/directoryRoles/{role['id']}/members",
                                headers=graph_api_headers,
                            ).json()["value"]
                            if (upn := user.get("userPrincipalName", "@")).split("@")[1]
                            not in ["cenitex.vic.gov.au", ""]
                            # if "#EXT#" in (upn := user.get("userPrincipalName", "@"))
                            # or upn.split("@")[1]
                            # not in ["cenitex.vic.gov.au", "vicgov.onmicrosoft.com", ""]
                        )
                    )
                    != ""
                )
            )
            is not None
            else None
        )
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
