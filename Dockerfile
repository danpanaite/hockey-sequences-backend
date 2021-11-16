FROM python:3.10
RUN pip install pipenv
COPY . /src
WORKDIR /src
RUN pipenv install --system --deploy --ignore-pipfile
CMD ["python", "run.py"]