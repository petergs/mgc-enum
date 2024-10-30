import platform
import base64
import sys
import json
import argparse
from enum import Enum
import sys
import json
import pathlib
from subprocess import run, PIPE, STDOUT
import shlex
import shutil
import os
import pwd
import urllib.request
import urllib.parse
import urllib.error
from dataclasses import dataclass


class TokenType(Enum):
    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return str(self.value)

    REFRESH = "RefreshToken"
    ACCESS = "AccessToken"
    ID = "IdToken"


@dataclass
class RefreshToken:
    tenant_id: str
    client_id: str
    user_id: str
    secret: str
    family_id: str

    @classmethod
    def init_from_cache(cls):
        pass

    def _format_for_cache(self) -> dict:
        rt_key = f"{self.user_id}.{self.tenant_id}-login.windows.net-refreshtoken-1--"
        return {
            rt_key: {
                "home_account_id": f"{self.user_id}.{self.tenant_id}",
                "environment": "login.windows.net",
                # "client_info": base64.b64ecode(str({"uid": "", "tid": ""})),
                "client_id": self.client_id,
                "secret": self.secret,
                "credential_type": "RefreshToken",
                "family_id": self.family_id,
            }
        }


@dataclass
class IdToken:
    tenant_id: str
    client_id: str
    username: str
    user_id: str
    secret: str

    @classmethod
    def init_from_cache(cls, entry: dict):
        jwt = entry["secret"].split(".")[1]  # split jwt
        jwt = base64.b64decode(jwt + "==").decode("latin-1")
        jwt = json.loads(jwt)
        username = jwt["preferred_username"]
        tenant_id = entry["home_account_id"].split(".")[0]
        user_id = entry["home_account_id"].split(".")[1]
        return IdToken(
            tenant_id=tenant_id,
            client_id=entry["client_id"],
            username=username,
            user_id=user_id,
            secret=entry["secret"],
        )

    def _format_for_cache(self) -> dict:
        idt_key = f"{self.user_id}.{self.tenant_id}-login.windows.net-idtoken-{self.client_id}-{self.tenant_id}-"
        return {
            idt_key: {
                "home_account_id": f"{self.user_id}.{self.tenant_id}",
                "environment": "login.windows.net",
                # "client_info": base64.b64ecode(str({"uid": "", "tid": ""})),
                "client_id": self.client_id,
                "secret": self.secret,
                "credential_type": "IdToken",
                "realm": self.tenant_id,
            }
        }


@dataclass
class MgcToken:
    token_type: TokenType
    tenant_id: str
    client_id: str
    username: str
    user_id: str
    token_content: None


class RefreshResponse:
    def __init__(self, response: dict):
        self.token_type: str = response["token_type"]  # Bearer
        self.scope: str = response["scope"]
        self.expires_in: str = response["expires_in"]
        self.ext_expires_in: str = response["ext_expires_in"]
        self.expires_on: str = response["expires_on"]
        self.not_before: str = response["not_before"]
        self.resource: str = response["resources"]  # https://graph.microsoft.com
        self.access_token: str = response["access_token"]
        self.refresh_token: str = response["refresh_token"]
        self.foci: str = response["foci"]
        self.id_token: str = response["id_token"]


@dataclass
class AccessTokenContent:
    home_account_id: TokenType
    environment: str
    client_info: str
    client_id: str
    secret: str
    realm: str

    @classmethod
    def init_from_cache(cls, entry: dict):
        pass

    @classmethod
    def init_from_refresh_response(cls, response: RefreshResponse):
        pass

    def write_cache(self):
        pass

    def _get_access_token_cache_format(self):
        pass


def print_tokens(tokens: list[MgcToken]) -> None:
    for token in tokens:
        print(token.__dict__)


