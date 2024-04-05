#!/bin/bash

service cron start

# Execute the main container command
exec "$@"