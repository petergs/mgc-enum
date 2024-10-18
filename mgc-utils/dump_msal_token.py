import keyring
from keyring.backends.SecretService import Keyring
import platform
import base64
import sys
import json

if __name__ == "__main__":
    label = "MicrosoftGraph.nocae"
    account = "MsalClientID"
    service = "Microsoft.Developer.IdentityService"
    keyring.set_keyring(Keyring())
    print(keyring.get_keyring())
    password = keyring.get_password(service, label)

    # if using keyring fails on linx, fall back to secretstorage
    if platform.system() == "Linux" and password is None:
        import secretstorage

        conn = secretstorage.dbus_init()
        collection = secretstorage.get_default_collection(conn)
        for item in collection.get_all_items():
            # put these in a list
            if item.get_label() == label:
                password = base64.b64decode(item.get_secret()).decode("latin-1")

    if password is None:
        print("Error: no MSAL token found. Did you already run `mgc login`?")
        sys.exit(1)
    else:
        print(json.dumps(json.loads(password), indent=2))
