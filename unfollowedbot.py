import cPickle as pickle
import time
import os
import sys

import twitter
import yaml

CONFIG = 'unfollowedbot.yaml'

INTERVAL = 120 # seconds

# limit the number of followers to 5000 (1 API call) to avoid rate limiting and getting 
# bottlenecked by a single user with too many followers
MAX_FOLLOW = 5000


def init_api():
  creds = yaml.load(open(CONFIG).read())
  creds['sleep_on_rate_limit'] = True
  print(str(creds))
  return twitter.Api(**creds)


def log(s):
  """ nohup doesn't show output unless flush is called """
  print(s)
  sys.stdout.flush()


def update_user(user, db, api):
  """ Perform update for a user (check for unfollows, send DM, block if too big
  Args:
    (User) user object
    
  Return:
    (int) number of unfollowers
    (list) set of current followers
  """
  
  unfollower_count = 0
  followers = []
  
  try:
    
    followers = api.GetFollowerIDs(user_id=user.id, total_count=MAX_FOLLOW)
    
    if len(followers) == MAX_FOLLOW:
      # block users that have too many followers.
      api.CreateBlock(user_id=user.id)
      log('\tblocked @'+user.screen_name)
    elif user.id in db:
      unfollowers = [f for f in db[user.id] if f not in followers]
      unfollower_count = len(unfollowers)
      # if there are any unfollowers, send a DM
      if unfollower_count > 0:
        users = api.UsersLookup(unfollowers)
        message = str(len(unfollowers)) + ' unfollower(s): ' +  ' '.join(['@'+f.screen_name for f in users])
        api.PostDirectMessage(message, user_id=user.id)
        log('\tDM\'d @'+user.screen_name)    
  except:
    pass

  return unfollower_count, followers


def main():
  
  db = {}
  if os.path.exists('db'):
    db = pickle.load(open('db'))
  
  api = init_api()
  
  last_daily = time.time()
  daily_count = 0

  while True:
    
    # update users on their unfollowers
    new_db = {}
    subscribers = api.GetFollowers(count=200)
    log(str(len(subscribers)) + ' subscribers')
    
    for s in subscribers:
      log('@'+s.screen_name)
      count, followers = update_user(s, db, api)
      new_db[s.id] = followers
      daily_count += count
      time.sleep(INTERVAL)
    
    db = new_db
    pickle.dump(db, open('db', w))
    
    # send the daily tweet
    if time.time() - last_daily > 60*60*24:
      last_daily = time.time()
      api.PostUpdate('Reported ' + str(daily_count) + ' unfollows today. Follow me to see who #unfollowed you!')
      daily_count = 0
      time.sleep(INTERVAL)


if __name__ == '__main__':
  main()

