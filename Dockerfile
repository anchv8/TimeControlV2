FROM python:3.11
WORKDIR .
COPY requirements requirements
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements
RUN chmod 755 .
COPY . .
CMD ["python", "__main__.py"]
