# Heikin-Ashi, Hull Moving Average Concavity, and EMA Trend Alert

This repository contains a Python script and a GitHub Actions workflow for tracking several trend indicators of a ticker. It calculates smoothed Heikin-Ashi candles, Hull Moving Average, 50 and 200 day exponential moving averages, and sends an email notification when conditions are met, with a state-tracking feature to ensure notifications are sent only on state changes.

## Features

- **Automated Updates**: Automated daily calculations for select trend indicators using GitHub Actions.
- **Stateful Email Notifications**: Sends an email notification only when the state changes.
- **Test Email Functionality**: Ability to trigger a test email to verify the setup.

## Setup and Configuration

### Prerequisites

- Python 3.x
- A GitHub account
- SMTP server credentials for sending emails (configured for Gmail)


### Configuring GitHub Secrets

Set up the following secrets in your GitHub repository for the email functionality:

- `SENDER_EMAIL`: Your email address for sending notifications.
- `SENDER_PASSWORD`: Your email password or app-specific password.
- `RECEIVER_EMAIL`: The email address to receive notifications.

### Usage

The script is primarily designed for automatic execution through GitHub Actions. It can be manually run for testing: 
```
python alert.py
```

Additionally, setup state.txt and last_seven_days.csv (can be empty, just needs to have these filenames) so that Github Actions will be able to push changes to these files.

### GitHub Actions Workflow

The `.github/workflows/main.yml` file schedules the workflow to run at close in Eastern Time and allows manual triggering for sending a test email or checking the state.

### State Tracking

The script tracks the state of the last update in a file named `state.txt`. It ensures that email notifications are sent only when the state changes.

### Sending a Test Email

Manually trigger the workflow in GitHub Actions with the `workflow_dispatch` event, and set `sendTestEmail` to `true` for sending a test email.
