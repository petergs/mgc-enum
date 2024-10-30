import platform
import base64
import sys
import json
import argparse
from enum import Enum
import sys
import json
from pathlib import Path

import requests
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import jwt
import keyring


MSAL_KEYRING_LABEL = "MicrosoftGraph.nocae"
MSAL_KEYRING_ACCOUNT = "MsalClientID"
MSAL_KEYRING_SERVICE = "Microsoft.Developer.IdentityService"
MS_GRAPH_API_BASE_URL = "https://graph.microsoft.com"
MSO_LOGIN_URL = "https://login.microsoftonline.com"

# from https://github.com/secureworks/family-of-client-ids-research/blob/main/known-foci-clients.csv
FOCI_CLIENTS = [
    {
        "client_id": "00b41c95-dab0-4487-9791-b9d2c32c80f2",
        "app_name": "Office 365 Management",
    },
    {
        "client_id": "04b07795-8ddb-461a-bbee-02f9e1bf7b46",
        "app_name": "Microsoft Azure CLI",
    },
    {
        "client_id": "1950a258-227b-4e31-a9cf-717495945fc2",
        "app_name": "Microsoft Azure PowerShell",
    },
    {
        "client_id": "1fec8e78-bce4-4aaf-ab1b-5451cc387264",
        "app_name": "Microsoft Teams",
    },
    {
        "client_id": "26a7ee05-5602-4d76-a7ba-eae8b7b67941",
        "app_name": "Windows Search",
    },
    {
        "client_id": "27922004-5251-4030-b22d-91ecd9a37ea4",
        "app_name": "Outlook Mobile",
    },
    {
        "client_id": "4813382a-8fa7-425e-ab75-3b753aab3abb",
        "app_name": "Microsoft Authenticator App",
    },
    {
        "client_id": "ab9b8c07-8f02-4f72-87fa-80105867a763",
        "app_name": "OneDrive SyncEngine",
    },
    {
        "client_id": "d3590ed6-52b3-4102-aeff-aad2292ab01c",
        "app_name": "Microsoft Office",
    },
    {
        "client_id": "872cd9fa-d31f-45e0-9eab-6e460a02d1f1",
        "app_name": "Visual Studio",
    },
    {
        "client_id": "af124e86-4e96-495a-b70a-90f90ab96707",
        "app_name": "OneDrive iOS App",
    },
    {
        "client_id": "2d7f3606-b07d-41d1-b9d2-0d0c9296a6e8",
        "app_name": "Microsoft Bing Search for Microsoft Edge",
    },
    {
        "client_id": "844cca35-0656-46ce-b636-13f48b0eecbd",
        "app_name": "Microsoft Stream Mobile Native",
    },
    {
        "client_id": "87749df4-7ccf-48f8-aa87-704bad0e0e16",
        "app_name": "Microsoft Teams - Device Admin Agent",
    },
    {
        "client_id": "cf36b471-5b44-428c-9ce7-313bf84528de",
        "app_name": "Microsoft Bing Search",
    },
    {
        "client_id": "0ec893e0-5785-4de6-99da-4ed124e5296c",
        "app_name": "Office UWP PWA",
    },
    {
        "client_id": "22098786-6e16-43cc-a27d-191a01a1e3b5",
        "app_name": "Microsoft To-Do client",
    },
    {"client_id": "4e291c71-d680-4d0e-9640-0a3358e31177", "app_name": "PowerApps"},
    {
        "client_id": "57336123-6e14-4acc-8dcf-287b6088aa28",
        "app_name": "Microsoft Whiteboard Client",
    },
    {
        "client_id": "57fcbcfa-7cee-4eb1-8b25-12d2030b4ee0",
        "app_name": "Microsoft Flow",
    },
    {
        "client_id": "66375f6b-983f-4c2c-9701-d680650f588f",
        "app_name": "Microsoft Planner",
    },
    {
        "client_id": "9ba1a5c7-f17a-4de9-a1f1-6178c8d51223",
        "app_name": "Microsoft Intune Company Portal",
    },
    {
        "client_id": "a40d7d7d-59aa-447e-a655-679a4107e548",
        "app_name": "Accounts Control UI",
    },
    {
        "client_id": "a569458c-7f2b-45cb-bab9-b7dee514d112",
        "app_name": "Yammer iPhone",
    },
    {"client_id": "b26aadf8-566f-4478-926f-589f601d9c74", "app_name": "OneDrive"},
    {
        "client_id": "c0d2a505-13b8-4ae0-aa9e-cddd5eab0b12",
        "app_name": "Microsoft Power BI",
    },
    {"client_id": "d326c1ce-6cc6-4de2-bebc-4591e5e13ef0", "app_name": "SharePoint"},
    {
        "client_id": "e9c51622-460d-4d3d-952d-966a5b1da34c",
        "app_name": "Microsoft Edge",
    },
    {
        "client_id": "eb539595-3fe1-474e-9c1d-feb3625d1be5",
        "app_name": "Microsoft Tunnel",
    },
    {
        "client_id": "ecd6b820-32c2-49b6-98a6-444530e5a77a",
        "app_name": "Microsoft Edge",
    },
    {
        "client_id": "f05ff7c9-f75a-4acd-a3b5-f4b6a870245d",
        "app_name": "SharePoint Android",
    },
    {
        "client_id": "f44b1140-bc5e-48c6-8dc0-5cf5a53c0e34",
        "app_name": "Microsoft Edge",
    },
    {
        "client_id": "be1918be-3fe3-4be9-b32b-b542fc27f02e",
        "app_name": "M365 Compliance Drive Client",
    },
    {
        "client_id": "cab96880-db5b-4e15-90a7-f3f1d62ffe39",
        "app_name": "Microsoft Defender Platform",
    },
    {
        "client_id": "d7b530a4-7680-4c23-a8bf-c52c121d2e87",
        "app_name": "Microsoft Edge Enterprise New Tab Page",
    },
    {
        "client_id": "dd47d17a-3194-4d86-bfd5-c6ae6f5651e3",
        "app_name": "Microsoft Defender for Mobile",
    },
    {
        "client_id": "e9b154d0-7658-433b-bb25-6b8e0a8a7c59",
        "app_name": "Outlook Lite",
    },
]

