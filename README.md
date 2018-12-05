# Slack Remind All

set a reminder for all users in a channel directly using a single command

## Requirements

* python 3.5+
* (optional) ngrok

## Installation

* clone the repo `git clone https://github.com/grzegorznowak/slack-remind-all.git`
* setup virtualenv: `virtualenv pyenv -p python3.6.7`
* activate venv: `. pyenv/bin/activate`
* `pip install -f requirements.txt`

### Running on dev

* (when behind a proxy) start your `ngrok` instance first
```
ngrok http 3000
```
* start the flask server
```
SLACK_SIGNING_SECRET={{ slack_remind_all_secret }} \
SLACK_OAUTH_TOKEN={{ slack_remind_all_oauth }} \
python {{ slack_remind_all_location }}/slack_remind_all/server.py
```

by default the app listens on `port 3000`, and it's currently fixed, but you can change that with a pinch of python.


## Provisioning on a server/container
see [Provisioning instructions](provision/README.md)

please note: provisioned service is exposed via http on a container's port, so need a SSL terminating proxy to function best
  
### @TODO:

* proper CI, test-coverage for the python part, shiny badges, etc. We all love those!
* **standalone** cross-workspace app on own server **(but only if folks actually need it!)**


## Sponsored by

##### [Kwiziq.com](https://www.kwiziq.com) - The AI language education platform
##### [Spottmedia.com](http://www.spottmedia.com) - Technology design, delivery and consulting


#### Author Information

python, slack & shell coding by [Grzegorz Nowak](https://www.linkedin.com/in/grzegorz-nowak-356b7360/)