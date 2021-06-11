import seaborn as sns
import pandas as pd
from dateutil import parser
import matplotlib.pyplot as plt
from pathlib import Path

Path("results").mkdir(exist_ok=True)


df = pd.read_csv("data/01-throttling2.tsv", sep = '\t', header=None)
def to_date(item):
    return parser.parse(item)
df[0] = df[0].apply(to_date)
df.rename(columns = {0:'timestamp', 1: 'cpu_temp', 3: 'cpu_frequency'}, inplace = True)
print(df)

fig, ax1 = plt.subplots() # initializes figure and plots
ax2 = ax1.twinx() # applies twinx to ax2, which is the second y axis. 

sns.set_theme(style="darkgrid")
sns.lineplot(x = 'timestamp', y = 'cpu_temp', ax = ax1, color = 'red', data=df) # plots the first set of data, and sets it to ax1. 
sns.scatterplot(x = 'timestamp', y = 'cpu_frequency', color = 'blue', ax = ax2, data=df) # plots the second set, and sets to ax2. 

# these lines add the annotations for the plot. 
ax1.set_xlabel('time')
ax1.set_ylabel('°C', color='r')
ax2.set_ylabel('Hz', color='b')

plt.savefig('results/01-throttling.png')