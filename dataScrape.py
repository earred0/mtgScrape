import pandas as pd
import matplotlib.pyplot as plt
import pylab
import matplotlib as mpl

mpl.rcParams['font.size'] = 7.0
dataOne = pd.read_csv("historyOfSet.csv")
sets = dataOne.set.unique()

fig, axes = plt.subplots(nrows=7, ncols=4)

sets = dataOne.set.unique()
rarityNames = ["Common", "Uncommon", "Rare", "Mythic Rare"]

for ax, x in zip(axes.flat, sets):
    counts = dataOne.loc[dataOne["set"] == x, "rarity"]
    wedges, texts, autotexts = ax.pie(counts.value_counts(), autopct='%.2f', pctdistance=1.32,
                                      colors=['#17202A', '#ECF0F1', '#D4AC0D', '#D35400'])
    ax.set(ylabel='', title=x[-4:-1], aspect='equal')
    centre_circle = plt.Circle((0, 0), 0.5, fc='white')
    plt.sca(ax)
    ax.fig = plt.gcf()
    ax.fig.gca().add_artist(centre_circle)
    plt.setp(autotexts, size=6)
plt.subplots_adjust(top=0.972,
                    bottom=0.014,
                    left=0.005,
                    right=0.995,
                    hspace=0.41,
                    wspace=0.0)
fig.legend(wedges, rarityNames, loc="right")
plt.show()