class MgcAuthRecord:
    def __init__(self):
        home = pathlib.Path.home()
        with open(f"{home}/.mgc/authRecord", "r") as f:
            auth_record = "\n".join(f.readlines())
            auth_record = json.loads(auth_record)
        self.username: str = auth_record["username"]
        self.authority: str = auth_record["authority"]
        self.tenant_id: str = auth_record["tenantId"]
        self.client_id: str = auth_record["clientId"]
        self.user_id: str = auth_record["homeAccountId"].split(".")[0]

    def __str__(self) -> str:
        return str(self.__dict__)

    def __repr__(self) -> str:
        return str(self.__dict__)

    def _commit_auth_record(self):
        ar = {
            "username": self.username,
            "authority": self.authority,
            "homeAccountId": f"{self.user_id}.{self.tenant_id}",
            "tenantId": self.tenant_id,
            "clientId": self.client_id,
            "version": "1.0",
        }
        home = pathlib.Path.home()
        with open(f"{home}/.mgc/authRecord", "w") as f:
            f.write(json.dumps(ar))


MSAL_KEYRING_ACCOUNT = "MicrosoftGraph.nocae"
MSAL_KEYRING_LABEL = "MsalClientID"
MSAL_KEYRING_SERVICE = "Microsoft.Developer.IdentityService"
MS_GRAPH_API_BASE_URL = "https://graph.microsoft.com"
MSO_LOGIN_URL = "https://login.microsoftonline.com"

