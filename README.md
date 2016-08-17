# Birdbody
![Birdbody logo](https://github.com/magnusnissel/birdbody/blob/master/assets/birdbody_fb_profile.png)


Birdbody is a graphical interface (built on top of the tweepy module) for creating corpora of tweets. It can

- gather the most recent tweets by specified users
- download tweets from a list of Tweet IDs
- collect tweets from the Twitter live stream over a period of time.

Tweets are downloaded as JSON files and then converted to CSV for use with spreadsheet software (the JSON files are retained). Birdbody also allows you to

- combine multiple files 
- convert from CSV to plaintext files
- convert from CSV to XML files with some metadata attributes
- export a list containing all Tweet IDs from a file

Twitter does not allow you to share collections of full tweets. With Birdbody it is possible to instead create a list of Tweet IDs and share it. The list can then can be imported into Birdbody to recreate the collection via the "Tweets by ID" feature.


It was originally based on the tweet_dumper.py gist by Yanofsky (https://gist.github.com/yanofsky/5436496).

## Requirements
  * Python 3
  * tweepy

A  Windows (64bit) executable is available for each versioned release.

# Citing Birdbody

If you end up using Birdbody for published research, I would appreciate a reference. For version 1.0.2 (codename Albatross) this could look like


Nissel, Magnus. 2016. Birdbody 1.0.2 (Albatross). https://github.com/magnusnissel/birdbody


Here is a BibTex entry suggestion
```
@misc{magnus_nissel_2016,
  author       = {Magnus Nissel},
  title        = {Birdbody 1.0.2 (Albatross)},
  year         = 2016,
  url          = {https://github.com/magnusnissel/birdbody}
}
```

# License
GNU General Public License Version 3 (or later). See LICENSE file for more information.

# Using Birdbody
You can easily create your own multi-user corpus in CSV, XML and TXT format using the steps outlined below.

## Initial setup
In order to use birdbody you need to first create a Twitter app through https://apps.twitter.com.
This allows you to generate the four credentials required to access the Twitter API:
 
 * Customer key
 * Customer secret
 * Access key
 * Access secret

Add these in the "Settings" tab.

### Downloading tweets from users
Birdbody can download as many recent tweets of a user as Twitter allows (around 3000).

1. Go to "Tweets by users" tab.
2. Type in a list of screen names (or load a text file). One screen name per line, without the @ sign.
3. Click on "Download tweets" and wait.
5. Go to your user data folder (specified under "Settings") and navigate to tweets/csv
6. Open the .csv files with the program of your choice
7. If you want XML or plaintext files for use with concordancers, see "Conversion" below

### Streaming tweets
Birdbody can listen to the Twitter stream and collect tweets matching search strings.

1. Go to the "Stream tweets" tab.
2. Type in a number of search terms to listen for.
3. Optional: Specify a maximum number of tweets to collect.
4. Click on "Start streaming" to start and again to stop.
5. After streaming ends, Birdbody may take a while to convert the tweets to CSV.

There is a button for JSON-to-CSV conversion in streaming does not stop regularly. This could happen if the software or computer crashes / shuts down during long streaming sessions.

### Creating corpora
You can aggregate the CSV files to create larger collections.

1. Go to the "File management" tab.
2. Select multiple CSV files from the list box (SHIFT+Click or CTRL+Click).
3. Type in a filename  next to the "Combine files" button. (A generic name with timestamp will be used if empty).
4. Click on "Combine files" and wait.
5. The combined file(s) will appear in the tweets/csv folder and in the file list.

### Conversion to XML or plaintext ###
You can convert the CSV files into plaintext (just the tweet texts separated by empty lines) or XML files (metadata is stored in attributes of <tweet> nodes, which contain the tweet texts).

1. Go to the "File management" tab.
2. Select any number of CSV files.
3. Click on "Convert to .xml" or "Convert to .txt" and wait.
4. The files are stored in the tweets/xml or tweets/txt folders within your user data folder. 

### Sharing corpora
Twitter does not allow you to distribute the actual text corpus, but you can share all relevant Tweet IDs so that other people can recreate the corpus by downloading the tweets themselves (see "Tweets by ID" tab).

1. Go to the "File management" tab.
2. Select any number of CSV files.
3. Click on "Export list of Tweet IDs"
4. The ID list(s) will appear in the "tweet_ids" folder inside your data folder.

### Troubleshooting

#### 401
If you receive a 401 error, the most common cause is that your authentication __credentials are incorrect__. However, I have also seen that error 
while __streaming tweets__ when my computer's __local time was off__. So if "Tweets by users" still works, but streaming doesn't, then check the time settings
of your operating system.

#### 403, 420, 429
These errors can occur due to __rate limiting__. While Birdbody uses [tweepy's feature to sleep automatically when rate limited](http://docs.tweepy.org/en/v3.2.0/api.html#API) 
it is still possible to get theses errors because you are requesting too much data from Twitter at too fast a pace. There are a number of ways to avoid this including
working with several smaller lists of users/keywords instead of a single large one or by limiting the number of tweets gathered. However, in normal situations you simply
need to wait until you are no longer rate limited and often tweepy/Birdbody will do this automatically for you.

#### More information 
[Official Twitter error code documentation](https://dev.twitter.com/overview/api/response-codes)



## Command Line Interface
cli.py includes basic command line functionality for downloading tweets by users
```
usage: cli.py [-h]
              [--userfile FILENAME | --userpath PATH | --usernames [LIST [LIST ...]]]
              [--limit N] [--skip]

Command line interface to download tweets by specified users

optional arguments:
  -h, --help            show this help message and exit
  --userfile FILENAME   name of a file inside the user_data/screen_names
                        folder
  --userpath PATH       full path to a user list
  --usernames [LIST [LIST ...]]
                        a space-separated list of user names
  --limit N             only save N tweets per user
  --skip                skip if a user tweet file for this date already exists
  ```



## Changelog

### 2016-08-16
- removed appdirs dependency and switched to "user_data" inside the Birdbody folder as the data directory
- removed custom users paths
- added some 401 error explanations
- changed structure from package to simple script


