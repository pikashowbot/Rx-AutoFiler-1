
# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

FROM python:3.10.8-slim-buster

# Update and install necessary packages
RUN apt update && apt upgrade -y && \
    apt install -y git

# Copy requirements file
COPY requirements.txt /requirements.txt

# Install Python dependencies
RUN pip3 install -U pip && pip3 install -U -r /requirements.txt

# Create working directory for the bot
RUN mkdir /Rx-AutoFiler2
WORKDIR /Rx-AutoFiler2

# Copy the start script and ensure Unix line endings
COPY start.sh /start.sh
RUN sed -i 's/\r$//' /start.sh

# Make the start.sh script executable
RUN chmod +x /start.sh

# Define the default command
CMD ["/start.sh"]
