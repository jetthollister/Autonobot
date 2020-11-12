import re
from textblob import TextBlob

# Sentiment: -1 = negative, 1 = positive
# Subjectivity: 0 = objective, 1 = subjective

sample = ('Time for @hallofstairs the unions to come through with '
          'their promises'
          ' of a general strike if Trump attempts a coup to subvert'
          ' democracy. He is doing it right now. Everybody out. STRIKE!'
          ' #GeneralStrike #TrumpOutNow #EverybodyOut #NoFascistUSA '
          '#SaveDemocracy')


def regTokenize(text):
    marker = text.replace('#', 'QT145')
    token = re.compile(r'\w+')
    words = token.findall(marker)
    return words


def splitHashtags(token):
    if 'QT145' in token:
        token = token.replace('QT145', '')
        return re.sub(r"([A-Z])", r" \1", token).split()

    return token


def recompile(group):
    res = []
    for i, item in enumerate(group):
        if type(item) == list:
            [res.append(j.lower()) for j in item]
        else:
            res.append(item.lower())

    return ' '.join(res)


def getSentiment(text):
    tokens = regTokenize(text)
    tokens = [splitHashtags(word) for word in tokens]
    recompiled = recompile(tokens)

    sent, subj = TextBlob(recompiled).sentiment

    return sent, subj
