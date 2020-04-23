#! /bin/bash

sshpass -p $SSH_PASSWORD ssh -o 'IdentitiesOnly yes' root@45.132.242.190 """

echo ''
echo '### ACCESSING DIRECTORY ========================================================================================'
echo ''

echo $APP_DIRECTORY ; cd $APP_DIRECTORY

echo ''
echo '### CHECKOUT BRANCH AND UPDATE ================================================================================='
echo ''

git checkout $BRANCH ; git pull

echo ''
echo '### ACTIVATE ENV AND INSTALL REQUIREMENTS ======================================================================'
echo ''

source env/bin/activate
pip install -r requirements.txt

echo ''
echo '### COLLECTSTATIC =============================================================================================='
echo ''

python manage.py collectstatic --noinput

echo ''
echo '### MIGRATE ===================================================================================================='
echo ''

python manage.py migrate

echo ''
echo '### RESTART SERVICES ==========================================================================================='
echo ''

sudo service $SERVICE_GUNICORN restart

echo ''
echo '### VERIFY SERVICES ============================================================================================'
echo ''

sudo service $SERVICE_GUNICORN status
"""