FOCI_CLIENTS.extend([
    {"client_id": "fb78d390-0c51-40cd-8e17-fdbfab77341b", "app_name": "Microsoft Exchange REST API Based PowerShell"}
])


class TokenType(Enum):
    REFRESH = 1
    ACCESS = 2


def cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python mgc-utils.py",
        description="Utilities for the Microsoft Graph CLI (mgc)",
    )
    subparsers = parser.add_subparsers(dest="cmd", metavar="subcommand")
    parser_list = subparsers.add_parser(
        name="list-tokens", help="Print all MSAL tokens currently stored in the keyring"
    )
    subparsers.add_parser(name="clear-tokens", help="Clear MSAL tokens for the OS keyring")
    parser_list.add_argument(
        "-f",
        "--format",
        required=False,
        choices=["json", "table"],
        help="Output format",
    )
    parser_dump = subparsers.add_parser(
        name="dump-token", help="Print an MSAL token from the keyring"
    )
    parser_dump.add_argument(
        "-c",
        "--client-id",
        required=False,
        help="Azure client id",
    )
    parser_dump.add_argument(
        "-t",
        "--token-type",
        default="access",
        choices=["access", "refresh"],
        required=False,
        help="Token type to get - either a refresh token or an access token",
    )
    subparsers.add_parser(name="foci-login", help="")
    subparsers.add_parser(name="foci-scope-enum", help="")
    return parser


def graph_api_get(
    path: str,
    client_id: str | None = None,
    version: str = "v1.0",
    params: dict | None = None,
):
    access_token = dump_token(client_id=client_id, token_type=TokenType.ACCESS)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    r = requests.get(
        url=f"{MS_GRAPH_API_BASE_URL}/{version}/{path}", headers=headers, params=params
    ).json()
    return r


def list_tokens() -> dict:
    if platform.system() == "Linux":
        from keyring.backends.SecretService import Keyring

        keyring.set_keyring(Keyring())

    keyring_secret = keyring.get_password(MSAL_KEYRING_SERVICE, MSAL_KEYRING_LABEL)

    # if using keyring fails on Linx, fall back to secretstorage
    if platform.system() == "Linux" and keyring_secret is None:
        import secretstorage

        conn = secretstorage.dbus_init()
        collection = secretstorage.get_default_collection(conn)
        for item in collection.get_all_items():
            if item.get_label() == MSAL_KEYRING_LABEL:
                keyring_secret = base64.b64decode(item.get_secret()).decode("latin-1")

    if keyring_secret is None:
        print("Error: No MSAL token found. Did you already run `mgc login`?")
        sys.exit(1)
    else:
        return json.loads(keyring_secret)

def clear_tokens() -> None:
    keyring.set_password(MSAL_KEYRING_SERVICE, MSAL_KEYRING_LABEL, "")


def dump_token(
    client_id: str | None = None, token_type: TokenType = TokenType.ACCESS
) -> str:
    """
    Returns the first available MSAL token if multiple apps have been logged into
    and no client_id is specified. Otherwise, it will return the token for the specified
    client_id if it exists.
    """
    token = None
    if token_type == TokenType.ACCESS:
        tokens = list_tokens()["AccessToken"]
    else:
        tokens = list_tokens()["RefreshToken"]

    for k in tokens.keys():
        token = tokens[k]["secret"]
        if len(tokens.keys()) == 1 or tokens[k]["client_id"] == client_id:
            break

    if token is None:
        print("Error: No tokens found")
        sys.exit(1)
    else:
        return token


def foci_login(
    new_client_id: str,
    tenant_id: str,
    refresh_token: str = None,
    refresh_token_client_id: str = None,
) -> dict:
    """
    Use a refresh token present in the MSAL keyring entry to login as another foci app
    """
    foci_client_ids = [x["client_id"] for x in FOCI_CLIENTS]
    if refresh_token is None and refresh_token_client_id is None:
        print(
            f"Error: foci_login expects either a refresh_token or a refresh_token_client_id"
        )
        sys.exit(1)

    if not refresh_token:
        if refresh_token_client_id in foci_client_ids:
            refresh_token = dump_token(
                refresh_token_client_id, token_type=TokenType.REFRESH
            )
        else:
            print(
                f"Error: The value supplied for refresh_token_client_id ({refresh_token_client_id}) is not a known foci client."
            )

    if new_client_id in foci_client_ids:
        payload = {
            "resource": MS_GRAPH_API_BASE_URL,
            "client_id": new_client_id,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "scope": "openid",
        }
        """
        retry = Retry(
            total=4,
            backoff_factor=2,
            status_forcelist=[400, 429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        adapter = HTTPAdapter(max_retries=retry)
        s = requests.Session()
        s.mount('https://', adapter)
        """
        r = requests.post(
            url=f"{MSO_LOGIN_URL}/{tenant_id}/oauth2/token", data=payload
        )
        return r.json()
    else:
        print(
            f"Error: The value supplied for new_client_id ({new_client_id}) is not a known foci client."
        )
        sys.exit(1)


def foci_scope_enum(refresh_token_client_id: str, tenant_id: str) -> list:
    result = []
    refresh_token = dump_token(refresh_token_client_id, token_type=TokenType.REFRESH)
    for client in FOCI_CLIENTS:
        next_client = client["client_id"]

        r = foci_login(
            refresh_token=refresh_token,
            new_client_id=next_client,
            tenant_id=tenant_id,
        )
        try:
            scopes = r["scope"].split(" ")
            success = True
        except KeyError as e:
            scopes = []
            success = False

        result.append(
            {"client_id": next_client, "app_name": client["app_name"], "scopes": scopes, "foci": True, "success": success}
        )

    return result


if __name__ == "__main__":
    args = cli().parse_args()
    if args.cmd:
        match args.cmd:
            case "list-tokens":
                print(json.dumps(list_tokens(), indent=2))
            case "clear-tokens":
                clear_tokens()
                print("Clearing keyring tokens...")
            case "dump-token":
                if args.token_type == "refresh":
                    token_type = TokenType.REFRESH
                else:
                    token_type = TokenType.ACCESS
                print(dump_token(client_id=args.client_id, token_type=token_type))
            case "foci-login":
                home = Path.home()
                with open(f"{home}/.mgc/authRecord", "r") as f:
                    auth_record = "\n".join(f.readlines())
                    auth_record = json.loads(auth_record)
                tenant_id = auth_record["tenantId"]
                username = auth_record["username"]
                r = foci_login(
                    refresh_token_client_id="872cd9fa-d31f-45e0-9eab-6e460a02d1f1",
                    new_client_id="1950a258-227b-4e31-a9cf-717495945fc2",
                    tenant_id=tenant_id,
                )
                print(json.dumps(r, indent=2))
            case "foci-scope-enum":
                tenant_id = "ef04ece3-8474-47ca-a91a-84da99c7c68f"
                r = foci_scope_enum(
                    refresh_token_client_id="1950a258-227b-4e31-a9cf-717495945fc2",
                    tenant_id=tenant_id,
                )
                print(json.dumps(r, indent=2))
            case _:
                print(f"The command specified is not valid.")
    else:
        cli().print_help(sys.stderr)
        sys.exit(1)
