import os
import datetime
import csv
import tweepy
import json

HAS_PANDAS = True
try:
    import pandas as pd
except ImportError:
    HAS_PANDAS = False


class BirdBodyListener(tweepy.StreamListener):
    """ 
    Copied from tweepy/streaming.py, then modified.
    Tweets are originally saved in the json they come in to avoid
    delays due to processing, then converted to the csv format when
    streaming is over
    """
    def __init__(self, json_path, max_tweets, conn=None):
        super().__init__()
        self.json_path = json_path
        self.conn = conn
        self.num_tweets = 0
        self.max_tweets = max_tweets

    def on_data(self, data):
        with open(self.json_path,'a') as handler:
            handler.write(data)
        self.num_tweets += 1
        m = self.num_tweets % 25  # notify every 25 tweets
        if m == 0 and self.num_tweets > 0:
            if self.max_tweets > 0:
                msg = "Collected {}/{} tweets so far.".format(self.num_tweets, self.max_tweets)
            else:
                msg = "Collected {} tweets so far.".format(self.num_tweets)
                
            if self.conn:
                self.conn.send(msg)
            else:
                print(msg)
        if self.max_tweets > 0 and self.num_tweets >= self.max_tweets:
            if self.conn:
                self.conn.send("Reached target number of tweets.")
            else:
                print("Reached target number of tweets.")
            return False
        else:
            return True

    def on_error(self, status):
        if status == 420:  # Rate Limited
            #returning False in on_data disconnects the stream
            if self.conn:
                self.conn.send("Rate limited reached. Will stop streaming.", ts=True)
            else:
                print("Rate limit reached. Will stop streaming.")
            return False
        else:
            if self.conn:
                self.conn.send(status)
            else:
                print(status)
            return True

def stream_tweets(data_path, fn, consumer_key, consumer_secret, access_key, access_secret, 
                  search_str_list, max_tweets, conn=None):
    json_dir = os.path.join(data_path, "tweets", "json")
    try:
        os.makedirs(json_dir)
    except OSError as e:
        if e.errno != 17:
            raise()
    json_path = os.path.join(json_dir, "{}.json".format(fn))
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    stream_listener = BirdBodyListener(json_path, max_tweets, conn)
    stream = tweepy.Stream(auth = api.auth, listener=stream_listener)
    stream.filter(track=search_str_list, async=False)


def grab_tweets_by_ids(data_path, consumer_key, consumer_secret, access_key, access_secret, 
                       tweet_ids, filename, conn=None):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    start_time = datetime.datetime.now()
    id_tweets = []
    id_lists =[tweet_ids[i:i+100] for i in range(0, len(tweet_ids), 100)] # up to 100 per attempt
    for id_list in id_lists:
        rl_status = api.rate_limit_status()['resources']['statuses']['/statuses/lookup']
        remaining = int(rl_status['remaining'])
        if remaining < 1:
            msg = "Waiting until Twitter rate limit is reset ..."
            if conn:
                conn.send(msg)
            else:
                print(msg)
        try:
            new_tweets = api.statuses_lookup(id_list, include_entities=True)
        except tweepy.error.TweepError as e:
            if conn:
                conn.send(e)
            else:
                print(e)
        else:
            id_tweets += new_tweets
            msg = "Downloaded {} out of {} tweets so far ...".format(len(id_tweets),
                                                                     len(tweet_ids))
            if conn:
                conn.send(msg)
            else:
                print(msg)
        if HAS_PANDAS:
            pd_id_tweets_to_csv(data_path, filename, id_tweets, conn)
        else:
            id_tweets_to_csv(data_path, filename, id_tweets, conn)
        
 
