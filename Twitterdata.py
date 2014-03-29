import tweepy
import json
import pickle
import nltk,sys
from nltk.corpus import stopwords

consumerKey = "A1pZOTrTqVmePalcUGi2ZA"
consumerSecret = "YD72Srbim8ezEwVFVl52GmS2Ws5Tvtcxp5TcgfhLS0Y"
accessToken = "129277744-2GsOUIUNTLw7MldL64BSjOf9NDn9HRSr9TxY0poU"
accessTokenSecret = "hD2puf6vMFv0ZX8legYGCN3eUfDLW95b9bblkPYU0"

def hasLink(str):
    s='http://t.co'
    pos=str.find(s)
    if pos != -1:
        return True
    else:
        return False

def FilterStatus(textword):
    wordList = textword.split(" ")
    newList = []
    for i in wordList:
        if i not in stopwords.words("english"):
            newList.append(i)
    return newList 
    

class StdOutListener(tweepy.streaming.StreamListener):
    ''' Handles data received from the stream. '''
    AuthorTweetDB = {}
    Authors = ['129277744']
    count = 0
    def on_status(self, status):
        # Prints the text of the tweet
        try :
            if status.__dict__.has_key("retweeted_status") and self.AuthorTweetDB[status.retweeted_status.user.id_str]["tweets"].has_key(status.retweeted_status.id_str):
                print "1-ReTweet",status.text
                self.AuthorTweetDB[status.retweeted_status.user.id_str]["tweets"][status.retweeted_status.id_str]["retweets"][status.id] = {
                                                                                                                                                "time" : status.created_at,
                                                                                                                                                "location" : status.user.location,
                                                                                                                                                "verified" : status.user.verified,
                                                                                                                                                "username" : status.user.screen_name,
                                                                                                                                                "description" : status.user.description
                                                                                                                                            }

            elif self.AuthorTweetDB.has_key(status.user.id_str) and status.in_reply_to_status_id_str == None and status.__dict__.has_key("retweeted_status")==False:
                print "2-Original", status.text
                self.AuthorTweetDB[status.user.id_str] = {
                                                        "username" : status.user.screen_name,
                                                        "created_time" : status.user.created_at,
                                                        "description" : status.user.description,
                                                        "location" : status.user.location,
                                                        "timezone" : status.user.time_zone,
                                                        "utc_offset" : status.user.utc_offset,
                                                        "verified" : status.user.verified,
                                                        "tweets" : { 
                                                                    status.id_str : {
                                                                                    "text" : FilterStatus(status.text),
                                                                                    "length" : len(status.text),
                                                                                    "created_at" : status.created_at,
                                                                                    "#" : status.entities["hashtags"],
                                                                                    "followers_count" : status.user.followers_count,
                                                                                    "link" : hasLink(status.text),
                                                                                    "retweets" : {},
                                                                                    "reply" : {}
                                                                                    }
                                                                   }
                                                    }
            elif status.in_reply_to_status_id_str != None :
                print "3-Reply",status.text
                self.AuthorTweetDB[status.in_reply_to_user_id_str]["tweets"][status.in_reply_to_status_id_str]["reply"][status.id] = {
                                                                                                                                            "time" : status.created_at,
                                                                                                                                            "location" : status.user.location,
                                                                                                                                            "verified" : status.user.verified,
                                                                                                                                            "username" : status.user.screen_name,
                                                                                                                                            "description" : status.user.description
                                                                                                                                     }
            self.count+=1
            if self.count == 4 :
                f = open("AuthorTweetDB","w")
                f.write(pickle.dumps(self.AuthorTweetDB))
                f.close()
                sys.exit()

        except KeyError:
            pass
        return True
 
    def on_error(self, status_code):
        print('Got an error with status code: ' + str(status_code))
        return True # To continue listening
 
    def on_timeout(self):
        print('Timeout...')
        return True # To continue listening
    
 

if __name__ == '__main__':
    listener = StdOutListener()
    for auth in listener.Authors:
        listener.AuthorTweetDB[auth] = {}
    auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessTokenSecret)
    stream = tweepy.streaming.Stream(auth, listener)
    stream.filter(follow=['129277744'])
