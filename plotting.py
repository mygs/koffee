#!/usr/bin/python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots()

df = pd.read_csv('./data/capsule-prices-20170520.csv', delimiter=';')
df_filtered = df[(df.date == 20170520) & (df.name == 'Ristretto')]
print(df_filtered[['country', 'brl']].as_matrix())

y_pos = np.arange(len(df_filtered['country']))
ax.barh(y_pos, df_filtered['brl'].as_matrix(), align='center', color='green')
ax.set_yticks(y_pos)
ax.set_yticklabels(df_filtered['country'].as_matrix())
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel('Ristretto Capsule Price')
ax.set_title('How much Ristretto capsule cost around the world?')
plt.show()
