# AWS Credential Generator via SSO (IAM Identity Center)

sso_gen will:
* Log you in to SSO (SSO much be set up)
* Create profiles for all accounts you have access to
* Generate temporary credentials for each of those accounts

## Setup
* Copy `.env.example` to `.env` and edit to add the correct values most importantly:
  * `SSO_START_URL=https://d-XXXXXXXXXX.awsapps.com/start`
* Optional: Install the needed python and poetry versions with [`asdf`](https://asdf-vm.com/) if they are not in your system path

## Makefile

### Code quality
* `format`: Format with `ufmt` that runs black and isort
* `lint`: Run linters
* `sec`: Scan with basic security tools

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

