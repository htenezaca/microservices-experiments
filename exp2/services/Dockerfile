FROM python:3.9-buster
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt
# Para hacer debugging interno a la imagen
# CMD ["tail", "-f", "/dev/null"]
CMD [ "flask", "run", "--host", "0.0.0.0" ]
