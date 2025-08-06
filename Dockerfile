# Use an official Python runtime as a parent image
FROM python:3.11.5

# Build variables.
ENV DEBIAN_FRONTEND noninteractive

# Install Microsoft SQL Server requirements.
ENV ACCEPT_EULA=Y
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        curl \
        gcc \
        g++ \
        gnupg \
        unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends --allow-unauthenticated msodbcsql17 mssql-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Upgrade pip and install requirements.
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /requirements.txt


# Copy all files to /app directory and move into directory.
COPY . /app
WORKDIR /app

# Set the PATH environment variable.
ENV PATH="$PATH:/opt/mssql-tools/bin"

Expose 8023

# Specify the command to run when the container starts.
# Adjust the command as per your requirements.
ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8023"]