def grab_tweets_from_users(data_path, consumer_key, consumer_secret, access_key, access_secret, 
                        screen_names, conn=None):
    # used to be user level authentication, app authentication seems better for this task
    auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    start_time = datetime.datetime.now()
    for sn in screen_names:
        if conn:
            msg = "Getting tweets for {} ...".format(sn)
            conn.send(msg)
        user_tweets = grab_tweets_for_user(api, sn, conn)
        if HAS_PANDAS:
            pd_user_tweets_to_csv(data_path, user_tweets, sn, conn)
        else:
            user_tweets_to_csv(data_path, user_tweets, sn, conn)
        msg = "Done with {}!".format(sn)
        if conn:
            conn.send(msg)
        else:
            print(msg)

def grab_tweets_for_user(api, screen_name, conn=None):
    #Twitter only allows access to a users most recent 3240 tweets with this method
    user_tweets = []  
    #make initial request for most recent tweets (200 is the maximum allowed count)
    rl_status = api.rate_limit_status()['resources']['statuses']['/statuses/user_timeline']
    remaining = int(rl_status['remaining'])
    if remaining < 1:
        msg = "Waiting until Twitter rate limit is reset ..."
        if conn:
            conn.send(msg)
        else:
            print(msg)
    try:
        new_tweets = api.user_timeline(screen_name = screen_name, count=200)
    except tweepy.error.TweepError as e:
        if conn:
            conn.send(e)
        else:
            print(e)
    else:
        #save most recent tweets
        user_tweets += new_tweets
        #save the id of the oldest tweet less one
        try:
            oldest = user_tweets[-1].id - 1
        except IndexError:
            oldest = None
        #keep grabbing tweets until there are no tweets left to grab
        while len(new_tweets) > 0:
            #all subsequent requests use the max_id parameter to prevent duplicates
            new_tweets = api.user_timeline(screen_name = screen_name,count=200,
                                                max_id=oldest)
            #save most recent tweets
            user_tweets.extend(new_tweets)
            #update the id of the oldest tweet less one
            oldest = user_tweets[-1].id - 1
            msg = "{} tweets downloaded for {} so far.".format(len(user_tweets), screen_name)
            if conn:
                conn.send(msg)
            else:
                print(msg)
    return user_tweets

def tweets_to_dict_list(tweets, from_json=False):
    today = datetime.datetime.now().date()
    tweet_dict_list = []
    if from_json:  # when tweets are created via json module vs. from tweepy api call
        for tweet in tweets:
            tweet = json.loads(tweet)
            t = {}
            t["TWEET_ID"] = tweet["id_str"]
            t["CREATED"] = tweet["created_at"] 
            t["TEXT"] = tweet["text"]
            if tweet["in_reply_to_user_id"]:
                t["IS_REPLY"] = True
            else:
                t["IS_REPLY"] = False
            t["LANGUAGE"] = tweet["lang"]
            t["SCREEN_NAME"] = tweet["user"]["screen_name"]
            t["NAME"] = tweet["user"]["name"]
            t["LOCATION"] = tweet["user"]["location"]
            t["VERIFIED"] = tweet["user"]["verified"]
            t["ACCOUNT_CREATED"] = tweet["user"]["created_at"]
            t["COLLECTED"] = today
            tweet_dict_list.append(t)
    else:
        for tweet in tweets:
            t = {}
            t["TWEET_ID"] = tweet.id_str
            t["CREATED"] = tweet.created_at 
            t["TEXT"] = tweet.text
            if tweet.in_reply_to_user_id:
                t["IS_REPLY"] = True
            else:
                t["IS_REPLY"] = False
            t["LANGUAGE"] = tweet.lang
            t["SCREEN_NAME"] = tweet.user.screen_name
            t["NAME"] = tweet.user.name
            t["LOCATION"] = tweet.user.location
            t["VERIFIED"] = tweet.user.verified
            t["ACCOUNT_CREATED"] = tweet.user.created_at
            t["COLLECTED"] = today
            tweet_dict_list.append(t)
    return tweet_dict_list


