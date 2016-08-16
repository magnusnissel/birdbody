# birdbody
A graphical interface for creating twitter corpora. It can gather the most recent tweets of specified users. It is also able download tweets from a list of Tweet IDs (and generate this list for downloaded tweets). Finally, it can also collect tweets from the Twitter live stream over a period of time.

Originally based on the tweet_dumper.py gist by Yanofsky (https://gist.github.com/yanofsky/5436496).

## Usage notes
You can easily create your own multi-user corpus in CSV, XML and TXT format using the steps outlined below.

### Initial setup
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

## Requirements
  * Python 3
  * tweepy

## Windows
A  Windows (64bit) executable is now available.

Please note that I can not guarantee that the Windows binary will always be up to date, but I will do my best to update it
whenever something important happens in this repository. 

## Known issues 
Especially under Windows there are still issues when switching windows (or tabs inside Birdbody) during complex operations. 
Sometimes waiting will resolve this, but it can also crash the app. Until I know how to fix this I suggest minimal
interface interactions while downloading/streaming tweets or converting files.
This seems to occur more frequently with the Windows binary than with the Python script, but I have only anecdotal evidence.

## Troubleshooting

### 401
If you receive a 401 error, the most common cause is that your authentication __credentials are incorrect__. However, I have also seen that error 
while __streaming tweets__ when my computer's __local time was off__. So if "Tweets by users" still works, but streaming doesn't, then check the time settings
of your operating system.

## 403, 420, 429
These errors can occur due to __rate limiting__. While Birdbody uses [tweepy's feature to sleep automatically when rate limited](http://docs.tweepy.org/en/v3.2.0/api.html#API) 
it is still possible to get theses errors because you are requesting too much data from Twitter at too fast a pace. There are a number of ways to avoid this including
working with several smaller lists of users/keywords instead of a single large one or by limiting the number of tweets gathered. However, in normal situations you simply
need to wait until you are no longer rate limited and often tweepy/Birdbody will do this automatically for you.

## More information 
[Official Twitter error code documentation](https://dev.twitter.com/overview/api/response-codes)

## LICENSE
GNU General Public License Version 3 (or later). See LICENSE file for more information.

## Changelog

### 2016-08-16
- removed appdirs dependency and switched to "user_data" inside the Birdbody folder as the data directory
- removed custom users paths
- added some 401 error explanations
- changed structure from package to simple script

## Citation
If you end up using Birdbody for published research, I would appreciate a reference along the lines of

Nissel, Magnus. 2016. Birdbody. Software (GPL). https://github.com/magnusnissel/birdbody

