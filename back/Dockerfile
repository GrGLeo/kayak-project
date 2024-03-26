FROM python:3.10.6-slim

WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y cron
RUN pip install --no-cache-dir -r requirements.txt
RUN mv cronjob /etc/cron.d/cronjob
RUN chmod 0644 /etc/cron.d/cronjob
RUN crontab /etc/cron.d/cronjob

CMD ["cron", "-f"]