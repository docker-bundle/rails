#!/bin/sh

WEBPACKER_DEV_SERVER_HOST=0.0.0.0 bin/webpack-dev-server &

$(dirname $0)/run.sh
