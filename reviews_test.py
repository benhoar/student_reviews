import pandas as pd
import numpy as np
import glob
import re
import os
import subprocess
import random as r
from matplotlib import pyplot as plt
import statistics as stat
from predict_2 import Score
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer as vader
#Comments written on 10/27/2020
#this class aids caller in obtaining reviews from raw data
#CSVs and subsequently parses and scores all review phrases
#A standard use of this object will follow the progression:
#Make Object(pass surname of instructor) --> call get_reviews
# --> call split_statements --> call score_all

class Reviews:
    def __init__(self, name):
        self.name = name
        #class instantiated with name alone, reviews must be in folder of following format
        self.files ='Reviews/' + name + '/*.csv' 
        
    #this function converts csvs into data frame
    def get_reviews(self, path=None): 
        reviews = pd.DataFrame(columns=['Reviews']) #makes empty DF w one column
        if (path is None): path = self.files
        for file in glob.glob(path): #iterate through directory with files
            t_frame = pd.read_csv(file) #make temp DF from current file
            try:
                t_frame = t_frame.filter(regex='^Please',axis=1) #rev col starts with "Please"
                #t_frame = t_frame.filter(regex='^Reviews',axis=1) #rev col starts with "Please"
            except:
                print("There is an issue with file: " + file) #revs in file not labelled as expected
                continue #move on to next file
            t_frame.columns = ['Reviews']
            t_frame = t_frame[(t_frame['Reviews'] != '[IMAGE]') & (t_frame['Reviews'] != None)] #remove empty revs
            t_frame.reset_index(inplace=True, drop=True)
            #this loop replaces common periods which would interfere with phrase splitting, replacements instead
            #of translations because some periods need to be maintained for the later splitting process
            for i in range(len(t_frame)):
                phrase = str(t_frame.loc[i]['Reviews'])
                txt = phrase.strip()
                if "T.A." in txt: txt = txt.replace("T.A.","TA")
                if "Mr." in txt: txt = txt.replace("Mr.","Mr")
                if "Dr." in txt: txt = txt.replace("Dr.","Dr")
                if "i.e." in txt: txt = txt.replace("i.e.", "ie")
                if "e.g." in txt: txt = txt.replace("e.g.", "eg")
                if "Prof." in txt: txt = txt.replace("Prof.", "prof")
                if "prof." in txt: txt = txt.replace("prof.", "prof")
                if "Ex." in txt: txt = txt.replace("Ex.", "Ex")
                reviews.loc[len(reviews)] = txt
        return reviews
    
    #this function splits statements e.g. "Ben is ok, but he sucks" to
    #"Ben is ok"  ...  "but he sucks" which were considered independent
    def split_statements(self, reviews):
        statements = []
        stud_nums = [] #track who statement belongs to for student averages
        for i, txt in enumerate(reviews['Reviews']):
            txt = re.split("(?=(?:but))|(?<=[.?!])\s+", txt) #split on but and punctuation
            for phrase in txt:
                if (len(phrase) != 0): 
                    phrase = re.sub("â€™", "'", phrase)
                    phrase = phrase.strip()
                    phrase = phrase.strip(',')
                    statements.append(phrase)
                    stud_nums.append(i)
        to_ret = pd.DataFrame(columns=['Reviews', 'Student'])
        to_ret['Reviews'] = statements
        to_ret['Student'] = stud_nums
        to_ret.dropna(inplace=True)
        return to_ret
           
    #make call to the gcp api for each phrase, sort out the relevant scores, send them back if both scores provided
    #or send back None if there was some error
    #this function is not called from this class, it is intended for client to test individual phrases
    def score_phrase(self, phrase):
        scorer = Score() #this is calling a .py file that contains code calling google SA API
        try:
            score = scorer.get_prediction(phrase)
        except:
            print("Continued error with: " + phrase)
        return score
    #this is a value that will be used to check 0 scores before adding them to the output file
    def vader_scores(self, reviews):
        analyser = vader()
        score = lambda x: analyser.polarity_scores(x).get('compound')
        reviews['Vader'] = reviews.apply(lambda x: score(x.Reviews), axis=1)
        return
    #this is a function that is called directly from client program, passed parsed reviews, scores them
    #the returned DF should almost always be saved by the client to avoid having to score again in future
    def score_all(self, reviews, dummy_run=False):
        to_ret = pd.DataFrame(columns=['Reviews', 'Score', 'Length', 'Student'])
        errs = []
        for i in range(len(reviews['Reviews'])):
            txt = reviews.loc[i]['Reviews']
            scorer = Score()
            try:
                if (not dummy_run):
                    score = scorer.get_prediction(txt) #function call
                else:
                    score = [round(4*r.random()), r.random()] #DUMMY SCORING
                if(score <= 4): #sometimes google gives a score of 10, this is to ensure a valid score
                    to_ret.loc[len(to_ret)] = [txt, score, len(txt), reviews.loc[i]['Student']]
            except Exception as e:
                print('error with phrase: ' + txt)
                print(e)
                errs.append([txt, len(txt), reviews.iloc[i]['Student']])
        self.__err_checks(errs, to_ret)
        self.vader_scores(to_ret)
        to_ret['Score'] = to_ret.apply(lambda x: x.Score + 1, axis=1)
        return to_ret

    def __err_checks(self, errs, reviews):
        for err in errs:
            try:
                score = Data.score_phrase(err[0])
                err.insert(1, score)
                reviews.loc[len(reviews)] = err
            except Ecxeption as e:
                print('phrase failed: ' + err)
                print('Error: ' + e)
        return