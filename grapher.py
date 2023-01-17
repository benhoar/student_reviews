from matplotlib import pyplot as plt
import numpy as np

class Histogram:
    def __init__(self, path, data, color, title, path_end=""):
        self.path = path
        self.data = data
        self.color = color
        self.title = title
        self.path_end = path_end
        self.stats = self.__calculate_stats()
        self.histogram()
        
    def __calculate_stats(self):
        average = np.dot(list(self.data.values()),list(self.data.keys()))/sum(self.data.values())
        vals = []
        [vals.append(key) for key in self.data.keys() for i in range(self.data.get(key))]
        stdev = np.std(vals)
        return average, stdev
        
    def histogram(self):
        for val in range(len(self.data.keys())):
            self.data[val+1] = self.data.get(val+1) if val+1 in self.data.keys() else 0
        bar = plt.bar(self.data.keys(), self.data.values(), color=self.color, width=0.6, alpha=0.8)
        plt.xlabel("Score", size=12)
        plt.ylabel("Count", size=12)
        plt.title(self.title, size=14)
        for rect in bar:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width()/2, height, '%d' % int(height), ha='center', va='bottom', size=12)
        plt.ylim([0, (0.3*(max(self.data.values()))+max(self.data.values()))]) #tries to avoid annotation interference with plot bars
        #statistics to include in corner
        average, stdev = self.stats
        
        plt.annotate('Avg. = ' + str(round(average,2)) + '\n' + 
                     'Std. Dev. = ' + str(round(stdev,2)), xy=(0.02, 0.88), xycoords='axes fraction', size=12)
        #plt.savefig(self.name + self.path_end + '_histo.png', dpi=200)
        plt.savefig(self.path + self.path_end + '_histo.png', dpi=200)
        plt.close()
        return 