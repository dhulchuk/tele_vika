# Vika


Telegram bot on AWS Lambda.


## Environment variables

```
AWS_ACCESS_KEY_ID  # from aws console
AWS_SECRET_ACCESS_KEY  # from aws console
VIKA_TOKEN  # from BotFather
```
```
npm i -g serverless
npm install
serverless deploy
```
```
VIKA_URL  # from deploy output
```
```bash
brew install httpie  # or use curl
http POST https://api.telegram.org/bot$VIKA_TOKEN/setWebhook url=$VIKA_URL
```


