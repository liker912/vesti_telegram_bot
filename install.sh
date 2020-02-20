#!/usr/bin/env bash

echo "Installation ynet bot start"
if [ ! -f ".env" ]; then
  touch .env
  read -p "Enter bot API TOKEN : " BOT_TOKEN
  read -p "Enter channel_id with @ : " CHANNEL_ID
  read -p "Enter ,monitoring channel_id with @ : " MONITORING_CHANNEL_ID

  URL_RSS="https://www.vesty.co.il/3rdparty/mobile/rss/vesty/13229/"
  DELAY_TIME="300"

  echo "URL_RSS"='"'$URL_RSS'"' >> .env
  echo "BOT_TOKEN"='"'$BOT_TOKEN'"' >> .env
  echo "CHANNEL_ID"='"'$CHANNEL_ID'"' >> .env
  echo "MONITORING_CHANNEL_ID"='"'$MONITORING_CHANNEL_ID'"' >> .env
  echo "DELAY_TIME"='"'$DELAY_TIME'"' >> .env
fi

docker-compose build vesti
echo "Instalation finish sucessfully"
