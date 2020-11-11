FROM python:3.6.10-alpine3.10

RUN pip3 install pygithub==1.47

COPY check_OCA.py /check_OCA.py
COPY constants.py /constants.py

RUN chmod +x /check_OCA.py

ENTRYPOINT ["/check_OCA.py"]