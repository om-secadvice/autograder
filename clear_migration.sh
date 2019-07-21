#!/bin/sh
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
#sudo mysql -e "DROP database autograder_db;CREATE database autograder_db character set utf8mb4 COLLATE utf8mb4_unicode_ci;SET time_zone = 'Asia/Calcutta';"
sudo -u postgres dropdb autograder_db
sudo -u postgres createdb -O autograder_app autograder_db 
psql -U autograder_app --dbname autograder_db -f database.pgsql
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser