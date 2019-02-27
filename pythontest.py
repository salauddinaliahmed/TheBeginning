import nltk
from nltk.collections import *

bigram_measures = nltk.collocations.BigramAssocMeasures()
trigram_measure = nltk.collocations.TrigramAssocMeasures()
finder = BigramCollectionFinder.from_words(nltk.corpus.genesis.words('english-web.txt'))

