# pantip_scraper
# Created by DarkDrag0nite

This is web scraper for pantip written in python.

# How to use

To use: python pantipScraper.py start_topic_id_here

Example: python pantipScraper.py 35143000

Example of reading JSON is in readExample.py

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

# Limitations

- no image being extracts (I can't decide how to save image properly and how to link that image to topic)
- no poll information and topic with poll might be extracted incorrectly
- only first 100 comments are gathered (for now, I will update in very near future)
- no reply to comment yet (sry, I'm working on it)

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
