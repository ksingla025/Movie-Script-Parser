#!/usr/bin/python

''' This scraps scripts from IMSDB and returns XML files '''

import sys
import requests
import commands
from bs4 import BeautifulSoup

out_xml = "/Users/Singla/Desktop/projects/MICA/Movie-Script-Parser/out_xml/"
commands.getstatusoutput("mkdir -p "+out_xml)

class ScriptParser(object):

	def _init(self):
		self.karan = ''
	def fetch_data(self,movie_list):
		all_text  = {}
		for movie in movie_list:
			all_text[movie] = []
			xml=[]
			text = ''
			res = requests.get('http://www.imsdb.com/scripts/'+movie+".html")
			soup = BeautifulSoup(res.text, 'html.parser')
			for link in soup.find_all('pre'):
				text = text + link.get_text()

			text = text.split("\n")
			all_text[movie] = text
		return all_text

	def text2xml(self,preprocessed_text):
		for movie in preprocessed_text.keys():

			text = preprocessed_text[movie]
			xml = []
			dialogue = 0
			FLAG = 0
			speakers = []
			contexts = []
			utterances = []
			num_utterance = 0

			for i  in range(0,len(text)):
		  	 	try :
					if "**start**" in text[i]:
						FLAG = 1
					
					if "**end**" in text[i]:
						FLAG = 0
					
					if FLAG == 1:
						if text[i].startswith("**speaker**"):
							text[i] = text[i].split("**speaker**")[1].strip()
							speakers.append("\t<speaker>"+text[i]+"</speaker>")

							# uttrances for a dialogue
							num_utterance = num_utterance + 1

							# get a uttrance until there is a line break
							utterance = ''
							for j in range(1,10):
								if len(text[i+j].split()) != 0:
									if "**dialgoue_change**" not in text[i+j]:
										utterance = utterance + " " + text[i+j].strip()
									else:
										break
								else:
									i = i + j
									break

							# get a context until there is a line break 
							context = ''
							for k in range(1,10):
								if len(text[i+k].split()) != 0:
									if "**dialgoue_change**" not in text[i+k]:
										context = context + " " + text[i+k].strip()
									else:
										break	
								else:
									i = i + k
									break
							contexts.append('\t\t<context>'+context+'</context>')
							utterances.append('\t\t<utterance>'+utterance+'</utterance>')

						elif "**dialgoue_change**" in text[i] :
							dialogue = dialogue + 1
							if dialogue == 1:
								xml.append('<dialogue id= "'+str(dialogue)+'" n_utterances= "'+str(num_utterance)+'">')
							else:
								xml.append('</dialogue>\n')
								xml.append('<dialogue id= "'+str(dialogue)+'" n_utterances= "'+str(num_utterance)+'">')
#						print speakers
#						print contexts
#						print utterances
							for sp in range(0,len(speakers)):
								xml.append(speakers[sp])
								xml.append(contexts[sp])
								xml.append(utterances[sp])
							speakers = []
							contexts = []
							utterances = []
							num_utterance = 0
				except:
		  			continue

			xml_file = open(out_xml+movie+".xml",'w')		
			for line in xml:
				xml_file.write(line.encode('utf-8')+"\n")

			xml_file.close()

	def pre_process(self,raw_text):
		preprocess_all_text = {}
		for movie in raw_text.keys():
			preprocess_all_text[movie] = []
			text = raw_text[movie]
			preprocess_text = []
			for i  in range(0,len(text)):

				try:
					text[i] = text[i].encode()

					# speaker boundries
					if len(text[i]) - len(text[i].lstrip()) == 4:
						text[i] = text[i].replace("\t\t\t\t","**speaker**")
					if text[i].startswith("                         "):
						text[i] = text[i].replace("                         ","**speaker**")
					
					# dialgoue boundries
					if "INT." in text[i]:
						text[i] = text[i].replace("INT.","**dialgoue_change**")
					if "EXT." in text[i]:
						text[i] = text[i].replace("INT.","**dialgoue_change**")

					# start points
					if "FADE IN:" in text[i]:
						text[i] = text[i].replace("FADE IN:","**start**")
					if "OMIT" in text[i]:
						text[i] = text[i].replace("OMIT","**start**")

					# end points
					if "FADE OUT" in text[i]:
						text[i] = text[i].replace("FADE OUT","**end**")

					preprocess_text.append(text[i])
				except:
					continue

			preprocess_all_text[movie] = preprocess_text
		
		return preprocess_all_text

if __name__ == "__main__":
	parser = ScriptParser()
	## names in this list should satisfy URL : 
	# TODO : replace this all movie crawler
	raw_text = parser.fetch_data(["12-Monkeys","Walk-to-Remember,-A","Hellboy"])
	preprocessed_text = parser.pre_process(raw_text)
	parser.text2xml(preprocessed_text)
