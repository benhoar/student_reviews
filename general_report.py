import pandas as pd
import numpy as np
import glob
import re
import os
import subprocess
import random as r
from matplotlib import pyplot as plt
import statistics as stat
import PIL
from wordcloud import WordCloud, ImageColorGenerator
import numpy as np
from PIL import Image
from reviews_test import Reviews
from grapher import Histogram
model = 'projects/919577446005/locations/us-central1/models/TST2565505874252529664'

#Comments written on 10/27/2020
#This class is intended to make the general report associated with the reviews
#scored and provided by the reviews.py Reviews class. The "general report"
#considered here is the csv file with all reviews. The graphing functions here
#are also used to generate the LaTeX report that is the focus of this project
#as of 10/27/2020

#Note: This class and the word_report class share redundancy, they may need to be
#made more succinct

class Report: 
    def __init__(self, revs, file_name):
        self.revs = revs
        self.file_name = file_name
        #we will always need the histogram data
        self.hist_data = self.__get_histo_data()
        #self.make_report()
        Histogram(self.file_name, self.hist_data, 'red', 'Per-Student Review Summary')
        self.hist_data_raw = dict(self.revs['Score'].value_counts())
        Histogram(self.file_name, self.hist_data_raw, 'red', 'Summary of Scores', path_end='raw')

    #this function returns the histogram data for the student averaged scores
    #if a student makes 5 statements, those will all be scored and then averaged
    def __get_histo_data(self):
        hist_data = {1:0, 2:0, 3:0, 4:0, 5:0}
        start = 0
        student_sum = 0
        for i in range(len(self.revs)):
            #this tab level: if end of DF or new student, compute average and add to DF, either add to sum or start new sum
            if ((i == len(self.revs)-1) or (self.revs.loc[i]['Student'] != self.revs.loc[start]['Student'])):
                avg = round(student_sum/(i-start)+.01)
                hist_data[avg] += 1
                start = i
                student_sum = 0
            student_sum += self.revs.loc[i]['Score']
        #averages must be whole number (scoring system is 0-4 ints, +0.01 biases all x.5s up
        avg = round(student_sum/(i-start+1)+0.01)
        hist_data[avg] += 1
        return hist_data
    
    def score_distribution_graphs(self, og_scores, hist_data):
        #og_scores = grab_og_scale_scores('TA', 'Reviews/' + name + '/*.csv')
        og_scores['Instructor'] /= 9
        og_scores_data = dict(og_scores['Instructor'].value_counts())
        keys = [val/max(hist_data.keys()) + 0.02 for val in hist_data.keys()]
        plt.bar(keys, hist_data.values(), width=0.1, color='dodgerblue', alpha=0.7, label='Text Data')
        plt.bar(og_scores_data.keys(), og_scores_data.values(), width=0.1, color='red', alpha=0.6, label='Student Scores \nof Instructor')
        plt.title('Student Scores From Text Sentiment and Raw Data')
        plt.xlabel('Normalized Scores (Text: 1-5, UCLA: 0-9)')
        plt.ylabel('Number of Students')
        plt.legend(loc='upper left')
        plt.savefig(self.file_name + 'distribution.png', dpi=200)
        plt.close('all')
        return
    
    def word_graph(self, stats):
        nums = stats.values()
        avs =  [item[0] for item in nums]
        stds = [round(item[1],2) for item in nums]
        bar = plt.bar(stats.keys(), avs, color='red', width=0.6, alpha=0.8)
        plt.xlabel("Term From Reviews", size=12)
        plt.ylabel("Average Score", size=12)
        plt.title("Average Score of Common Topics", size=14)
        for i, rect in enumerate(bar):
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width()/2, height, 'StDev\n' + '%.2f' % stds[i], ha='center', va='bottom', size=8)
        plt.ylim([0, (0.15*(max(avs))+max(avs))])
        plt.xticks(rotation=40)
        plt.gcf().subplots_adjust(bottom=0.3)
        plt.savefig(self.file_name + 'word_averages.png', dpi=300)
        plt.close()
        return
    
    def word_cloud(self, words, name):
        mask = np.array(Image.open('./flask.png'))
        for_cloud = ""
        for word in words: for_cloud = for_cloud + word + " "
        cloud = WordCloud(max_font_size=50, max_words=150, background_color="white", mask=mask)
        cloud.generate(for_cloud)
        plt.figure()
        plt.imshow(cloud, interpolation='bilinear')
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(self.file_name + 'word_cloud.png', dpi=1000)
        plt.close()
        return