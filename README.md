# birdbody
A graphical interface for creating twitter corpora. Still very much a work in progress.
Based around the tweet_dumper.py gist by Yanofsky (https://gist.github.com/yanofsky/5436496)

## Usage notes ##

### Initial setup ###
In order to use birdbody you need to first create a Twitter app through https://apps.twitter.com.
This allows you to generate the four credentials required to access the Twitter API:
 
 * Customer key
 * Customer secret
 * Access key
 * Access secret

Add these in the "Settings" tab.

### Downloading tweets from users ###

1. Go to "Tweets by users" tab
2. Type in a list of screen names (or load a text file). One screen name per line, without the @ sign.
3. Click on "Download tweets" and wait.
4. The status bar and the "Log" window will show you when everything is downloaded.
5. Go to your user data folder (specified under "Settings") and navigate to tweets/csv
6. Open the .csv files with the program of your choice
7. If you want XML or plaintext files for use with concordancers, see below





## Requirements ##
  * Python 3
  * tweepy
  * appdirs (included as a private copy)


## Windows ##
An executable of birdbody for Windows can be downloaded here:

http://www.u203d.net/birdbody.exe

Please note that I can not guarantee that the Windows binary will always be up to date, but I will do my best to update it
whenever something import happens in this repository. Note that birdbody.exe takes a few seconds longer to load.

How to use the Windows release:

 * Unzip the birdbody.zip folder
 * Execute birdbody.exe
