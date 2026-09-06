set dotenv-load := true

# list justfile recipes
default:
    just --list

# create dev environment
[no-cd]
install:
    curl -LsSf https://astral.sh/uv/install.sh | sh

# install dependencies
[no-cd]
setup:
    uv venv
    source .venv/bin/activate
    uv sync

# run linting
lint:
    ruff format .
    ruff check --fix .

# run tests
test:
    pytest

# clean dev environment
[no-cd]
clean:
    rm -rf .venv
