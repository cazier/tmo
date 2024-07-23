#!/bin/bash
set -x

coverage run -m pytest "${@:-"tests"}" -s -v
coverage html
