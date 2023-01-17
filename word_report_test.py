import pandas as pd
import numpy as np
import glob
import re
import os
import subprocess
import random as r
from matplotlib import pyplot as plt
import statistics as stat
import nltk
from nltk.corpus import stopwords
import string
model = 'projects/919577446005/locations/us-central1/models/TST2565505874252529664'

#this class generates reports that are derived from a dataframe consisting of all student
#comments based on lists of terms that are requested. Can be used to filter all terms
#about homework from a body of general reviews, for example.

class Word_Report:
    def __init__(self, revs, file_name, words):
        self.words = words
        self._og_frame = revs.copy()
        self.name = file_name
        self.file_name = 'Reviews/' + file_name + '/Results/word_reports/' + (self.words[0]).strip()
        self.revs = revs
        self.revs = self.filter_keyword()
        
    def filter_keyword(self):
        self.words = [word.lower() for word in self.words] #lower case reduces edge cases
        self.revs['Reviews'] = self.revs['Reviews'].str.lower()
        frame = pd.DataFrame(columns=self.revs.columns.values)
        for i in range(len(self.revs)):
            #if any of the words from the words list is in the review, keep it
            if any(word in str(self.revs.loc[i]['Reviews']) for word in self.words):
                frame.loc[len(frame)] = self.revs.iloc[i][:]
        return frame
            
    #this provides the statistics about the frame consisting of filtered reviews
    #this function is public because all the word reports for a given instructor
    #will be considered for a summary figure in teh final LaTeX report
    def word_stats(self):
        hist_data = dict(self.revs['Score'].value_counts())
        average = round(np.dot(list(hist_data.values()),list(hist_data.keys()))/sum(hist_data.values()), 2)
        vals = []
        [vals.append(key) for key in hist_data.keys() for i in range(hist_data.get(key))]
        stdev = round(np.std(vals), 2)
        return (average, stdev)
    
    def histo_word(self):
        temp_hist = dict(self.revs['Score'].value_counts())
        hist_data = {1:0, 2:0, 3:0, 4:0, 5:0}
        #loop either uses the value resulting from value counts or a 0, ensures all keys show in graph
        for key in hist_data.keys():
            hist_data[key] = hist_data.get(key) if key not in temp_hist.keys() else temp_hist.get(key)
        #print(str(self.words[0]) + " " + str(hist_data))
        bar = plt.bar(hist_data.keys(), hist_data.values(), color='dodgerblue', width=0.6, alpha=0.8)
        plt.xlabel("Comment Score", size=12)
        plt.ylabel("Number of Comments", size=12)
        plt.title("Summary of Scores for " + self.words[0], size=14)
        for rect in bar: #annotates the bar graphs with their counts at top of each bar
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width()/2, height, '%d' % int(height), ha='center', va='bottom', size=12)
        if not hist_data.values(): #if the word report is empty... just break... possibly look into cleaner method here
            plt.close()
            return
        plt.ylim([0, (0.3*(max(hist_data.values()))+max(hist_data.values()))])
        #statistics to include in corner
        stats = self.word_stats()
        plt.annotate('Avg. = ' + str(stats[0]) + '\n' + 'Std. Dev. = ' + str(stats[1]), xy=(0.02, 0.88), xycoords='axes fraction', size=12)
    
        plt.savefig(self.file_name + '.png', dpi=200)
        plt.close()
        return
    
    def __scrub_zeroes(self, data):
        data = data.drop(data[(data.Score == 0) & (data.Vader >= 0)].index)
        return
    #This generates a csv with data for tables shown in final LaTeX report
    def latex_table(self, data, path=None):
        self.__scrub_zeroes(data)
        if (path is None): #if a table is not to go in word_reports directory, that can be explicitly defined
            path = self.file_name
        x = 15 #this is 5 less than the approximate safe (formatting wise) max length of a table

        if (len(data) < x+5): #if filtered table is less than 20, stop, just make the table
            data.to_csv(path + '_latex.csv', index=False)
            return
        #following three lines calculate proportional representation of each score for the table
        counts = dict(data['Score'].value_counts())
        total_scores = sum(counts.values())
        reps = {score : round((props/total_scores),2) for (score,props) in counts.items()}
        latex_table = pd.DataFrame(columns=['Review', 'Score'])
        for val in counts.keys():
            #take phrases with certain lengths
            temp = data[(data['Score'] == val) & (data['Length'] > 20) & (data['Length'] <= 190)]
            temp.reset_index(inplace=True, drop=True)
            #if 20% of the DF is score x, 20% of table should be score x
            rep_group_size = round(reps.get(val)*x)
            #following two if statements say, if representation is small enough, just include them
            if ((val == 5 or val == 2) and (len(temp) < 3 or rep_group_size == 0)):
                indices = range(len(temp))
                indices = indices[:3]
            elif ((val == 3 or val == 4 or val == 1) and (len(temp) < 2 or rep_group_size == 0)):
                indices = range(len(temp))
                indices = indices[:2]
            #take random statements until we have a full set of statements
            else:
                indices = set()
                while (len(indices) < rep_group_size):
                    v = round((len(temp)-1)*r.random())
                    indices.add(v)
            for index in indices:
                latex_table.loc[len(latex_table)] = [temp.iloc[index]['Reviews'], temp.iloc[index]['Score']]
        latex_table.sort_values(by='Score', ascending=False, inplace=True)
        latex_table.to_csv(path + '_latex.csv', index=False)
        return

    #make csv of the word filtered DF
    def make_word_report(self):
        self.revs.sort_values(by=['Score','Length'], ascending=False, inplace=True)
        self.revs.reset_index(inplace=True, drop=True)
        self.latex_table(self.revs.copy())
        self.revs.drop('Length', inplace=True, axis=1)
        #print(word + ' reviews can be found in: ' + word + '_report.csv')
        full_file_name = self.file_name + '.csv'
        rep = open(full_file_name, 'w')
        rep.write('Below is the report for keywords: ' + str(self.words) + '\n\n')
        rep.write('Average Score: ' + str(round(self.revs['Score'].mean(),2)) + '\n')
        rep.write('Std. Dev. Score: ' + str(round(self.revs['Score'].std(),2)) + '\n\n')
        rep.close()
        self.revs.to_csv(full_file_name, mode='a', index=False)
        self.histo_word()
        return 

    #this function returns the top words of in a corpus minus those already accounted for manually
    def top_words(self, names, x):
        #stop words are essentially meaningless words, we add the instructor names as they are already accounted for
        stop_words = stopwords.words('english')
        stop_words.append(names[0].lower())
        stop_words.append(names[1].lower())
        word_counts = {}
        #take all statements from DF PRE FILTERING and calculate word counts
        for i in range(len(self._og_frame)):
            phrase = str(self._og_frame.loc[i]['Reviews']).lower()
            phrase = phrase.translate(str.maketrans('', '', string.punctuation))
            words = phrase.split()
            for word in words:
                if (not word in stop_words):
                    word_counts[word] = 1 + word_counts.get(word, 0) 
        word_counts = {word : count for word, count in sorted(word_counts.items(), key=lambda item: item[1], reverse=True)}
        keys = list(word_counts.keys())
        return keys[:x]