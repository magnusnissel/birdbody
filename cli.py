import argparse
import sys
import os
import datetime
import configparser
import worker

SCRIPT_PATH = os.path.dirname(os.path.realpath(sys.argv[0]))
USER_PATH = os.path.join(SCRIPT_PATH, "user_data")

def get_user_names_from_file(args):
    if args.user_path:
        list_path = args.user_path
    else:
        list_path = os.path.join(USER_PATH, "screen_names", args.user_file)
    try:
        with open(list_path, encoding="utf-8") as h:
            lines = h.readlines()
            lines = [l.strip() for l in lines if l]
    except IOError as e:
        raise(e)
    else:
        return lines

def get_credentials(config_path=os.path.join(USER_PATH, "settings.ini")):
    config = configparser.SafeConfigParser()
    config.optionxform = str
    config.read(config_path)
    ck = config['Credentials']['CustomerKey'].strip()
    cs = config['Credentials']['CustomerSecret'].strip()
    ak = config['Credentials']['AccessKey'].strip()
    acs = config['Credentials']['AccessSecret'].strip()
    return ck, cs, ak, acs

def download_user_tweets(args):
    if args.user_names:
        user_names = args.user_names
    else:
        user_names = get_user_names_from_file(args)

    if not user_names:
        print("No usernames found.")
    else:
        if args.skip:  # remove users for which tweet CSV files exist for today
            d = datetime.datetime.now().date()
            user_names = [u for u in user_names if not os.path.exists(os.path.join(USER_PATH, "tweets", "csv", 
                                                                                   "{}_{}_tweets.csv".format(u, d)))]

        num_users = len(user_names)
        if args.limit > 0:
            print("Getting up to {} tweets each for {} users.".format(args.limit, num_users))
        else:
            print("Getting tweets for {} users.".format(num_users))
            if args.limit < 0:  # just in case
                args.limit = 0

        ck, cs, *rest = get_credentials()
        worker.grab_tweets_from_users(USER_PATH, ck, cs, screen_names=user_names, tweet_limit=args.limit, conn=False)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Command line interface to download tweets by specified users')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--userfile", metavar="FILENAME", default="", dest="user_file", type=str,
                        help="name of a file inside the user_data/screen_names folder", action="store")
    group.add_argument("--userpath", metavar="PATH", default="", dest="user_path", type=str,
                        help="full path to a user list", action="store")
    group.add_argument("--usernames", metavar="LIST", default="", nargs = '*', dest="user_names", type=str,
                        help="a space-separated list of user names", action="store")
    parser.add_argument("--limit", metavar="N", default=0, type=int, dest="limit", action="store",
                        help="only save N tweets per user")
    parser.add_argument("--skip", dest="skip", default=False, help="skip if a user tweet file for this date already exists", action="store_true")
    
    
    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)
    else:
        if args.user_file or args.user_names or args.user_path:
            download_user_tweets(args)
        else:
            parser.print_help()
            sys.exit(0)

