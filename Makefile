all: test

test: build
	echo "To be implemented: test..."

build: clean
	echo "To be implmented: build..."	

run-front: build
	npm run dev --prefix ./src/main/vue

run-back: build
	sudo service mysql start
	pipenv run python ./src/main/django/manage.py runserver

clean:
	

setup:
	sudo apt install nodejs python3 mysql-client mysql-server python3-pip python3-dev libmysqlclient-dev -y
	sudo pip3 install pipenv
	sudo pipenv sync
	sudo npm cache clean -f
	npm config set strict-ssl false
	sudo npm install -g n
	npm config set strict-ssl true
	sudo n stable
	npm install --prefix ./src/main/vue vue-cli webpack	
	npm install --prefix ./src/main/vue
