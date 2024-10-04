# mgc-enum
> Thin python wrapper around `mgc` (https://github.com/microsoftgraph/msgraph-cli) to enumerate Entra directory information

# usage
```
      _ __ ___   __ _  ___       ___ _ __  _   _ _ __ ___
     | '_ ` _ \ / _` |/ __|____ / _ \ '_ \| | | | '_ ` _ \
     | | | | | | (_| | (_|_____|  __/ | | | |_| | | | | | |
     |_| |_| |_|\__, |\___|     \___|_| |_|\__,_|_| |_| |_|
                |___/

usage: mgc-enum [-h] commands: ...

Thin wrapper around mgc (the Microsoft Graph CLI)

positional arguments:
  commands:
    login                      login to micrsoft graph
    organization               enumerate organization information
    current-user               enumerate current user information
    current-user-memberships   enumerate current user group and role memberships
    users                      enumerate directory users
    groups                     enumerate directory groups
    service-principals         enumerate service principals, including graph api permissions
    privileged-role-assignments
                               enumerate user, service principal, and group assignments to privleged roles
    conditional-access         enumerate conditional access policies
    all                        run all enumeration functions and output to a specified directory

options:
  -h, --help                   show this help message and exit
```
