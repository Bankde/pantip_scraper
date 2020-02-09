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

udg_thaiEncode = 'utf-8-sig'
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

# GLOBAL MODE # // This shouldn't be global but global is easier for faster develop
disableCommentFeature = False

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
		self.topic = ''

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
					comments = functionData.getData()

				# Get Comment count
				if comments:
					commentCount = len(comments)
				else:
					commentCount = 0

				self.topic.commentCount = commentCount
				self.topic.comments = comments

				rData = ReturnData(True, "Success: Crawling page %s"%(self.tid))
				return rData
			except ConnectionError as e:
				print("Connection error: Program will try again in 10s. Ctrl+c to quit")
				time.sleep(10)
			except ReadTimeout as e:
				print("Request timeout: Program will try again in 10s. Ctrl+c to quit")
				time.sleep(10)

	def __str__(self):
		return str(self.topic)

	def toDict(self):
		tempDict = self.topic.toDict()
		return tempDict

	def toJson(self):
		return json.dumps(self.toDict(), ensure_ascii=False)

class Topic:
	def __init__(self, tid, name, author, author_id, story, likeCount, emoCount, emotions, tags, time, commentCount=0, comments=[]):
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
		self.commentCount = 0
		self.comments = []

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
		tree = html.fromstring(start_page.text)

		tmp = tree.xpath('//div[starts-with(@class,"callback-status")]')
		if tmp and tmp[0].text_content():
			if not tree.xpath('//h2[@class="display-post-title"]/text()'):
				rData = ReturnData(False, tree.xpath('//div[starts-with(@class,"callback-status")]')[0].text_content().strip())
				return rData

		name = tree.xpath('//h2[@class="display-post-title"]/text()')[0]
		author = tree.xpath('//a[@class="display-post-name owner"]/text()')[0]
		author_id = tree.xpath('//a[@class="display-post-name owner"]/@id')[0]
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
			'dateTime' : self.dateTime,
			'commentCount' : self.commentCount,
			'comments' : [comment.toDict() for comment in self.comments]
		}

	def toJson(self):
		return json.dumps(self.toDict(), ensure_ascii=False)

	def __str__(self):
		return ("Name: " + self.name.encode(udg_thaiEncode) +
			"\r\nAuthor: " + self.author.encode(udg_thaiEncode) +
			"\r\nText: " + self.story.encode(udg_thaiEncode) + "\r\n"
			"\r\nLike Count: %s\r\nEmotion Count: %s"%(self.likeCount, self.emoCount) +
			"\r\nTag-item: " + ",".join(self.tagList).encode(udg_thaiEncode) +
			"\r\nDatetime: " + self.dateTime +
			"\r\nCommentCount: " + self.commentCount)

