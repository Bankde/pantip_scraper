# pantip_scraper
# Created by DarkDrag0nite

This is web scraper for pantip written in python2

# How to use


To get a topic: python pantipScraper.py topic_id
	
Start from: python pantipScraper.py -start topic_id
	
End at: python pantipScraper.py -start topic_id -end topic_id



Example: python pantipScraper.py 35000000

Example: python pantipScraper.py -start 35000000

Example: python pantipScraper.py -start 35000000 -end 35001000



Example of reading JSON is in readExample.py

Another example of reading JSON (plain text style): 

    PYTHONIOENCODING=UTF-8 python readExample2.py > result_of_readExample2

# Features

The data will be store in pantip_storage as JSON.

Right now it could extract
- topic name
- author
- story
- like Count
- emotion Count
- emotions (count of each types)
- tags
- comments count
- comments

Extra Feature
- Could Handel connection problem (test on OS X, not confirm on linux/windows)

# Limitations

- no image being extracts (I can't decide how to save image properly and how to link that image to topic)
- no poll information and topic with poll might be extracted incorrectly
- no reply to comment yet (sry, I'm working on it)

# Json Structure

JSON structure is as following:

== Topic ==
- tid (อันนี้หมายถึง topic id)
- name (topic name)
- author
- author_id
- story
- likeCount
- emoCount
- emotions (as Emotion object)
- tagList (as array of string)
- dateTime
- commentCount
- comments (as array of Comment object)

== Comment ==
- num
- user_id
- user_name
- replyCount
- replies (still working on it)
- message
- emotions (as Emotion object) 
- likeCount
- dateTime

== Emotion ==
- like
- laugh
- love
- impress
- scary
- surprised

# Credit, Feedback, Suggestion is appreciated.
