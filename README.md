# github-slack-notifier

This is a very basic flask server using [Flask-Hookserver](https://github.com/nickfrostatx/flask-hookserver)
that responds to custom github webhooks.

[![Coverage Status](https://coveralls.io/repos/github/CruxConnect/github-review-slack-notifier/badge.svg?branch=master)](https://coveralls.io/github/CruxConnect/github-review-slack-notifier)
[![Build Status](https://drone.cruxconnect.com/api/badges/CruxConnect/github-review-slack-notifier/status.svg)](https://drone.cruxconnect.com/CruxConnect/github-review-slack-notifier/)


## What it does

When a pull request hook is received, the app does the following things:

1. Check the action on the PR webook. Only continues if it is a review request or assignment
1. Look up all slack users
1. Attempt to match the github username to a slack username or displayname
1. If there is no match, it will retrieve the github user's full name via the API and attempt to match it to a slack full name.
1. If there is no matched username, it will use a generic phrase, and post the message in the default channel
1. If a matched slack username is found, a message will be sent to the matched user only.
1. The message will contain:
  * Github Repo & PR #
  * A link to the PR
  * PR Title and description
  * The author of the PR
  * A random [octocat](http://octodex.github.com) (because why not?)

## Setup

First, [create a custom slack bot](https://get.slack.help/hc/en-us/articles/115005265703-Create-a-bot-for-your-workspace#create-a-bot).
Save the API Key.

Next, [create a Github Personal Access Token](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/).
This used for basic auth needed to lookup a user's full name over the api.

Next, [create a custom github webhook](https://developer.github.com/webhooks/creating/) on your repo or organization.
The webhook should be defined at the highest level for which you would like notifications.
If you want notifications on a single repo, set it up on that repo.
If you would like it for all repos on an organization, create the webhook on the organization.
The pull request event is currently the only event that matters.
*Make note of the secret*. You will need to use this as an environment variable.
Point the URL to where you will be hosting your code.
Make sure to include `/hooks`. e.g. `https://my-github.example.com/hooks`

Finally, host the code on a server that github can reach.
You will need the following environment variables:

```
SLACK_BOT_TOKEN='<YOUR SLACKBOT TOKEN>'
GITHUB_WEBHOOKS_KEY='<YOUR WEBHOOK SECRET>'
GITHUB_API_TOKEN='<YOUR GITHUB API TOKEN>'
GITHUB_API_USER='<YOUR GITHUB API USERNAME>'
DEFAULT_NOTIFICATION_CHANNEL='#<YOUR DEFAULT SLACK CHANNEL>' # Fallback channel where messages will appear when no user found
IGNORED_USERS='<IGNOREDUSERNAME>,<ANOTHER_IGNORED_USERNAME>' # Actions initiated by these users will be ignored
```

## Using the Docker image

You can use the [prebuilt Docker image](https://hub.docker.com/r/gidgidonihah/github-review-slack-notifier/) to run the server. Be sure to inject the appropriate env vars when starting up the container.

## TODO

* Notification of review completion
* Cache the slack user lookup to remove needless api calls.
* The name matching is imprecise and would probably break with two people of the same name.
* Would be better as an oauth app that stores the github/slack username link.
* Improve the readme (provide better, more explicit setup steps)
