#! /usr/bin/env python

# This script makes use of Facebook Graph API to post thank you so much (i.e. tysm :) )
# comments on the statuses containing the string 'happy' in them.
# This script was written to thank everyone who was wished you a happy birthday on 
# your facebook Wall.

# @author: Akhil Rao

import urllib
import urllib2
import json

class FB:
	'''
	a class that handles FB specific actions.
	'''
	def __init__(self,access_token,message = "Thank you so much"):
		"""
		Initialise the fb object with self id and access token
		"""
		self.graph_base_url="https://graph.facebook.com/";	#graph base url to which all queries are appended
		self.access_token=access_token;				#access token to be sent with every request.
		self.message=message;					#default comment message					
		self.done=[];						#Keeps track of posts already covered
		self.response="";					#Stores the reponse after every query
		self.id=""						#Stores the unique facebook numeral id
		try:		
			donefile=open('done.txt','r');			
			for postid in donefile.readlines():		#Populate the done list with covered posts.
				self.done.append(postid.strip());
		except:
			print 'done.txt does not exist.'
		resp=self.SubmitRequest(self.graph_base_url+"me",getdict={'fields':'id,name'});
		self.id=json.loads(resp)['id'];				#Obtain the self id
	
	def __del__(self):	
		"""
		Performs the cleanup by dumping all the covered posts in a file: done.txt separated by new lines.
		"""				
		try: 	
			donefile=open('done.txt','w');
			for postid in self.done:
				donefile.write(postid+'\n');
			donefile.close();
		except:
			print 'done.txt cannot be saved;'
		
	def SubmitRequest(self,url,getdict={},postdata=None):
		"""
		Submits a request to facebook
		url is the connection url
		getdict contains GET method parameter and value pairs	
		postdata contains data to be sent by POST method
		"""
		if(url.count("?")==0):
			url=url + "?";
		else:
			url=url+"&";
		for key in getdict:
			url=url+key+"="+getdict[key]+'&';
		url=url+'access_token='+self.access_token;	
		if postdata != None:	
			dat=urllib.urlencode(postdata);
			return	urllib2.urlopen(url=url,data=dat).read();
		else:
			return	urllib2.urlopen(url=url).read();
	
	def like(self,postid):	
		"""
			Likes the post with id: postid
		"""
		link=self.graph_base_url+postid+"/likes"
		return self.SubmitRequest(link,postdata={});

	def comment(self,postid,message=""):
		"""
			Comments message on the post with postid
		"""
		if message=="":
			message=self.message;
		link=self.graph_base_url+postid+"/comments"
		return self.SubmitRequest(link,postdata={'message':message});
		
	def getFeed(self,limit=25):
		"""
			Get the feed from the wall with a maximum limit of "limit"
		"""
		link=self.graph_base_url+"/me/feed/"
		getdictfilter={
			'fields':'id,type,message,from',
			'limit':str(limit)
		}
		self.response=self.SubmitRequest(link,getdict=getdictfilter);
		
	def parse(self,jsondata=""):
		"""
			Parses the json data in the respnse to obtain 
			fromname,fromid, postid,message,type and returns
			a list of dictionaries
		"""
		if jsondata=="":
			jsondata=self.response;	
		data=json.loads(jsondata)
		whole=data[u'data'];
		pposts=[];
		for post in whole:
			dictpost={};
			dictpost['id']=post[u'id'];
			if u'message' in post.keys():
				dictpost['message']=post[u'message'];
			dictpost['type']=post[u'type'];
			if u'from' in post:
				dictpost['from']=post[u'from'][u'id'];		
				dictpost['from-name']=post[u'from'][u'name'];
			pposts.append(dictpost);
		return pposts;

	def getResponse(self):
		"""
			Returns last saved response
		"""
		return self.response;

	def addToDoneList(self,value):
		"""
			Adds a postid to the done list
		"""
		self.done.append(value);

	def getDoneList(self):
		"""
			Returns the done list
		"""
		return self.done;
	
	def getid(self):
		"""
			Returns the user's facebook unique ID
		"""
		return self.id;

def main():

	print '''Welcome to TYSM by Akhil Rao.
This tool will allow you to thank all the friends who post on your wall.
You need to provide your access token from the graph api explorer with 
the following permissions:
*publish_stream
*read_status
*read_friendlists

Graph API Explorer : https://developers.facebook.com/tools/explorer			  
	'''	
	prompt_for_message=False;		#True : will make it prompt for custom message
	add_name_in_comment=True;		#Will add the name in front of the comment if True

	access_token=raw_input('Enter your access token') #Obtain the access_token from the user
	
	if prompt_for_message:
		message = raw_input('Enter your comment message:')
	else:
		message = u'Thank you so much '
	myfb=FB(access_token,message); 			#Initialize the FB object with access token
	
	myfb.getFeed(10);				#Get the feed with the post limit and parse
	postsdone=myfb.getDoneList();			
	fields=myfb.parse();	
	types=['status','video','photo'];	
	for post in fields:
		#	post a like and comment if following is True
		#	post id is not already covered
		#	post is a status and not from you
		#	post contains the string 'happy' in any case
		try:
			if (not post['id'] in postsdone) and post['type'] in types and 'message' in post.keys() and \
					(post['message'].lower().count(u'happy')>0) and post['from'] != myfb.getid():
				myfb.like(post['id']);	
				if add_name_in_comment:
					postfix=post['from-name']+" ";
				else:
					postfix=""			
				myfb.comment(post['id'],message=unicode(message)+unicode(postfix)+u'!!! :)');
				myfb.addToDoneList(post['id']);
				print 'Liked and Commented on post by ' + post['from-name'];
		except:
			continue;

if __name__ == "__main__":
	main();	

