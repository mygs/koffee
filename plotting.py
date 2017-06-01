#!/usr/bin/python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        width = rect.get_width()
        ax.text(1.08*width,rect.get_y() + height/2.,
                "${:.2f}".format(width),
                ha='center', va='center')


fig, ax = plt.subplots()

df = pd.read_csv('./data/capsule-prices-20170520.csv', delimiter=';')
df_filtered = df[(df.date == 20170520) & (df.name == 'Ristretto')].sort_values(['brl'], ascending=False)
y_pos = np.arange(len(df_filtered['country']))
rec = ax.barh(y_pos, df_filtered['brl'].as_matrix(), linewidth=0, align='center', color='#72D776')
ax.set_yticks(y_pos)
ax.set_yticklabels(df_filtered['country'].as_matrix())
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel('Ristretto Capsule Price')
ax.set_title('How much Ristretto capsule cost around the world?')

autolabel(rec)

plt.show()
