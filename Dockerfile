FROM python:3.10.11

# Set the API_URL environment variable
ENV API_URL=http://localhost:5069/api/
ENV CRON_SCHEDULE_TIME="30 1 * * * TZ="Asia/Ho_Chi_Minh"

# Set the working directory
WORKDIR /app

# Copy the Python script into the container
COPY main.py /app/
COPY requirements.txt /app/

# Install any dependencies if needed
RUN pip install -r requirements.txt

RUN apt-get update && apt-get -y install cron

RUN mkdir /var/cronjob/

RUN echo "Extract log" >> /var/log/extract.log

CMD cron \
    && echo "$CRON_SCHEDULE_TIME /usr/local/bin/python /app/main.py --url=$API_URL >> /var/log/extract.log" > /var/cronjob/extract-crontab \
    && crontab /var/cronjob/extract-crontab \
    && tail -f /var/log/extract.log