def pd_id_tweets_to_csv(data_path, filename, tweets, conn=None, add_date_to_fn=True):
    tweet_dict_list = tweets_to_dict_list(tweets)
    dn = os.path.join(data_path, "tweets", "csv")
    df = pd.DataFrame.from_dict(tweet_dict_list)
    try:
        os.makedirs(dn)
    except OSError as e:
        if e.errno != 17:
            raise()
    if not add_date_to_fn:
        fp = os.path.join(dn, "{}.csv".format(filename))  
    else:
        today = datetime.datetime.now().date()
        fp = os.path.join(dn, "{}_{}.csv".format(filename, today))
    if len(df.index) > 0:
        df.to_csv(fp)


def id_tweets_to_csv(data_path, filename, tweets, conn=None, add_date_to_fn=True):    
    fields = ["TWEET_ID", "CREATED", "TEXT", "IS_REPLY", "LANGUAGE", "SCREEN_NAME", "NAME", "LOCATION", 
              "VERIFIED", "ACCOUNT_CREATED", "COLLECTED"]
    tweet_dict_list = tweets_to_dict_list(tweets)
    if len(tweet_dict_list) > 0:
        dn = os.path.join(data_path, "tweets", "csv")
        try:
            os.makedirs(dn)
        except OSError as e:
            if e.errno != 17:
                raise()
        if not add_date_to_fn:
            fp = os.path.join(dn, "{}.csv".format(filename))  
        else:
            today = datetime.datetime.now().date()
            fp = os.path.join(dn, "{}_{}.csv".format(filename, today))
        with open(fp, 'w', newline='', encoding='utf8') as handler:
            writer = csv.DictWriter(handler, fieldnames=fields, dialect="excel")
            writer.writeheader()
            writer.writerows(tweet_dict_list)


def dict_list_to_csv(dict_list, csv_path):
    if len(dict_list) > 0:
        fields = sorted(list(dict_list[0].keys()))
        with open(csv_path, "w", newline="", encoding="utf-8") as handler:
            writer = csv.DictWriter(handler, fieldnames=fields, dialect="excel")
            writer.writeheader()
            writer.writerows(dict_list)

def pd_dict_list_to_csv(dict_list, csv_path):
    df = pd.DataFrame.from_dict(dict_list)
    if len(df.index) > 0:
        df.to_csv(csv_path)

def pd_user_tweets_to_csv(data_path, tweets, screen_name, conn=None, add_date_to_fn=True):
    tweet_dict_list = tweets_to_dict_list(tweets)
    dn = os.path.join(data_path, "tweets", "csv")
    df = pd.DataFrame.from_dict(tweet_dict_list)
    try:
        os.makedirs(dn)
    except OSError as e:
        if e.errno != 17:
            raise()
    if not add_date_to_fn:
        fp = os.path.join(dn, "{}_tweets.csv".format(screen_name))  
    else:
        today = datetime.datetime.now().date()
        fp = os.path.join(dn, "{}_{}_tweets.csv".format(screen_name, today))
    if len(df.index) > 0:
        df.to_csv(fp)

def user_tweets_to_csv(data_path, tweets, screen_name, conn=None, add_date_to_fn=True):    
    fields = ["TWEET_ID", "CREATED", "TEXT", "IS_REPLY", "LANGUAGE", "SCREEN_NAME", "NAME", "LOCATION", 
              "VERIFIED", "ACCOUNT_CREATED", "COLLECTED"]
    tweet_dict_list = tweets_to_dict_list(tweets)
    if len(tweet_dict_list) > 0:
        dn = os.path.join(data_path, "tweets", "csv")
        try:
            os.makedirs(dn)
        except OSError as e:
            if e.errno != 17:
                raise()
        if not add_date_to_fn:
            fp = os.path.join(dn, "{}_tweets.csv".format(screen_name))  
        else:
            fp = os.path.join(dn, "{}_{}_tweets.csv".format(screen_name, today))
            today = datetime.datetime.now().date()
        with open(fp, 'w', newline='', encoding='utf8') as handler:
            writer = csv.DictWriter(handler, fieldnames=fields, dialect="excel")
            writer.writeheader()
            writer.writerows(tweet_dict_list)
            msg = "Saved tweets to {}.".format(fp)
            if conn:
                conn.send(msg)
            else:
                print(msg)

