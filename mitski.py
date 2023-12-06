import json
import tweepy
import requests
import random
import re
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date
import time

# Parse credentials
with open("twitter.json", "r") as json_file:
    tokens = json.load(json_file)

BEARER_TOKEN = tokens['bearer_token']
CONSUMER_KEY = tokens['api_key']
CONSUMER_SECRET = tokens['api_key_secret']
ACCESS_TOKEN = tokens['access_token']
ACCESS_TOKEN_SECRET = tokens['access_token_secret']

# Create X API v2 Client
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

# Connect to Genius API
with open("genius_login.json", "r") as json_file2:
    tokens2 = json.load(json_file2)

CLIENT_ACCESS_TOKEN = tokens2['client_access_token']

#genius_search_url = f"http://api.genius.com/artists/2579/songs?sort=popularity&per_page=5&page=3&access_token={CLIENT_ACCESS_TOKEN}"
#genius_search_url = f"http://api.genius.com/referents?song_id=399852&text_format=plain&per_page=5&page=3&access_token={CLIENT_ACCESS_TOKEN}"
#genius_search_url = f"http://api.genius.com/songs/399852?access_token={CLIENT_ACCESS_TOKEN}"

def write_song_info(artist, day):
    # Set preference for most popular songs - Genius returns songs in order of popularity
    # ie most of the time it will pull from the first page of results
    if day%2==0:
        page = 1
    else:
        page = random.randint(1,4)

    genius_search_url = f"http://api.genius.com/search?q={artist}&access_token={CLIENT_ACCESS_TOKEN}&page={page}&per_page=15"
    response = requests.get(genius_search_url)
    json_data = response.json()

    song_index = random.randint(0,9)
    data = json_data["response"]['hits'][song_index]
    path = data['result']['path'][1:]
    with open('output.json', "w") as json_file:
        json.dump(data, json_file, indent=2)
    
    # Clear the text file then write to
    with open('lines.txt','w') as txt_file:
        txt_file.write('')

    with open('lines.txt','a') as txt_file:
        title = data['result']['title'] + "\n"
        txt_file.write(title)

    return path, title

def write_lyrics(path):
    response = requests.get("https://genius.com/" + path)
    html_string = response.text
    doc = BeautifulSoup(html_string, 'html.parser')

    loelements = doc.find_all("a", href=re.compile(path[:-7])) #command f: __PRELOADED_STATE
    lyrics = [lyric.text for lyric in loelements]

    with open('lyrics.txt','w') as file:
        file.write('')

    pattern = r'^Who produced'
    #capital_letter = r'(?<=[a-z])(?=[A-Z])'
    capital_letter = r'(?<=[a-z])(?=[A-Z])'
    line_number = -1
    for line in lyrics[1:]:
        if re.search(pattern, line):
            break
        else:
            with open('lyrics.txt','a') as file:
                strings = re.split(capital_letter, line)
                for string in strings:
                    if string[0][0] == '[':
                        continue
                    file.write(string+'\n')
                    line_number += 1
    return line_number

def tweet(tweet_content):
    try:
        #tweet_content = 'test3'
        client.create_tweet(text=tweet_content)
        print("Tweet posted successfully.")
    except tweepy.errors.TweepyException as e:
        print(f"Error posting tweet: {e}")

def main():
    # Pseudo-randomly select a song and dump the Genius information to output.json
    artist = 'Mitski'
    day = int(date.today().strftime('%d'))
    path, song_name = write_song_info(artist, day)
    print(path)

    # Get the lyrics for the song selected in the previous step and write to lyrics.txt
    line_number = write_lyrics(path)

    # Select two lines and post a tweet
    with open('lyrics.txt','r') as lyric_file:
        lyrics = lyric_file.readlines()
        random_index = random.randint(0,line_number-2)
        l1 = lyrics[random_index].strip()
        l2 = lyrics[random_index+1].strip()
        l3 = lyrics[random_index+2].strip()
        lf = f'✰ {song_name}'.strip()
        if l1==l2:
            tweet_content = f"{l1}\n\n{lf}"
        elif day%5==0:
            tweet_content = f"{l1}\n{l2}\n{l3}\n\n{lf}"
        else:
            tweet_content = f"{l1}\n{l2}\n\n{lf}"
        tweet(tweet_content)

    #tweet()
    #scheduled_time = "12:00"
    #while True:
        #curr_time = datetime.now().strftime("%H:%M")
        #if curr_time == scheduled_time:
            #tweet()
        #time.sleep(60)   

if __name__=="__main__":
    main()