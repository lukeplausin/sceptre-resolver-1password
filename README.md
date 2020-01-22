# Sceptre resolver for 1password

This resolver can retrieve secrets and documents from 1password.

## Why?

One simple reason - secrets should never be committed to source code!

Use this resovler to keep your secrets in 1password. You can then use the `!one_password` resolver in your sceptre config files to refer to the 1password secrets.

You can filter secrets dynamically based on tags and specify the field name.

## Installation

```
pip install git+https://github.com/lukeplausin/sceptre-resolver-1password.git
```

## Usage

Specify the field name and tags in this format:

```
{field name}#{comma separated tag list}
```

### Examples

```yaml
# This resolver will query for a secret with the tags "rds" and "production", and return the "username" and "password" fields
Username: !one_password username#rds,production
Password: !one_password password#rds,production
# This resolver will retrieve the document of a secret with the tags "instance", "production" and "userdata"
UserData: !one_password document#instance,production,userdata
```

- Tell people how to install it (e.g. pip install ...).
- Be clear about the purpose of the resolver, its capabilities and limitations.
- Tell people how to use it.
- Give examples of the resolver in use.

Read our wiki to learn how to use this repo:
https://github.com/Sceptre/project/wiki/Sceptre-Resolver-Template

If you have any questions or encounter an issue
[please open an issue](https://github.com/Sceptre/project/issues/new)
