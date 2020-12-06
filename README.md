# Discord Bot
A simple Discord bot written in Python using the discord.py library.

## Features and Commands
- Music Commands
  - Voice Channel:
    - `.join .leave`
  - Song Queue:
    - `.add .remove .removefront .songlist .autoplay`
  - Song Control:
    - `.play .pause .resume .skip .volume`
- 8ball: `.8ball`
- Latency: `.ping`
- Bot Status Display

## Download
```
$ git clone https://github.com/RichardVN/discord-bot.git
$ cd discord-bot
$ python3 -m venv myenv
$ source myenv/bin/activate
$ pip3 install -r requirements.txt
```

## Configuration
### Setting up Credentials File
1. Go to `discord.com/developers/applications`
2. Select the discord application designated for your bot
3. Select the Bot tab in the side menu and view your token
4. Rename `credentials.py.example` to `credentials.py` and fill out your bot token value
   - **DO NOT PUBLISH YOUR BOT TOKEN PUBLICLY. IF THIS HAPPENS, RESET TOKEN ON DISCORD PAGE**
    ```
    BOT_TOKEN = "Your Discord bot token here"
    ```
### Invite Bot to Desired Server
1. Go to `discord.com/developers/applications`
2. Select the discord application designated for your bot
3. Select desired scopes using checkboxes
4. Generate a OAuth2 URL
5. Go to URL and authorize bot permissions

## Run the Bot 
In `discord-bot` project directory: `$ python3 bot.py`
The bot should now be online on any server it has joined. Enjoy!
