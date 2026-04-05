#!/bin/sh
set -e

# Substitute environment variables in the config file using sed
sed "s|\${DISCORD_WEBHOOK_URL}|${DISCORD_WEBHOOK_URL}|g" /etc/alertmanager/config.yml.template > /etc/alertmanager/config.yml

# Start Alertmanager with the processed config
exec /bin/alertmanager "$@"
