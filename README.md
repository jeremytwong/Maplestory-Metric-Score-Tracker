# MapleStory Score Tracking Bot

This bot is designed to track player scores for each guild for the popular MMORPG, MapleStory.

## Features

* Track player scores
* Update scores in real-time
* Provide leaderboards

## Installation

1. Clone this repository
2. Navigate to the directory where the `metrictracker.py` file is located
3. Install the required Python packages with the command `pip install -r requirements.txt`
4. You need a Google service account with access to the Google Sheets API. Follow the instructions [here](https://developers.google.com/workspace/guides/create-service-account) to create one and download the JSON key file.
5. Place the JSON key file in the same directory as `metrictracker.py` and rename it to `service_account.json`.
6. Run the script with the command `python metrictracker.py`

## Configuration

Before using the bot, you need to make a few edits to the code:

1. **Guild Name**: Go to line 285 and replace the placeholder with your guild's name.
2. **Sheet Name**: Go to line 17 and replace the placeholder with the name of your sheet.
3. **Emoji ID**: Go to line 297 and replace the placeholder with your emoji ID.
4. **Two Emoji IDs**: Go to line 322 and replace the two placeholders with your two emoji IDs.

After making these changes, you should be able to use the bot with your own settings.