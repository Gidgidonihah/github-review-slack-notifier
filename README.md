# github-slack-notifier

This is a very basic flask server using [Flask-Hookserver](https://github.com/nickfrostatx/flask-hookserver) to respond
to custom github webhooks.

![Coverage Status](https://coveralls.io/repos/github/DobaTech/github-review-slack-notifier/badge.svg?branch=master)
![Build Status](http://ci.projectthanos.com/api/badges/DobaTech/github-review-slack-notifier/status.svg)


## What it does

When a pull request hook is received, the app does the following things:

1. Check the action on the PR webook. Only continues if it is a review request
1. Look up all slack users
1. Attempt to match the github username to a slack username
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

First, create a custom slack bot. Get the API Key.

Next, get a Github API Key. This is needed to lookup a user's full name.

Next, create a custom github webhook on your repo or organization. The pull request event is currently the only event
that matters. *Make note of the secret* Point the URL to where you will be hosting your code. Make sure to include
`/hooks`. e.g. `https://my-github.example.com/hooks`

Finally, host the code on a server that github can reach. You will need the following environment variables:

```
export SLACK_BOT_TOKEN='<YOUR SLACKBOT TOKEN>'
export GITHUB_WEBHOOKS_KEY='<YOUR WEBHOOK SECRET'
export GITHUB_API_TOKEN='<YOUR GITHUB API TOKEN>'
export GITHUB_API_USER='<YOUR GITHUB API USERNAME>'
export DEFAULT_NOTIFICATION_CHANNEL='#<YOUR DEFAULT SLACK CHANNEL>'
```


## TODO

* The slack user lookup is not cached.
* Perhaps would be better as an app that stores the github/slack username link.
* The matching is imprecise and would probably break with two people of the same name.
