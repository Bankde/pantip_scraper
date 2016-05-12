# pantip_scraper
# Created by DarkDrag0nite

This is web scraper for pantip written in python2

# How to use

To use: python pantipScraper.py start_topic_id_here

Example: python pantipScraper.py 35143000

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
- only first 100 comments are gathered (for now, I will update in very near future)
- no reply to comment yet (sry, I'm working on it)
- Small problem on reading JSON because of encoding (I suggest using python3 when reading those file, you still need to use python2 to run this program though). In python2, You can easily get pass encoding problem by following my example.

# Json Structure

JSON structure is as followed:
- tid (อันนี้หมายถึง topic id)
- name (topic name)
- author
- author_id
- story
- likeCount
- emoCount
- emotions
  - > like
  - >	laugh
  - > love
  - > impress
  - > scary
  - > surprised
- tagList (จะเป็น array)
- dateTime

# Credit, Feedback, Suggestion is appreciated.
