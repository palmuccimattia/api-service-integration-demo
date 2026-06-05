# Base image AWS Lambda Python 3.11
FROM public.ecr.aws/lambda/python:3.11

# Copia requirements e installa le dipendenze
COPY requirements.txt ./
RUN pip install --platform manylinux2014_x86_64 --only-binary=:all: -r requirements.txt --target .
ENV PYTHONPATH=/var/task

# Copia il codice Lambda
COPY . .

# Imposta l'handler per Lambda
CMD ["main.lambda_handler"]