gunicorn --bind 127.0.0.1:5000 app:app & APP_PID=$!
sleep 5
echo start app
python3 test.py
APP_CODE=$?
sleep 5
echo $APP_PID
kill -TERM $APP_PID
exit $APP_CODE