# from https://github.com/secureworks/family-of-client-ids-research/blob/main/known-foci-clients.csv
FOCI_CLIENTS = [
    {
        "client_id": "1950a258-227b-4e31-a9cf-717495945fc2",
        "app_name": "Microsoft Azure PowerShell",
    },
    {
        "client_id": "00b41c95-dab0-4487-9791-b9d2c32c80f2",
        "app_name": "Office 365 Management",
    },
    {
        "client_id": "04b07795-8ddb-461a-bbee-02f9e1bf7b46",
        "app_name": "Microsoft Azure CLI",
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

FOCI_CLIENTS.extend(
    [
        {
            "client_id": "fb78d390-0c51-40cd-8e17-fdbfab77341b",
            "app_name": "Microsoft Exchange REST API Based PowerShell",
        }
    ]
)


def urlreq(method: str, url: str, headers: dict = {}, data: dict | None = None) -> str:
    """
    Function for simple HTTP requests using urllib.requests
    Ref: https://docs.python.org/3/howto/urllib2.html
    """

    encoded_data: bytes | None = None
    if data is not None:
        if method == "GET":
            # urlencode data as path parameters
            params: str = urllib.parse.urlencode(data)
            url = f"{url}?{params}"
        else:
            encoded_data = urllib.parse.urlencode(data).encode("utf-8")

    request = urllib.request.Request(
        url=url, data=encoded_data, headers=headers, method=method
    )

    with urllib.request.urlopen(request) as response:
        return response.read().decode("utf-8")


def cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python mgc-utils.py",
        description="Utilities for the Microsoft Graph CLI (mgc)",
    )
    subparsers = parser.add_subparsers(dest="cmd", metavar="subcommand")
    parser_list = subparsers.add_parser(
        name="list-tokens", help="Print all MSAL tokens currently stored in the keyring"
    )
    subparsers.add_parser(
        name="clear-tokens", help="Clear MSAL tokens for the OS keyring"
    )
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
    subparsers.add_parser(name="write-tokens", help="")
    return parser


def list_tokens() -> tuple[list[MgcToken], dict]:
    if platform.system() == "Linux":
        find_cmd = f"secret-tool lookup {MSAL_KEYRING_LABEL} {MSAL_KEYRING_SERVICE}"
        output = run(shlex.split(find_cmd), stdout=PIPE, stderr=STDOUT)
        tokens = base64.b64decode(output.stdout.decode()).decode("utf-8")
        tokens = json.loads(tokens)
    elif platform.system() == "Darwin":
        find_cmd = f'security find-generic-password -w -a "{MSAL_KEYRING_ACCOUNT}"'
        output = run(shlex.split(find_cmd), stdout=PIPE, stderr=STDOUT)
        tokens = json.loads(output.stdout.decode())
    else:
        print(f"Error: Unsupported platform {platform.system()}")
        sys.exit(1)

    if tokens is None:
        sys.exit(1)

    result = []
    for _, v in tokens["AccessToken"].items():
        jwt = v["secret"].split(".")[1]  # split jwt
        jwt = base64.b64decode(jwt + "==").decode("latin-1")
        jwt = json.loads(jwt)
        username = jwt["upn"]
        tenant_id = jwt["tid"]
        user_id = jwt["oid"]
        token = MgcToken(
            token_type=TokenType.ACCESS,
            tenant_id=tenant_id,
            client_id=v["client_id"],
            username=username,
            user_id=user_id,
            token_content=None,
        )
        result.append(token)

    for _, v in tokens["RefreshToken"].items():
        jwt = v["secret"].split(".")[1]  # split jwt
        username = ""
        tenant_id = v["home_account_id"].split(".")[0]
        user_id = v["home_account_id"].split(".")[1]
        token = MgcToken(
            token_type=TokenType.REFRESH,
            tenant_id=tenant_id,
            client_id=v["client_id"],
            username=username,
            user_id=user_id,
            token_content=None,
        )
        result.append(token)

    for _, v in tokens["IdToken"].items():
        jwt = v["secret"].split(".")[1]  # split jwt
        jwt = base64.b64decode(jwt + "==").decode("latin-1")
        jwt = json.loads(jwt)
        username = jwt["preferred_username"]
        tenant_id = v["home_account_id"].split(".")[0]
        user_id = v["home_account_id"].split(".")[1]
        token = MgcToken(
            token_type=TokenType.ID,
            tenant_id=tenant_id,
            client_id=v["client_id"],
            username=username,
            user_id=user_id,
            token_content=None,
        )
        result.append(token)

    return result, tokens


def write_tokens() -> None:
    # For some reason, keychain access will prompt for a keychain password for future mgc calls
    # after modifying the token. Even with usage of the -T parameter to update the keychain item's
    # ACL to include mgc.
    """
    mgc_path = shutil.which("mgc")
    if mgc_path is None:
        print("mgc not found in PATH")
        sys.exit(1)
    mgc_path = pathlib.Path(mgc_path).resolve() # resolve symlinks if present
    """
    if platform.system() == "Darwin":
        token = json.dumps(list_tokens()[1])
        add_cmd = f"security add-generic-password -a '{MSAL_KEYRING_ACCOUNT}' -s '{MSAL_KEYRING_SERVICE}' -w '{token}' -U "  # -T '{mgc_path}"
        add_output = run(shlex.split(add_cmd), stdout=PIPE, stderr=STDOUT)
        print(add_output.stdout.decode())


def clear_tokens() -> None:
    if platform.system() == "Darwin":
        username = pwd.getpwuid(os.getuid()).pw_name
        cmd = f"security delete-generic-password -a '{MSAL_KEYRING_ACCOUNT}' -s '{MSAL_KEYRING_SERVICE}'"
        if platform.system() == "Darwin":
            output = run(shlex.split(cmd), stdout=PIPE, stderr=STDOUT)
            print(output.stdout.decode())


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
        tokens = list_tokens()[1]["AccessToken"]
    else:
        tokens = list_tokens()[1]["RefreshToken"]

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
    refresh_token: str | None = None,
    refresh_token_client_id: str | None = None,
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
        r = urlreq(
            method="POST", url=f"{MSO_LOGIN_URL}/{tenant_id}/oauth2/token", data=payload
        )
        return json.loads(r)
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
        print(r)
        exit()
        try:
            scopes = r["scope"].split(" ")
            success = True
        except KeyError as e:
            scopes = []
            success = False

        result.append(
            {
                "client_id": next_client,
                "app_name": client["app_name"],
                "scopes": scopes,
                "foci": True,
                "success": success,
            }
        )

    return result


if __name__ == "__main__":
    args = cli().parse_args()
    if args.cmd:
        match args.cmd:
            case "list-tokens":
                # print(json.dumps(list_tokens(), indent=2))
                print_tokens(list_tokens()[0])
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
                home = pathlib.Path.home()
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
            case "write-tokens":
                write_tokens()
            case _:
                print(f"The command specified is not valid.")
    else:
        cli().print_help(sys.stderr)
        sys.exit(1)
