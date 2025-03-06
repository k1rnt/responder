#!/usr/bin/env bash
# wait-for-it.sh
# 指定されたホストとポートが利用可能になるまで待機するスクリプト

if [ "$#" -lt 3 ]; then
    echo "Usage: $0 host port command"
    exit 1
fi

host="$1"
port="$2"
shift 2
cmd="$@"

echo "Waiting for $host:$port to be available..."
while ! nc -z "$host" "$port"; do
  sleep 1
done
echo "$host:$port is available, executing command: $cmd"
exec $cmd
