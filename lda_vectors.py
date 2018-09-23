from unidecode import unidecode
import pickle
         
import nltk

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.model_selection import GridSearchCV

import random
import numpy as np

chatbot_path = '/home/myrto/pink_dir/github/lda_chatbot/myrto-tsokanaridou-chatbot/'
data_file_path = '/home/myrto/pink_dir/github/LDA_pseudodocuments_clear.txt'

def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        message = "Topic #%d: " % topic_idx
        message += " ".join([feature_names[i]
                             for i in topic.argsort()[:-n_top_words - 1:-1]])
        print(message)
    print()
    

stop_words = set({'make','makes','just','does','newlinechar','before', 'de', 'bill', 'give', 'afterwards', 'what', 'never', 'seemed', 'yet', 'it', 'becomes', 'eleven', 'must', 'rather', 'has', 'at', 'beforehand', 'to', 'none', 'sometime', 'ever', 'found', 'without', 'several', 'since', 'through', 'hundred', 'us', 'hence', 'for', 'ourselves', 'whither', 'yourselves', 'least', 'whoever', 'twelve', 'part', 'very', 'you', 'been', 'beyond', 'however', 'etc', 'per', 'seem', 'whence', 'with', 'amongst', 'last', 'enough', 'show', 'thick', 'twenty', 'some', 'ltd', 'wherein', 'sincere', 'interest', 'take', 'anyone', 'himself', 'because', 'else', 'move', 'describe', 'inc', 'over', 'thus', 'is', 'ten', 'he', 'such', 'there', 'whole', 'nor', 'someone', 'whom', 'another', 'thence', 'do', 'become', 'becoming', 'everywhere', 'had', 'own', 'or', 'thereby', 'un', 'your', 'her', 'became', 'somehow', 'full', 'three', 'same', 'be', 'if', 'otherwise', 'a', 'mill', 'should', 'throughout', 'anyway', 'others', 'due', 'still', 'that', 'its', 'itself', 'few', 'those', 'where', 'them', 'no', 'along', 'ie', 'therefore', 'put', 'both', 'already', 'fire', 'not', 'thereupon', 'whereafter', 'sixty', 'also', 'find', 'as', 'onto', 'something', 'get', 'they', 'top', 'was', 'nine', 'the', 'we', 'this', 'during', 'their', 'might', 'first', 'being', 'eg', 'out', 'nevertheless', 'hereby', 'well', 'back', 'latter', 'noone', 'down', 'six', 'perhaps', 'seeming', 'then', 'whereupon', 'and', 'under', 'via', 'next', 'could', 'many', 'whenever', 'while', 'she', 'please', 'everyone', 'front', 'keep', 'which', 'behind', 'empty', 'my', 'cry', 'former', 'together', 'two', 'anywhere', 'elsewhere', 'fifty', 'cant', 'across', 'each', 'almost', 'every', 'hers', 'i', 'our', 'within', 'mostly', 'forty', 'except', 'about', 'four', 'on', 'may', 'amount', 'who', 'can', 'into', 'made', 'go', 'once', 'hereafter', 'other', 'all', 're', 'nothing', 'around', 'whatever', 'when', 'seems', 'how', 'thereafter', 'therein', 'although', 'see', 'up', 'formerly', 'are', 'neither', 'against', 'side', 'alone', 'more', 'were', 'yourself', 'couldnt', 'ours', 'too', 'whereas', 'yours', 'further', 'from', 'above', 'would', 'these', 'any', 'am', 'have', 'anyhow', 'hasnt', 'here', 'latterly', 'though', 'call', 'between', 'cannot', 'detail', 'often', 'sometimes', 'mine', 'nowhere', 'toward', 'until', 'towards', 'me', 'only', 'namely', 'whether', 'system', 'bottom', 'fill', 'again', 'much', 'third', 'somewhere', 'myself', 'by', 'amoungst', 'his', 'fifteen', 'even', 'one', 'among', 'nobody', 'most', 'serious', 'meanwhile', 'now', 'whose', 'after', 'less', 'an', 'co', 'name', 'of', 'upon', 'besides', 'everything', 'hereupon', 'whereby', 'why', 'beside', 'con', 'off', 'anything', 'done', 'eight', 'thru', 'themselves', 'moreover', 'below', 'either', 'wherever', 'always', 'thin', 'herself', 'than', 'him', 'in', 'indeed', 'five', 'will', 'herein', 'but', 'so'})    


data_file = open(data_file_path , 'r')
lines = data_file.readlines()
print(len(lines))
random.Random(78).shuffle(lines)
data_file.close()

#Vectorizing
data_vectorizer = CountVectorizer(max_df = 0.98,
                                max_features = 50000,
                                stop_words=stop_words)

vectorized_data = data_vectorizer.fit_transform(lines)
data_feature_names = data_vectorizer.get_feature_names()

# #GRID SEARCH for k topics
# k_topics = {'n_components':[10, 20, 30, 40, 50, 60, 70, 80]}

# lda = LatentDirichletAllocation(doc_topic_prior=0.1, topic_word_prior=0.01, learning_method = 'online', random_state = 42)

# model = GridSearchCV(lda, param_grid=k_topics)

# model.fit(vectorized_data)

# #Results
# print("Best Model's Params: ", model.best_params_)
# print("Best Log Likelihood Score: ", model.best_score_)


#APPLY LDA for 40 topics

lda = LatentDirichletAllocation(n_components=40, doc_topic_prior=0.1, topic_word_prior=0.01, learning_method = 'online', random_state = 42)

lda.fit(vectorized_data)

best_lda = lda

#Create LDA_vectors for (sub)words of the vocabulary
from_list = []
to_list = []

with open(chatbot_path + 'data/vocab.bpe.from') as f:
    for line in f:
        from_list.append(line.strip())
f.close()

wnl = nltk.stem.WordNetLemmatizer()

for id in range(len(from_list)):
    word = from_list[id]
    word = wnl.lemmatize(unidecode(word).replace('▁', '').replace('#', '').lower())
    to_list.append(word)
    
test = to_list

vocabulary_vectorized = data_vectorizer.transform(to_list)
vocabulary_topic_dist = np.matrix(best_lda.transform(vocabulary_vectorized))

with open('LDA_vectors.pickle', 'wb') as h:
    pickle.dump(vocabulary_topic_dist, h)
