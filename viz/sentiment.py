import seaborn as sns
import matplotlib.pyplot as plt
import pickle
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

sns.set_context("poster")
plt.style.use("dark_background")

sample = ('Time for @hallofstairs the unions to come through with '
          'their promises'
          ' of a general strike if Trump attempts a coup to subvert'
          ' democracy. He is doing it right now. Everybody out. STRIKE!'
          ' #GeneralStrike #TrumpOutNow #EverybodyOut #NoFascistUSA '
          '#SaveDemocracy')


def getSentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(text)
    return score['compound']


def plotSentiment(scores, topic):

    f = plt.figure(figsize=(12, 7))

    y, _, _ = plt.hist(scores, bins=15, density=True)
    plt.clf()

    n, bins, patches = plt.hist(scores, bins=15,
                                facecolor='#2ab0ff',
                                edgecolor='white',
                                linewidth=1, alpha=1,
                                density=True)

    n = n.astype('int')

    for i in range(len(patches)):
        patches[i].set_facecolor(plt.cm.RdBu(i*18))

    ax = sns.kdeplot(scores, color='#D3D3D3')

    ax.set(xlim=(-1.05, 1.05))
    ax.set(ylim=(0, y.max()+(y.max()/10)))

    sns.despine()
    ax.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0])
    ax.set_xticklabels([-1.0, -0.5, 0.0, 0.5, 1.0])

    # Plot formatting
    plt.title(f'Sentiment Density of {len(scores)} "{topic}" Tweets')
    plt.xlabel('Sentiment')
    plt.ylabel('Density')
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    f.savefig('./viz/plots/sentPlot.png', transparent=False)

    # pickle.dump(f, open('./viz/pickles/sentPlot.pickle', 'wb'))

    return
