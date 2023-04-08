#!/usr/bin/env bash

set -e

find crawler \
	-type d -name migrations -prune -o \
	-type f -name "*.py" \
	-exec "$@" {} +
