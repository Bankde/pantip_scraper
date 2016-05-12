#!/opt/local/bin/python

#############################################################
#															#
#  Created by DarkDrag0nite									#
#															#
#  To use: python pantipScraper.py <start_topic_id>			#
#  Example: python pantipScraper.py 35000000				#
#															#
#############################################################


from lxml import html
import json
import requests
from requests.exceptions import ConnectionError, ReadTimeout
import time
import random
import os, sys
import re
import codecs

udg_thaiEncode = 'UTF-8'
udg_header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:42.0) Gecko/20100101 Firefox/42.0'}
udg_header_comment = {
	'Host': 'pantip.com',
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:42.0) Gecko/20100101 Firefox/42.0',
	'Accept': 'application/json, text/javascript, */*; q=0.01',
	'Accept-Language': 'en-US,en;q=0.5',
	'Accept-Encoding': 'gzip, deflate',
	'X-Requested-With': 'XMLHttpRequest',
	'Connection': 'keep-alive'
}
udg_storage_dir = "pantip_storage"

# # Not being used
# def validateText(text):
# 	validateText = text.replace("<br>", "")
# 	validateText = validateText.replace("<br />", "")
# 	validateText = validateText.replace("</br>", "")
# 	validateText = validateText.replace("<u>", "")
# 	validateText = validateText.replace("</u>", "")
# 	validateText = validateText.replace("<i>", "")
# 	validateText = validateText.replace("</i>", "")
# 	validateText = validateText.replace("<b>", "")
# 	validateText = validateText.replace("</b>", "")
# 	validateText = validateText.replace("<strong>", "")
# 	validateText = validateText.replace("</strong>", "")
# 	validateText = re.sub('<img[\w"\'\\/=\s]*>', "(img)", validateText)
# 	return validateText

class ReturnData:

	def __init__(self, status, data):
		self.status = status
		self.data = data

	def getStatus(self):
		return self.status

	def getData(self):
		return self.data

class PantipCrawler:

	def __init__(self, tid):
		self.tid = tid
		self.commentCount = 0
		self.topic = ''
		self.comments = ''

	def crawl(self):
		while True:
			try:
				# Get Main Topic
				functionData = Topic.get_topic_from_link(self.tid)
				if functionData.getStatus() == False:
					return functionData
				else:
					self.topic = functionData.getData()

				# Get Comments
				functionData = Comment.get_comments_from_link(self.tid)
				if functionData.getStatus == False:
					return functionData
				else:
					self.comments = functionData.getData()

				# print json.dumps(self.comments, ensure_ascii=False)
				# s = json.dumps(self.topic.toDict(), ensure_ascii=False)

				# Get Comment count
				if self.comments and 'count' not in self.comments:
					self.commentCount = 0
				else:
					self.commentCount = self.comments['count']

				rData = ReturnData(True, "Success: Crawling page %s"%(self.tid))
				return rData
			except ConnectionError as e:
				print "Connection error: Program will try again in 10s. Ctrl+c to quit"
				time.sleep(10)
			except ReadTimeout as e:
				print "Request timeout: Program will try again in 10s. Ctrl+c to quit"
				time.sleep(10)

	def __str__(self):
		return (str(self.topic) + "\r\n" +
			"Comment count: %s\r\n"%(self.commentCount))

	def toDict(self):
		tempDict = self.topic.toDict()
		tempDict['commentCount'] = self.commentCount
		return tempDict

	def toJson(self):
		return json.dumps(self.toDict(), ensure_ascii=False)

class Topic:
	def __init__(self, tid, name, author, author_id, story, likeCount, emoCount, emotions, tags, time):
		self.tid = tid
		self.name = name
		self.author = author
		self.author_id = author_id
		self.story = story
		self.likeCount = likeCount
		self.emoCount = emoCount
		self.emotions = emotions
		self.tagList = tags
		self.dateTime = time

	@staticmethod
	def get_topic_from_link(tid):
		global udg_header
		index = 0
		while(index < 4):
			start_page = requests.get("http://pantip.com/topic/%s"%(tid), 
				headers=udg_header_comment)
			if (start_page.reason == 'OK'):
				break
			else:
				index = index + 1
			if index == 4:
				rData = ReturnData(False, "Cannot open page %s: "%(tid) + start_page.reason)
				return rData

		start_page.encoding = udg_thaiEncode
		# validText = validateText(start_page.text)
		# tree = html.fromstring(validText)
		tree = html.fromstring(start_page.text)
		
		if tree.xpath('//div[starts-with(@class,"callback-status")]/text()'):
			if not tree.xpath('//h2[@class="display-post-title"]/text()'):
				rData = ReturnData(False, tree.xpath('//div[starts-with(@class,"callback-status")]/text()')[0].strip())
				return rData

		name = tree.xpath('//h2[@class="display-post-title"]/text()')[0]
		author = tree.xpath('//a[@class="display-post-name owner"]/text()')[0]
		author_id = tree.xpath('//a[@class="display-post-name owner"]/@id')[0]
		# story = tree.xpath('//div[@class="display-post-story"]/text()')[0]
		story = tree.xpath('//div[@class="display-post-story"]')[0].text_content()
		likeCount = tree.xpath('//span[starts-with(@class,"like-score")]/text()')[0]
		emoCount = tree.xpath('//span[starts-with(@class,"emotion-score")]/text()')[0]
		allEmos = tree.xpath('//span[@class="emotion-choice-score"]/text()')
		tags = tree.xpath('//div[@class="display-post-tag-wrapper"]/a[@class="tag-item"]/text()')
		dateTime = tree.xpath('//abbr[@class="timeago"]/@data-utime')[0]

		emotions = Emotion(allEmos[0], allEmos[1], allEmos[2], allEmos[3], allEmos[4], allEmos[5])
		topic = Topic(tid, name, author, author_id, story, likeCount, emoCount, emotions, tags, dateTime)
		rData = ReturnData(True, topic)
		return rData

	def toDict(self):
		return {
			'tid': self.tid,
			'name': self.name,
			'author' : self.author,
			'author_id' : self.author_id,
			'story' : self.story,
			'likeCount' : self.likeCount,
			'emoCount' : self.emoCount,
			'emotions' : self.emotions.toDict(),
			'tagList' : self.tagList,
			'dateTime' : self.dateTime
		}

	def toJson(self):
		return json.dumps(self.toDict(), ensure_ascii=False)

	def __str__(self):
		return ("Name: " + self.name.encode(udg_thaiEncode) +
			"\r\nAuthor: " + self.author.encode(udg_thaiEncode) +
			"\r\nText: " + self.story.encode(udg_thaiEncode) + "\r\n"
			"\r\nLike Count: %s\r\nEmotion Count: %s"%(self.likeCount, self.emoCount) +
			"\r\nTag-item: " + ",".join(self.tagList).encode(udg_thaiEncode) +
			"\r\nDatetime: " + self.dateTime)

