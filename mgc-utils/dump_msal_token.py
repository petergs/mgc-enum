import keyring

print(keyring.get_keyring())
label = "MicrosoftGraph.nocae"
account = "MsalClientID"
service = "Microsoft.Developer.IdentityService"
# keyring.set_keyring(keyring.backends.libsecret.Keyring())
items = keyring.get_keyring().get_preferred_collection()
for item in items:
    print(item)
    print(item.get_label(), item.get_attributes(), item.get_password())
    # print(item.get_password())
