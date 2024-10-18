import keyring
import platform
import base64
import sys
import json
import argparse

MSAL_KEYRING_LABEL = "MicrosoftGraph.nocae"
MSAL_KEYRING_ACCOUNT = "MsalClientID"
MSAL_KEYRING_SERVICE = "Microsoft.Developer.IdentityService"


def cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python mgc-utils.py",
        description="Utilities for the Microsoft Graph CLI (mgc)",
    )
    subparsers = parser.add_subparsers(dest="cmd", metavar="subcommand")
    parser_dump = subparsers.add_parser(
        name="list-tokens", help="Print all MSAL tokens currently stored in the keyring"
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
    return parser


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


def dump_token(client_id=None) -> str:
    """
    Returns the first available MSAL token if multiple apps have been logged into
    and no client_id is specified.
    """
    token = None
    access_tokens = list_tokens()["AccessToken"]
    for k in access_tokens.keys():
        token = access_tokens[k]["secret"]
        if len(access_tokens.keys()) == 1 or access_tokens[k]["client_id"] == client_id:
            break

    if token is None:
        print("Error: No tokens found")
        sys.exit(1)
    else:
        return token


def foci_login() -> None:
    """
    Use a refresh token present in the MSAL keyring entry to login as another foci app
    """
    pass


if __name__ == "__main__":
    args = cli().parse_args()
    if args.cmd:
        match args.cmd:
            case "list-tokens":
                print(json.dumps(list_tokens(), indent=2))
            case "dump-token":
                print(dump_token(args.client_id))
            case _:
                print(f"The command specified is not valid.")
    else:
        cli().print_help(sys.stderr)
        sys.exit(1)
