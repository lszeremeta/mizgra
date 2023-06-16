FROM python:3.11-slim
LABEL maintainer="Łukasz Szeremeta <l.szeremeta.dev+mmlkg@gmail.com>"
WORKDIR /app
# Copy the project files into the docker image (see .dockerignore)
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT [ "python", "-m", "mizgra" ]