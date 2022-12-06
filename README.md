![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-360/) ![semver](https://img.shields.io/badge/semver-0.1.0-blue)


# AWS Credential Generator via SSO (IAM Identity Center)

sso_gen will:
* Log you in to SSO (SSO must be set up)
* Create profiles for all accounts you have access to
* Generate temporary credentials for each of those accounts

## Before you start
You will need the AWS cli installed, at least version 2.

You can get it from the [AWS Documentation](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).

## Setup
* Copy `.env.example` to `.env` and edit to add the correct values most importantly:
  * `SSO_START_URL=https://d-XXXXXXXXXX.awsapps.com/start`
* Copy `acct_map.example.json` to `acct_map.json` and give each account an 
  abbreviation for use in a profile name
* Optional: Install the needed python and poetry versions with [`asdf`](https://asdf-vm.com/) if they are not in your system path
* Have an existing directory `~/.aws/` in your home directory
* Have the minimum in your `~/.aws/config` (TODO: auto-create)
```
[profile login]
sso_start_url = https://d-XXXXXXXXXX.awsapps.com/start
sso_region = us-east-1
```

## Makefile

### Code quality
* `format`: Format with black and isort
* `lint`: Run linters
* `sec`: Scan with basic security tools
* `scan`: Do a Snyk scan via dockerhub (requires a docker login)

### Building
* `build`: Create a docker image
* `binary`: Create a binary with pyinstaler

### Execution
* `run`: Run the script from the commandline
* `docker-run`: Run the docker image

## Reference
#### Special files:
* `.isort.cfg` - configuration file for isort
* `.tool-version` - versions of tools for asdf

#### Poetry configuration:

Force the virtual env to build in the project dir: `poetry config virtualenvs.in-project true` This avoids system clutter.
Be sure the virtual env dir is in `.gitignore`

