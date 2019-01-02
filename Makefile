ifdef test
TOTEST=-k ${test}
else
TOTEST=
endif

postgres_db = ejournal
postgres_test_db = test_$(postgres_db)
postgres_dev_user = ejournal_development_user
postgres_dev_user_pass = development

##### TEST COMMANDS #####

test-back:
	pep8 ./src/django --max-line-length=120 --exclude='./src/django/VLE/migrations','./src/django/VLE/settings*'
	bash -c 'source ./venv/bin/activate && flake8 --max-line-length=120 src/django --exclude="src/django/VLE/migrations/*","src/django/VLE/settings/*","src/django/VLE/settings.py" && deactivate'
	bash -c "source ./venv/bin/activate && pytest --cov=VLE --cov-config .coveragerc src/django/test ${TOTEST} && deactivate"
	bash -c 'source ./venv/bin/activate && isort -rc src/django/ -c && deactivate'

test-front:
	npm run lint --prefix ./src/vue
	npm run test --prefix ./src/vue

display-coverage:
	bash -c "source ./venv/bin/activate && cd src/django/ && coverage report -m && deactivate"

test: test-front test-back

run-test:
	bash -c 'source ./venv/bin/activate && cd ./src/django && python manage.py test test.test_$(arg)'

##### DEVELOP COMMANDS #####

run-front:
	bash -c "source ./venv/bin/activate && npm run dev --prefix ./src/vue && deactivate"

run-back: isort
	bash -c "source ./venv/bin/activate && python ./src/django/manage.py runserver && deactivate"

isort:
	bash -c 'source ./venv/bin/activate && isort -rc src/django/ && deactivate'


setup:
	@echo "This operation will clean old files, press enter to continue (ctrl+c to cancel)"
	@read -r a
	make setup-no-input
setup-no-input:
	@make clean

	# Install apt dependencies and ppa's.
	(sudo apt-cache show python3.6 | grep "Package: python3.6") || \
	(sudo add-apt-repository ppa:deadsnakes/ppa -y; sudo apt update) || echo "0"

	sudo apt install npm -y
	sudo npm install npm@latest -g
	sudo apt install nodejs python3 python3-pip pep8 libpq-dev python3-dev postgresql postgresql-contrib -y

	make setup-venv

	# Reinstall nodejs dependencies.
	npm ci --prefix ./src/vue

	make preset-db-no-input

	@echo "DONE!"

setup-travis:
	(sudo apt-cache show python3.6 | grep "Package: python3.6") || (sudo add-apt-repository ppa:deadsnakes/ppa -y; sudo apt update) || echo "0"
	sudo apt install npm -y
	sudo apt install nodejs python3 python3-pip pep8 -y

	make setup-venv

	# Reinstall nodejs dependencies.
	npm ci --prefix ./src/vue

	@echo "DONE!"

setup-venv:
	sudo pip3 install virtualenv
	virtualenv -p python3 venv
	bash -c '\
		source ./venv/bin/activate && \
		pip install git+https://github.com/joestump/python-oauth2.git && \
		pip install -r requirements.txt && \
		isort -rc src/django/ && \
		deactivate'

##### DEPLOY COMMANDS ######

ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
install:
	bash -c 'bash $(ROOT_DIR)/scripts/install.sh $(ROOT_DIR)'
deploy:
	bash -c 'bash $(ROOT_DIR)/scripts/deploy.sh $(ROOT_DIR)'
serve:
	bash -c 'bash $(ROOT_DIR)/scripts/serve.sh $(ROOT_DIR)'

##### MAKEFILE COMMANDS #####

default:
	make setup-no-input
	make test

clean:
	rm -rf ./venv
	rm -rf ./src/vue/node_modules
	@if [ $(shell id "postgres" > /dev/null 2>&1; echo $$?) -eq 0 ]; then \
		make postgres-reset; \
	fi

##### DATABSE COMMANDS #####

postgres-reset:
	@sudo su -c "psql \
	-c \"DROP DATABASE IF EXISTS $(postgres_db)\" \
	-c \"DROP USER IF EXISTS $(postgres_dev_user)\" \
	" postgres

postgres-drop-development-db:
	@sudo su -c "psql -c \"DROP DATABASE IF EXISTS $(postgres_db)\"" postgres

postgres-init-development:
	@sudo su -c "psql \
	-c \"CREATE DATABASE $(postgres_db)\" \
	-c \"CREATE USER $(postgres_dev_user) WITH PASSWORD '$(postgres_dev_user_pass)'\" \
	-c \"ALTER ROLE $(postgres_dev_user) CREATEDB\" \
	-c \"ALTER ROLE $(postgres_dev_user) SET client_encoding TO 'utf8'\" \
	-c \"ALTER ROLE $(postgres_dev_user) SET default_transaction_isolation TO 'read committed'\" \
	-c \"ALTER ROLE $(postgres_dev_user) SET timezone TO 'CET'\" \
	-c \"GRANT ALL PRIVILEGES ON DATABASE $(postgres_db) TO $(postgres_dev_user)\" \
	" postgres

preset-db:
	@echo "This operation will wipe the $(postgres_db) database, press enter to continue (ctrl+c to cancel)"
	@read -r a
	make preset-db-no-input
preset-db-no-input:
	make postgres-reset
	make postgres-init-development
	make migrate-back
	bash -c 'source ./venv/bin/activate && cd ./src/django && python manage.py preset_db && deactivate'

migrate-back:
	bash -c "source ./venv/bin/activate && cd ./src/django && python manage.py makemigrations VLE && python manage.py migrate && deactivate"

migrate-merge:
	bash -c "source ./venv/bin/activate && cd ./src/django && python manage.py makemigrations --merge"

##### MISC COMMANDS #####

superuser:
	bash -c 'source ./venv/bin/activate && python src/django/manage.py createsuperuser && deactivate'

update-dependencies:
	npm update --dev --prefix ./src/vue
	npm install --prefix ./src/vue

fix-npm:
	npm cache clean -f
	npm config set strict-ssl false
	sudo npm install -g n
	npm config set strict-ssl true
	sudo n stable

fix-live-reload: SHELL:=/bin/bash
fix-live-reload:
	@bash -c '\
		echo $$(( `sudo cat /proc/sys/fs/inotify/max_user_watches` * 2 )) | \
		sudo tee /proc/sys/fs/inotify/max_user_watches'

shell:
	bash -c 'source ./venv/bin/activate && cd ./src/django && python manage.py shell'
