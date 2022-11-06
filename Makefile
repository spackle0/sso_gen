APP_NAME=sso_gen
VERSION=0.1.0
PYVERSION=3.10-slim
#REGISTRY=example.com
#MIN_TEST_COV=80
MIN_TEST_COV=0
BASE=${REGISTRY}/${APP_NAME}
IMAGE_NAME=${BASE}:${VERSION}
IMAGE_LATEST=${BASE}:latest

$(info ========================================)
$(info Version=${VERSION})
$(info App Name=${APP_NAME})
$(info Container Python Version=${PYVERSION})
$(info Minimum Test Coverage=${MIN_TEST_COV})
$(info ========================================)

# Update semver per .bumpversion.cfg
.PHONY: bump_major
bump_major:
	poetry run bump2version --list major

.PHONY: bump_minor
bump_minor:
	poetry run bump2version --list minor

.PHONY: bump_patch
bump_patch:
	poetry run bump2version --list patch

##
# Run

# Run from cmdline
.PHONY: run
run:
	poetry run python ssogen.py

##
# Code formatting

# Format with ufmt: black and isort
.PHONY: format
format:
	@echo =========================
	@echo Formatting...
	@echo =========================
	poetry run black sso_gen/*.py tests/*.py
	poetry run isort sso_gen/*.py tests/*.py

# Separate because ufmt doesn't read config for section titles
.PHONY: isort
isort:
	@echo =========================
	@echo Running isort just to get headings...
	@echo =========================
	poetry run isort sso_gen/*.py tests/*.py


##
# Dev operations

# Linters
.PHONY: lint
lint:
	@echo "Flake8 running"
	-poetry run flake8 ${APP_NAME}
	@echo "Pylint running"
	#-poetry run pylint --ignored-classes=SQLAlchemy ${APP_NAME}
	-poetry run pylint ${APP_NAME}

# Security scanning
.PHONY: sec
sec:
	echo "Security Scanning"
	# Known insecure coding practices
	poetry run bandit -c bandit.yml -r ${APP_NAME}
	# OSS Violations
	poetry run safety check

##
# Container operations

# Create container image
.PHONY: build
build:
	docker build \
		--platform linux/x86_64 \
		--build-arg PYVERSION=${PYVERSION} \
		-t ${IMAGE_NAME} \
		.

# Tag container image
.PHONY: latest
latest:
	docker tag ${IMAGE_NAME} ${IMAGE_LATEST}


# Run container
.PHONY: docker-run
docker-run: build
	docker run --rm \
		--name sso_gen \
		--platform linux/x86_64 \
		--volume ~/.aws:/home/sso_gen/.aws \
		${IMAGE_NAME}

# Push image to a registroy
.PHONY: push
push: build
	docker push ${IMAGE_NAME}

##
# Packaging

# Create python wheel files
.PHONY: dist
dist:
	poetry build
	ls -l dist/*.whl


# Build a binary
.PHONY: binary
binary:
	poetry run pyinstaller --clean --noconfirm --name sso_gen --onefile sso_gen/ssogen.py


