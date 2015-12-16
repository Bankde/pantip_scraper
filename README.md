# pantip_scraper

This is web scraper for pantip written in python.
To use:
python pantip.py start_topic_id_here

The data will be store in pantip_storage.
Right now it could extract
- topic name
- author
- story
- like votes
- emotion votes
- tags
- comments count

Limitations:
- no image being extracts
- no poll information and topic will poll might be extracted incorrectly
- no comments yet

The program will not extract main story unless you fix it a bit. (You can easily see line being commented)
I haven't set up comment part yet because it would be too much work (for me right now)
