FROM python:3.11-slim-buster

RUN mkdir /usr/src/app
RUN mkdir /usr/src/app/frontend

# install node js
RUN apt-get update && \
    apt-get install -y nodejs && \
    apt-get install -y npm  && \
    apt-get install -y cron

RUN apt-get install -y libmagic1

# configure typescript
RUN npm install -g typescript

COPY . /usr/src/app
COPY ./frontend/public/* /usr/src/app/frontend/public/
COPY ./frontend/views/* /usr/src/app/frontend/views/
COPY ./cronjob /etc/cron.d/cronjob
COPY ./.env /usr/src/app/.env

# Start the cron servive
RUN chmod 0644 /etc/cron.d/cronjob
RUN touch /var/log/cron.log
RUN crontab /etc/cron.d/cronjob
RUN service cron start

WORKDIR /usr/src/app

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

EXPOSE 8000

# Set the entrypoint script to run on container start
RUN chmod +x /usr/src/app/entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

CMD [ "python3", "app.py"]