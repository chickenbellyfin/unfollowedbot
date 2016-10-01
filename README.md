# unfollowedbot
Twitter bot that DM's users with lists of people that un-followed them.

Live at [@unfollowedbot](https://twitter.com/unfollowedbot)
- Users follow the bot to subscribe to follower tracking
- Bot will periodically DM user with a list of @usernames that un-followed them
- Bot will tweet out the total number of unfollows reported daily

### Dependencies
- python-twitter
- PyYAML

### Running
- Add OAuth creds to `unfollowedbot.yaml`
- run `python unfollowedbot.py`

### Limitations
- blocks any users with 5000 or more followers
- Users are spaces out at 2-minute intervals to avoid API rate limiting
