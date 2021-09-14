#!/usr/bin/env bash

APP_HOME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${APP_HOME}"

npm install --ignore-scripts
npm run fonts

MODULES=("jquery" "fomantic-ui")
mkdir web/modules/
for module in ${MODULES[@]}; do
    cp -r node_modules/${module}/dist web/modules/$module
done

rm -r node_modules/