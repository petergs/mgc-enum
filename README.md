# mgc-enum
> Thin python wrapper around `mgc` (https://github.com/microsoftgraph/msgraph-cli) to enumerate 
Entra directory information

# features
The primary goal of this script is to simplify enumeration operations that typically require 
chaining multiple Graph API calls or mapping GUIDs to users, groups, roles, or service principals
including the ability to:
- Dump a list of privileged role assignments to direct users, users within role-assignable groups, 
and service principals.
- Identify service principals that have high-privileged Graph API permissions

There are many tools out there to do the same thing, but quite a few rely on PowerShell and have 
mixed support for MacOS and Linux.

# setup
Other than python 3.10+, there are no additional python dependencies. Simply install the [Microsoft 
Graph CLI](https://github.com/microsoftgraph/msgraph-cli) and ensure it's in your `PATH`.

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

Run `mgc-enum login` to default to an Interactive Browser login format with the client set to 
Microsoft Azure PowerShell (1950a258-227b-4e31-a9cf-717495945fc2), then run the command of your 
choice.
