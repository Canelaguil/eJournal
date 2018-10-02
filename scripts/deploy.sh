#!/bin/bash

source settings/deploy.conf
source settings/secrets.conf
source settings/database.conf
source settings/email.conf
source settings/variables.conf

###########
# BACKEND #
###########

# Sync django to the target directory
sudo rsync -a --exclude='VLE.db' --exclude='settings/development.py' --exclude='test/' --exclude="__pycache__" ./src/django ${TARGET}
sudo rsync -a --exclude='example_current_lti_params' ./lti ${TARGET}
# Set variables in the target directory
sudo sed -i "s@{{DIR}}@${TARGET}/django@g" ${TARGET}/django/VLE/wsgi.py

# Email variables
sudo sed -i "s@{{SMTP_HOST}}@${SMTP_HOST}@g" ${TARGET}/django/VLE/settings/production.py
sudo sed -i "s@{{SMTP_LOGIN_MAIL}}@${SMTP_LOGIN_MAIL}@g" ${TARGET}/django/VLE/settings/production.py
sudo sed -i "s@{{SMTP_LOGIN_PASSWORD}}@${SMTP_LOGIN_PASSWORD}@g" ${TARGET}/django/VLE/settings/production.py
sudo sed -i "s@{{SMTP_PORT}}@${SMTP_PORT}@g" ${TARGET}/django/VLE/settings/production.py

# DB variables
sudo sed -i "s@{{DATABASE_TYPE}}@${DATABASE_TYPE}@g" ${TARGET}/django/VLE/settings/production.py
sudo sed -i "s@{{DATABASE_NAME}}@${DATABASE_NAME}@g" ${TARGET}/django/VLE/settings/production.py
sudo sed -i "s@{{DATABASE_USER}}@${DATABASE_USER}@g" ${TARGET}/django/VLE/settings/production.py
sudo sed -i "s@{{DATABASE_PASSWORD}}@${DATABASE_PASSWORD}@g" ${TARGET}/django/VLE/settings/production.py
sudo sed -i "s@{{DATABASE_PORT}}@${DATABASE_PORT}@g" ${TARGET}/django/VLE/settings/production.py
sudo sed -i "s@{{DATABASE_HOST}}@${DATABASE_HOST}@g" ${TARGET}/django/VLE/settings/production.py
sudo sed -i "s@{{BASELINK}}@${TYPE}://${SERVERNAME}${HOOKPOINT}@g" ${TARGET}/django/VLE/settings/production.py

# Secret keys
sudo sed -i "s'{{SECRET_KEY}}'${SECRET_KEY}'g" ${TARGET}/django/VLE/settings/production.py
sudo sed -i "s'{{LTI_SECRET}}'${LTI_SECRET}'g" ${TARGET}/django/VLE/settings/production.py
sudo sed -i "s'{{LTI_KEY}}'${LTI_KEY}'g" ${TARGET}/django/VLE/settings/production.py
sudo sed -i "s@development@production@g" ${TARGET}/django/manage.py

# File variables
sudo sed -i "s@'{{USER_MAX_FILE_SIZE_BYTES}}'@${USER_MAX_FILE_SIZE_BYTES}@g" ${TARGET}/django/VLE/settings/production.py
sudo sed -i "s@'{{USER_MAX_TOTAL_STORAGE_BYTES}}'@${USER_MAX_TOTAL_STORAGE_BYTES}@g" ${TARGET}/django/VLE/settings/production.py

# Migrate the database
source ${TARGET}/venv/bin/activate
    python ${TARGET}/django/manage.py migrate || sudo sh -c "${TARGET}/venv/bin/activate && python ${TARGET}/django/manage.py migrate"
    python ${TARGET}/django/manage.py collectstatic --noinput
    python ${TARGET}/django/manage.py check --deploy
deactivate

# Sync the static files to the static directory
sudo mkdir ${TARGET}/django/media
sudo chmod g+w ${TARGET}/django/media
sudo chgrp www-data ${TARGET}/django/media
############
# FRONTEND #
############

# Build vue
sudo npm run-script build --prefix ./src/vue

# Deploy
sudo rsync -a ./src/vue/dist/ ${TARGET}
sudo sed -i "s@http://localhost:8000/@${TYPE}://${APIURL}${HOOKPOINT}@g" ${TARGET}/static/js/*
