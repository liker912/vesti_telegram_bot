# Vesti Telegramm Bot
Got latest news from Vesti Rss channel and publish it to Telegra.ph and specific Telegram Channel

## Requirements:
!!! Docker should be install on server !!!

## Installation
Make git clone to server and run install.sh

Put BOT_TOKEN, CHANNEL_ID and MONITORING_CHANNEL_ID

## Run
Add to CRON job script run.sh

Example for each 30 min:
````
*/22 * * * * cd /path/to/repo/ && run.sh
````



