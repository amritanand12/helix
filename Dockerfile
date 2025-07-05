FROM python:3.11-slim

#Upgrade pip
RUN python -m pip install --upgrade pip

#set up a working directory
WORKDIR /app

#Copy requiements and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#copy all application files
COPY . /app

#Tell uvicorn to start spin up our code, which will be running inside the container now
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9758"]

