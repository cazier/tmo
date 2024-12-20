#!/bin/bash
set -x

rm -rf htmlcov
coverage run -m pytest -s "${@:-"tests"}"
coverage html
