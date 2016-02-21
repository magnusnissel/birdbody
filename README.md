# birdbody
A graphical interface for creating twitter corpora. Still very much a work in progress.
Based around the tweet_dumper.py gist by Yanofsky (https://gist.github.com/yanofsky/5436496)

## Usage notes ##
In order to use birdbody you need to first create a Twitter app through https://apps.twitter.com.
This allows you to generate the four credentials required to access the Twitter API:
 
 * Customer key
 * Customer secret
 * Access key
 * Access secret

Add these in the fields in the "Settings" tab. If you want you can ask birdbody to store these locally so you don't need to
type / copy them every time you open the app.

## Requirements ##
  * Python 3
  * tweepy
  * appdirs (included as a private copy)


## Windows ##
An executable of birdbody for Windows, that doesn't require Python to be installed, can be downloaded here:

http://www.u203d.net/birdbody.zip

Please note that I can not guarantee that the Windows binary will always be up to date, but I will do my best to update it
whenever something import happens in this repository.

How to use the Windows release:

 * Unzip the birdbody.zip folder
 * Execute birdbody.exe
