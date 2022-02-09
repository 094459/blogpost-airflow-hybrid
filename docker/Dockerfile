FROM  public.ecr.aws/docker/library/python:latest

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

#CMD [ "python3", "app/read-data-q.py"]
ENTRYPOINT [ "python3", "app/read-data-q.py" ]