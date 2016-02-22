# birdbody
A graphical interface for creating twitter corpora. Still very much a work in progress.
Based around the tweet_dumper.py gist by Yanofsky (https://gist.github.com/yanofsky/5436496)

## Usage notes ##
You can easily create your own multi-user corpus in CSV, XML and TXT format using the steps outlined below.

### Initial setup ###
In order to use birdbody you need to first create a Twitter app through https://apps.twitter.com.
This allows you to generate the four credentials required to access the Twitter API:
 
 * Customer key
 * Customer secret
 * Access key
 * Access secret

Add these in the "Settings" tab.

### Downloading tweets from users ###
Birdbody can download as many recent tweets of a user as Twitter allows (around 3000).

1. Go to "Tweets by users" tab.
2. Type in a list of screen names (or load a text file). One screen name per line, without the @ sign.
3. Click on "Download tweets" and wait.
5. Go to your user data folder (specified under "Settings") and navigate to tweets/csv
6. Open the .csv files with the program of your choice
7. If you want XML or plaintext files for use with concordancers, see "Conversion" below


### Creating corpora ###
You can aggregate the CSV files to create larger collections.

1. Go to the "File management" tab.
2. Select multiple CSV files from the list box (SHIFT+Click or CTRL+Click).
3. Type in a filename  next to the "Combine files" button. (A generic name with timestamp will be used if empty).
4. Click on "Combine files" and wait.
5. The new combined file will appear in the tweets/csv folder and in the file list.

### Conversion to XML or plaintext ###
You can convert the CSV files into plaintext (just the tweet texts separated by empty lines) or XML files (metadata is stored in attributes of <tweet> nodes, which contain the tweet texts).

1. Go to the "File management" tab.
2. Select any number of CSV files.
3. Click on "Convert to .xml" or "Convert to .txt" and wait.
4. The files are stored in the tweets/xml or tweets/txt folders within your user data folder. 


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