class Comment:
	def __init__(self, num, user_id, user_name, replyCount, replies, message, emotions, likeCount, dateTime):
		self.num = num
		self.user_id = user_id
		self.user_name = user_name
		self.replyCount = replyCount
		self.replies = replies
		self.message = message
		self.emotions = emotions
		self.likeCount = likeCount
		self.dateTime = dateTime

	@staticmethod
	def get_comments_from_link(tid):
		global udg_header_comment
		global disableCommentFeature

		udg_header_comment['Referer'] = "http://pantip.com/topic/%s"%(tid)
		comments = []
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
		comment_response_json = comment_response.json()

		if comment_response_json and 'count' not in comment_response_json:
			commentCount = 0
		else:
			commentCount = comment_response_json['count']

		if not disableCommentFeature and not commentCount == 0:
			for c in comment_response_json['comments']:
				comments.append(Comment.convertPantip2Python(c))

			if int(commentCount) > 100:
				pageIndex = 2
				while commentCount > (pageIndex-1)*100:
					index = 0
					while index < 4:
						random_time = random.random()
						comment_response = requests.get("http://pantip.com/forum/topic/render_comments?tid=%s&param=page%s&type=4&page=%s&parent=2&expand=1&time=%s"%(tid, pageIndex, pageIndex, random_time),
								headers=udg_header_comment)
						if (comment_response.reason == 'OK'):
							break
						else:
							index = index + 1
						if index == 4:
							rData = ReturnData(False, "Cannot get comments %s: "%(tid) + start_page.reason)
							return rData

					comment_response.encoding = udg_thaiEncode
					comment_response_json = comment_response.json()
					for c in comment_response_json['comments']:
						comments.append(Comment.convertPantip2Python(c))
					pageIndex += 1
		else:
			comments = {}

		rData = ReturnData(True, comments)
		return rData

	@staticmethod
	def convertPantip2Python(comment):
		# Coming soon
		replies = []
		emotions = Emotion.convertPantip2Python(comment['emotion'])
		return Comment(comment['comment_no'], 
			comment['user']['mid'], 
			comment['user']['name'], 
			comment['reply_count'], 
			replies, 
			comment['message'], 
			emotions, 
			comment['point'], 
			comment['data_utime'])

	def toDict(self):
		return {
			'num' : self.num,
			'user_id' : self.user_id,
			'user_name' : self.user_name,
			# I'm still thinking how should I handel the replies
			'replyCount' : self.replyCount,
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

	@staticmethod
	def convertPantip2Python(emotions):
		return Emotion(emotions['like']['count'], 
			emotions['laugh']['count'], 
			emotions['love']['count'], 
			emotions['impress']['count'], 
			emotions['scary']['count'], 
			emotions['surprised']['count'])

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


def modeRoom(submode):
	random_time = random.random()
	topicList_response = requests.post("http://pantip.com/forum/topic/ajax_json_all_topic_info_loadmore?t=%s"%(random_time), 
				data = {'last_id_current_page' : "35100000",
						'dataSend[room]' : "food",
						'dataSend[topic_type][type]' : "0",
						'dataSend[topic_type][default_type]' : "1",
						'thumbnailview' : "false",
						'current_page': "1"
						},
				headers=udg_header_comment)

	topicList = topicList_response.json()
	for topic in topicList['item']['topic']:
		print(topic['_id']),

def modeBruteID(submode):
	pageID = submode['pageID']
	endID = submode['endID']

	storage_file = 0
	f = None
	indexFile = open(udg_storage_dir + "/indexFile.txt", "w+")
	errorFile = open(udg_storage_dir + "/errorFile.txt", "a+")
	while (True):
		temp_file = str(int(pageID / 1000))
		if temp_file != storage_file:
			storage_file = temp_file
			f.close() if f else None
			f = open(udg_storage_dir + "/ptopic" + storage_file, "ab+")
		crawler = PantipCrawler(str(pageID))
		functionData = crawler.crawl()
		if functionData.getStatus() == True:
			f.write(crawler.toJson().encode(udg_thaiEncode))
			f.write(b"\n")
			indexFile.seek(0,0)
			indexFile.write("Done: %s\n"%(pageID))
			print(functionData.getData())
		else:
			errorFile.write("Failed: Crawling page %s: "%(pageID) + functionData.getData() + "\n")
			print("Failed: Crawling page %s: "%(pageID) + functionData.getData())
		pageID = pageID + 1
		if pageID > endID:
			break
		time.sleep(3)

def helpMode():
	print("""
== Quick use ==
To get a topic: python pantipScraper.py <topic_id>
Start from: python pantipScraper.py -start <topic_id>
End at: python pantipScraper.py -start <topic_id> -end <topic_id>

== Mode ==
\t-b\t\tbrute topic ID
\t-r <room>\tbrute from selected pantip room
\t-c\t\tcontinue from previous work
== Submode ==
\t-tid <id>\t get data from selected topic id
\t-start <id>\t start from selected topic id
\t-end <id>\t stop at selected topic id (leave this empty for infinite)
\t-noComment\t do not save comment (save data storage, bandwidth is still used)
""")

if __name__ == "__main__":
	if not os.path.exists(udg_storage_dir):
		os.makedirs(udg_storage_dir)

	index = 1
	mode = ""
	submode = {}
	## Default ##
	submode['mode'] = "get"
	mode = modeBruteID
	#############
	if len(sys.argv) > 1:
		if sys.argv[1] == '-h' or sys.argv[1] == '--help' or sys.argv[1] == "help":
			helpMode()
			exit()
		while index < len(sys.argv):
			if sys.argv[index] == "-r":
				mode = modeRoom
			elif sys.argv[index] == "-b":
				mode = modeBruteID
			elif sys.argv[index] == "-cont" or sys.argv[index] == "-c":
				submode['mode'] = "cont"
			elif sys.argv[index] == "-start":
				submode['mode'] = "start"
				index = index + 1
				submode['start'] = (int)(sys.argv[index])
			elif sys.argv[index] == "-end":
				index = index + 1
				submode['end'] = (int)(sys.argv[index])
			elif sys.argv[index] == "-tid" or sys.argv[index] == "-get":
				submode['mode'] = "get"
				index = index + 1
				submode['tid'] = (int)(sys.argv[index])
			elif sys.argv[index] == "-noComment":
				disableCommentFeature = True
			elif index == (len(sys.argv)-1) and ('start' not in submode) and ('end' not in submode):
				mode = modeBruteID
				submode['tid'] = (int)(sys.argv[index])
			else:
				print("You just typed invalid mode: " + sys.argv[index])
				print("PS: please type ID as last parameter (or after -tid, -start, -end)")
				exit()
			index = index + 1
	else:
		print("""
Please enter mode to start program.
E.g. python pantipScraper.py 35000000
For more mode: python pantipScraper.py --help
""")
		exit()

	# Arrange the input
	funcArgv = {}
	if 'end' not in submode:
		funcArgv['endID'] = 100000000000
	else:
		funcArgv['endID'] = submode['end']

	if submode['mode'] == "start":
		funcArgv['pageID'] = submode['start']
	elif submode['mode'] == "get":
		funcArgv['pageID'] = submode['tid']
		funcArgv['endID'] = submode['tid']
	mode(funcArgv)

	print("Finished scraping")

