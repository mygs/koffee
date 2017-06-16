#!/usr/bin/python
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np
import platform

capsule = 'Ristretto'
date = 20170616

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        width = rect.get_width()
        ax.text(width+0.06,rect.get_y() + height/2.,
                "${:.2f}".format(width),
                ha='center', va='center')
print ('python version '+platform.python_version())
rcParams.update({'figure.autolayout': True})
os.chdir(sys.path[0]) # change working directory to script directory
fig, ax = plt.subplots()
df = pd.read_csv('./data/capsule-prices-'+str(date)+'.csv', delimiter=';')
df_filtered = df[(df.date == date)&(df.name == capsule)&(df.fx == 'BRL')].sort_values(['price'], ascending=True)
print(df_filtered)
countries = df_filtered['country'].as_matrix()
n_countries = len(countries)
y_pos = np.arange(n_countries)
prices = df_filtered['price'].as_matrix()
rec = ax.barh(y_pos, prices, linewidth=0, align='center', color='#72D776',zorder=3)

xmin = prices.min() - (prices.max() - prices.min())*.08
xmax = prices.max() + (prices.max() - prices.min())*.16
img = plt.imread("img/background.png")
#[left, right, bottom, top]
ax.imshow(img, aspect='auto', zorder=0, extent=[xmin, xmax,-1, n_countries])
#ax.set(xlim=[xmin,xmax])
#ax.set(ylim=[-1,n_countries])
ax.set_yticks(y_pos)
ax.set_yticklabels(countries)
#ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel(capsule+' Capsule Price')
ax.set_title('How much '+capsule+' capsule cost around the world?')
autolabel(rec)

plt.show()
