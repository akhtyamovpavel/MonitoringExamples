#!/bin/bash
# wait-for-grid.sh

set -e

cmd="$@"

echo "$cmd"
exec $cmd
