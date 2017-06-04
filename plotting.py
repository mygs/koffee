#!/usr/bin/python
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import platform

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        width = rect.get_width()
        ax.text(width+0.08,rect.get_y() + height/2.,
                "${:.2f}".format(width),
                ha='center', va='center')
print ('python version '+platform.python_version())
fig, ax = plt.subplots()
os.chdir(sys.path[0]) # change working directory to script directory
df = pd.read_csv('./data/capsule-prices-20170603.csv', delimiter=';')
df_filtered = df[(df.date == 20170603) & (df.name == 'Ristretto')].sort_values(['brl'], ascending=False)
countries = df_filtered['country'].as_matrix()
n_countries = len(countries)
y_pos = np.arange(n_countries)
prices = df_filtered['brl'].as_matrix()
rec = ax.barh(y_pos, prices, linewidth=0, align='center', color='#72D776')
xmin = prices.min() - (prices.max() - prices.min())*.08
xmax = prices.max() + (prices.max() - prices.min())*.16
ax.set(xlim=[xmin,xmax])
ax.set_yticks(y_pos)
ax.set(ylim=[-1,n_countries+1])
ax.set_yticklabels(countries)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel('Ristretto Capsule Price')
ax.set_title('How much Ristretto capsule cost around the world?')
autolabel(rec)
plt.show()
