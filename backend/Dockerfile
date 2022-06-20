FROM python:3.7-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt --no-cache-dir
RUN chmod ugo+x entrypoint.sh
CMD sh entrypoint.sh

