sleep 2
# do not need it because  fastApi make migrations
# echo Run db upgrade
# poetry run flask db upgrade
# echo Run app
# flask run -h 0.0.0.0
echo Run app server
poetry run gunicorn -w 4 -b 0.0.0.0 'wsgi:app'