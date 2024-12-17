# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install cpulimit
RUN apt-get update && apt-get install -y cpulimit

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Run the scheduler script with nice and cpulimit
CMD ["sh", "-c", "cpulimit -l 20 -- nice -n 10 python ./scheduler/scheduler.py"]
