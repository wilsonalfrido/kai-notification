FROM python:3.11.9

WORKDIR /home/bot_api

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

# RUN mkdir -p /home/bot_api/driver/linux

#Set timezone -> https://dev.to/bitecode/set-timezone-in-your-docker-image-d22
RUN apt-get update && \
    apt-get install -yq tzdata && \
    ln -fs /usr/share/zoneinfo/Asia/Jakarta /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

# # Get chrome
# RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
# RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
# RUN apt-get -y update

# # Install
# RUN apt-get install -y google-chrome-stable
# RUN apt-get install -yqq unzip

# RUN MAJOR_VERSION=$(google-chrome --version | grep -oP '(?<=Google Chrome )\d+' | head -1)
# RUN CHROMEDRIVER_VERSION=$(curl -sS https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$MAJOR_VERSION)
# RUN wget -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/$(curl -sS https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$(google-chrome --version | grep -oP '(?<=Google Chrome )\d+' | head -1))/linux64/chromedriver-linux64.zip 
# RUN unzip /tmp/chromedriver.zip -d /home/bot_api/driver/linux/

# ENV DISPLAY=:99


CMD ["python3","main.py"]

