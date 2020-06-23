import tweepy
import json
import re
import csv


class TwitterApi:

    def __init__(self):
        self.api = None

    def authentication(self):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)

    def fetch_tweets(self, search_keywords, file_name):
        print("Fetching tweets...")
        tweets = []
        self.authentication()
        for keyword in search_keywords:
            for page in tweepy.Cursor(self.api.search, q=keyword, lang="en", tweet_mode="extended").pages(50):
                for i in page:
                    tweets.append(i._json)
        print("Fetching completed.")
        with open(file_name, 'w') as jsonFile:
            json.dump(tweets, jsonFile, indent=4)
        print("Tweets stored into ", file_name)
        return tweets
    def counting_tweets(self,file_name):
        count=0
        with open(file_name,'r') as read_file:
            text=json.load(read_file)
            for i in text:
                count=count+1
        print("number of tweets:")
        print(count)
            
        

    def clean_tweets(self, source_file_name, destination_file_name):
        print("Loading JSON file...")
        with open(source_file_name, 'r') as read_file:
            data = json.load(read_file)
        tweets = []
        print("Cleaning tweets...")
        for i in data:
            filtered_tweet = {'name': ''.join([c for c in i.get('user').get('name') if ord(c) < 128]),
                              'screen_name': ''.join([c for c in i.get('user').get('screen_name') if ord(c) < 128]),
                              'location': ''.join([c for c in i.get('user').get('location') if ord(c) < 128]),
                              'created_at': ''.join([c for c in i.get('user').get('created_at') if ord(c) < 128])}
            if i.get('retweeted_status'):
                tweet = i.get('retweeted_status').get('full_text')
            else:
                tweet = i.get('full_text')

            tweet = ''.join([c for c in tweet if ord(c) < 128])
            tweet = re.sub(r"http\S+", "", tweet)
            tweet = re.sub(r"\n", " ", tweet)
            tweet = re.sub(r"@\w*", " ", tweet)
            tweet = re.sub(r"^(RT|FAV)", " ", tweet)
            tweet = re.sub(r"[^\w\s]", "", tweet)
            tweet = tweet.strip()
            tweet = re.sub(r"#\w*", " ", tweet.lower())

            filtered_tweet['full_text'] = tweet
            tweets.append(filtered_tweet)

        print("Cleaning completed.")
        with open(destination_file_name, 'w') as jsonFile:
            json.dump(tweets, jsonFile, indent=4)
        print("Cleaned tweets stored into ", destination_file_name)
        return tweets
    
consumer_key = "d35NF4JMtgEGBDZa3OC96ymaM"
consumer_secret = "MyOYXdRhoL8pqwxZpH8mWXkgAzC1XYOxSsMk2PRdBRPCgDPFZy"
access_key = "1241313237615833088-oyTgXVAWvNYZO4B7UK0781MnsvNleV"
access_secret = "6IAQynfiRtCVZoa8US3781fUVcv0e5RjJMEj9ynPOQP46"
searchKeywords = ["Uttarakhand tourism","Uttarakhand food","Uttarakhand weather forecast","Uttarakhand tradition","Uttarakhand","Uttarakhand education","Uttarakhand finance","Uttarakhand economy","Uttarakhand government","Uttarakhand politics","Uttarakhand sports","Uttarakhand health facilities","Uttarakhand hospitals"]
twitterObj = TwitterApi()


twitter_data = twitterObj.fetch_tweets(searchKeywords, 'finaltweets.json')
twitterObj.counting_tweets('finaltweets.json')
cleaned_data=twitterObj.clean_tweets('newtweets2.json', 'finalcleaned_tweets.json')




def create_bag_of_words():
    print("Loading JSON file...")
    with open('finalcleaned_tweets.json', 'r') as read_file:
        data = json.load(read_file)
    print("Creating bag of words...")
    tweetCount = 0
    for i in data:
        tweets[tweetCount] = {}
        tweets[tweetCount]['tweet'] = i['full_text']
        tweets[tweetCount]['bagOfWords'] = {}
        words = re.findall(r"\b\w+-?\w+\b", i['full_text'])

        for word in words:
            if word not in tweets[tweetCount]['bagOfWords']:
                tweets[tweetCount]['bagOfWords'][word] = 1
            else:
                tweets[tweetCount]['bagOfWords'][word] += 1
        tweetCount += 1
    print("Bags of words successfully created.")


def create_sentiment_vectors():
    global positive_opinion_vector
    global negative_opinion_vector
    print("Loading positive-words.txt...")
    with open('positive-words.txt', 'r') as read_file:
        positive_opinion_vector = read_file.read().splitlines()

    print("Loading negative-words.txt...")
    with open('negative-words.txt', 'r') as read_file:
        negative_opinion_vector = read_file.read().splitlines()

    print("Opinion vectors successfully created.")


def analyze_sentiments():
    global positive_opinion_vector
    global negative_opinion_vector
    metadata = ('S.No', 'Message/Tweet', 'Match', 'Polarity')
    print("Performing sentiment analysis...")
    with open('finaltagged-tweets.csv', 'w', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(metadata)
        for t in tweets:
            row = [t, tweets[t]['tweet']]

            positive = list(set(positive_opinion_vector) & set(list(tweets[t]['bagOfWords'].keys())))
            negative = list(set(negative_opinion_vector) & set(list(tweets[t]['bagOfWords'].keys())))
            positiveMagnitude = 0
            negativeMagnitude = 0
            for i in positive:
                positiveMagnitude += tweets[t]['bagOfWords'][i]
            for i in negative:
                negativeMagnitude += tweets[t]['bagOfWords'][i]

            match = " ".join(j for j in positive)
            temp = " ".join(j for j in negative)
            match = match + " " + temp
            row.append(match)

            if positiveMagnitude > negativeMagnitude:
                row.append("positive")
            elif positiveMagnitude < negativeMagnitude:
                row.append("negative")
            else:
                row.append("neutral")

            writer.writerow(row)
    print("Tagged tweets successfully stored in finaltagged-tweets.csv")


tweets = {}
positive_opinion_vector = []
negative_opinion_vector = []
create_bag_of_words()
create_sentiment_vectors()
analyze_sentiments()