class Comment:
	def __init__(self, num, user_id, user_name, replies, message, emotions, likeCount, dateTime):
		self.num = num
		self.user_id = user_id
		self.user_name = user_name
		self.replies = replies
		self.message = message
		self.emotions = emotions
		self.likeCount = likeCount
		self.dateTime = dateTime

	@staticmethod
	def get_comments_from_link(tid):
		global udg_header_comment
		udg_header_comment['Referer'] = "http://pantip.com/topic/%s"%(tid)
		index = 0
		while(index < 4):
			random_time = random.random()
			comment_response = requests.get("http://pantip.com/forum/topic/render_comments?tid=%s&param=&type=3&time=%s"%(tid, random_time), 
					headers=udg_header_comment)
			if (comment_response.reason == 'OK'):
				break
			else:
				index = index + 1
			if index == 4:
				rData = ReturnData(False, "Cannot get comments %s: "%(tid) + start_page.reason)
				return rData

		comment_response.encoding = udg_thaiEncode
		comments = comment_response.json()

		# 	jquery.topic-renovate.js
		# 	$.commentTopic.replyNext = function(){
		# $(document).on('click','.load-reply-next',function(){
		# 	var id = $(this).data('lmr').split('-');
		# 	var lastId = id[0];
		# 	var refId = id[1];
		# 	var refCount = id[2];
		# 	var refBar = $(this).parents('.loadmore-bar-paging.sub-loadmore').get(0).id;
		# 	#	Owner of TOPIC
		# 	var owner = $('.main-post-inner').find('.display-post-name.owner').get(0).id;
			
		rData = ReturnData(True, comments)
		return rData		

	def toDict(self):
		return {
			'num' : self.num,
			'user_id' : self.user_id,
			'user_name' : self.user_name,
			# I'm still thinking how should I handel the replies
			'replies' : self.replies,
			'message' : self.message,
			'emotions' : self.emotions.toDict(),
			'likeCount' : self.likeCount,
			'dateTime' : self.dateTime
		}

	def toJson(self):
		return json.dumps(self.toDict(), ensure_ascii=False)


class Emotion:
	def __init__(self, like=0, laugh=0, love=0, impress=0, scary=0, surprised=0):
		self.like = like
		self.laugh = laugh
		self.love = love
		self.impress = impress
		self.scary = scary
		self.surprised = surprised

	def toDict(self):
		return {
			'like' : self.like,
			'laugh' : self.laugh,
			'love' : self.love,
			'impress' : self.impress,
			'scary' : self.scary,
			'surprised' : self.surprised
		}

	def toJson(self):
		return json.dumps(self.toDict(), ensure_ascii=False)



if __name__ == "__main__":
	if not os.path.exists(udg_storage_dir):
		os.makedirs(udg_storage_dir)
	if not len(sys.argv) == 2:
		print "Please enter starting pageID to start program."
		print "E.g. python pantipScraper.py 35000000"
		exit()
	pageID = (int)(sys.argv[1])
	storage_file = str(pageID / 1000)
	f = open(udg_storage_dir + "/ptopic" + storage_file, "a+")
	indexFile = open(udg_storage_dir + "/indexFile.txt", "w+")
	errorFile = open(udg_storage_dir + "/errorFile.txt", "a+")
	while (True):
		temp_file = str(pageID / 1000)
		if temp_file != storage_file:
			storage_file = temp_file
			f.close()
			f = codecs.open(udg_storage_dir + "/ptopic" + storage_file, "a+", encoding=udg_thaiEncode)
		crawler = PantipCrawler(str(pageID))
		functionData = crawler.crawl()
		if functionData.getStatus() == True:
			f.write(crawler.toJson().encode('UTF-8'))
			f.write("\n")
			indexFile.seek(0,0)
			indexFile.write("Done: %s\n"%(pageID))
			print functionData.getData()
		else:
			errorFile.write("Failed: Crawling page %s: "%(pageID) + functionData.getData().encode(udg_thaiEncode) + "\n")
			print "Failed: Crawling page %s: "%(pageID) + functionData.getData().encode(udg_thaiEncode)
		pageID = pageID + 1
		time.sleep(3)

