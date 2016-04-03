#!/opt/local/bin/python

############################################################
#
## Created by DarkDrag0nite ##
#
#  Example: python pantipScraper.py <start_topic_id>
#
############################################################


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

def validateText(text):
	validateText = text.replace("<br>", "")
	validateText = validateText.replace("<br />", "")
	validateText = validateText.replace("</br>", "")
	validateText = validateText.replace("<u>", "")
	validateText = validateText.replace("</u>", "")
	validateText = validateText.replace("<i>", "")
	validateText = validateText.replace("</i>", "")
	validateText = validateText.replace("<b>", "")
	validateText = validateText.replace("</b>", "")
	validateText = validateText.replace("<strong>", "")
	validateText = validateText.replace("</strong>", "")
	validateText = re.sub('<img[\w"\'\\/=\s]*>', "(img)", validateText)
	return validateText

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
				functionData = self.get_comments_from_link()
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

	def get_comments_from_link(self):
		global udg_header_comment
		udg_header_comment['Referer'] = "http://pantip.com/topic/%s"%(self.tid)
		index = 0
		while(index < 4):
			random_time = random.random()
			comment_response = requests.get("http://pantip.com/forum/topic/render_comments?tid=%s&param=&type=3&time=%s"%(self.tid, random_time), 
					headers=udg_header_comment)
			if (comment_response.reason == 'OK'):
				break
			else:
				index = index + 1
			if index == 4:
				rData = ReturnData(False, "Cannot get comments %s: "%(self.id) + start_page.reason)
				return rData

		comment_response.encoding = udg_thaiEncode
		comments = comment_response.json()
		rData = ReturnData(True, comments)
		return rData

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
	def __init__(self, tid, name, author, author_id, story, like, emo, tags, time):
		self.tid = tid
		self.name = name
		self.author = author
		self.author_id = author_id
		self.story = story
		self.likeScore = like
		self.emoScore = emo
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
		like = tree.xpath('//span[starts-with(@class,"like-score")]/text()')[0]
		emo = tree.xpath('//span[starts-with(@class,"emotion-score")]/text()')[0]
		tags = tree.xpath('//div[@class="display-post-tag-wrapper"]/a[@class="tag-item"]/text()')
		dateTime = tree.xpath('//abbr[@class="timeago"]/@data-utime')[0]

		topic = Topic(tid, name, author, author_id, story, like, emo, tags, dateTime)
		rData = ReturnData(True, topic)
		return rData

	def toDict(self):
		return {
			'tid': self.tid,
			'name': self.name,
			'author' : self.author,
			'author_id' : self.author_id,
			'story' : self.story,
			'likeScore' : self.likeScore,
			'emoScore' : self.emoScore,
			'tagList' : self.tagList,
			'dateTime' : self.dateTime
		}

	def toJson(self):
		return json.dumps(self.toDict(), ensure_ascii=False)

	def __str__(self):
		return ("Name: " + self.name.encode(udg_thaiEncode) +
			"\r\nAuthor: " + self.author.encode(udg_thaiEncode) +
			"\r\nText: " + self.story.encode(udg_thaiEncode) + "\r\n"
			"\r\nLike Count: %s\r\nEmotion Count: %s"%(self.likeScore, self.emoScore) +
			"\r\nTag-item: " + ",".join(self.tagList).encode(udg_thaiEncode) +
			"\r\nDatetime: " + self.dateTime)

class Emotion:
	def __init__(self, like=0, laugh=0, love=0, deep=0, terrify=0, amaze=0):
		self.like = like
		self.laugh = laugh
		self.love = love
		self.deep = deep
		self.terrify = terrify
		self.amaze = amaze

	def toDict(self):
		return {
			'like' : self.like,
			'laugh' : self.laugh,
			'love' : self.love,
			'deep' : self.deep,
			'terrify' : self.terrify,
			'amaze' : self.amaze
		}

	def toJson(self):
		return json.dumps(self.toDict(), ensure_ascii=False)



if __name__ == "__main__":
	if not os.path.exists(udg_storage_dir):
		os.makedirs(udg_storage_dir)
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
			# f.write("Topic-id: %s\n"%(pageID))
			# f.write(str(crawler))
			# writeData = json.dumps(crawler.toJson(), ensure_ascii=False).encode('utf8')
			# json.dump(writeData, f, ensure_ascii=False)
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

