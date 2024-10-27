#!/bin/bash
set -x

rm -rf htmlcov
coverage run -m pytest "${@:-"tests"}" -s -v
coverage html
