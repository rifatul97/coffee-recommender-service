# import os
# import re
#
#
# from flask import Flask, render_template, request, jsonify
# from pathlib import Path
# import requests
# import io
# import json
# import redis
# from collections import Counter
# import matplotlib.pyplot as plt
# from gensim.corpora import Dictionary
# from gensim.models import CoherenceModel, Nmf
# from nltk import TweetTokenizer, RegexpTokenizer, SnowballStemmer
# from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
# from sklearn.decomposition import NMF
# from pandas import pandas as pd
# import altair as alt
# from wordcloud import WordCloud
# import wordcloud
# import gensim
#
# alt.renderers.enable('altair_viewer')
#
#
# model = None
# tfidfVect = None
# file_url = "https://raw.githubusercontent.com/rifatul97/coffee-recommender-service/main/data/coffee_reviews_cleaned.txt"
#
#
# # def get_topics(model, feature_names, no_top_words, topic_names=None):
# #     topics = []
# #     for ix, topic in enumerate(model.components_):
# #         if not topic_names or not topic_names[ix]:
# #             print("\nTopic ", ix)
# #         else:
# #             print("\nTopic: '", topic_names[ix], "'")
# #         topics.append(", ".join([feature_names[i]
# #                                  for i in topic.argsort()[:-no_top_words - 1:-1]]))
# #     return topics
#
#
# @app.route('/')
# def home():
#     return "welcome to coffee recommender service"
#
#
# def casual_tokenizer(text):
#     tokenizer = TweetTokenizer()
#     tokens = tokenizer.tokenize(text)
#     return tokens
#
#
# def top_words(topic, n_top_words):
#     return topic.argsort()[:-n_top_words - 1:-1]
#
#
# def topic_table(model, feature_names, n_top_words):
#     topics = {}
#     for topic_idx, topic in enumerate(model.components_):
#         t = (topic_idx)
#         topics[t] = [feature_names[i] for i in top_words(topic, n_top_words)]
#     return pd.DataFrame(topics)
#
#
# def whitespace_tokenizer(text):
#     pattern = r"(?u)\b\w\w+\b"
#     tokenizer_regex = RegexpTokenizer(pattern)
#     tokens = tokenizer_regex.tokenize(text)
#     return tokens
#
#
# # Funtion to remove duplicate words
# def unique_words(text):
#     ulist = []
#     [ulist.append(x) for x in text if x not in ulist]
#     return ulist
#
#
# def process_text(text):
#     text = casual_tokenizer(text)
#     text = [each.lower() for each in text]
#     text = [re.sub('[0-9]+', '', each) for each in text]
#     # text = [expandContractions(each, c_re=c_re) for each in text]
#     text = [SnowballStemmer('english').stem(each) for each in text]
#     # text = [w for w in text if w not in punc]
#     # text = [w for w in text if w not in stop_words]
#     text = [each for each in text if len(each) > 1]
#     text = [each for each in text if ' ' not in each]
#     return text
#
#
# @app.route('/get_recommend_for', methods=['GET'])
# def recommend():
#     bar = request.args.to_dict()
#     args = []
#     for arg in bar.values():
#         print(arg)
#         args.append(arg + " ")
#
#     return ''.join(map(str, args))
#
#
# def get_topics(components, vocab):
#     topic_word_list = []
#     for i, comp in enumerate(components):
#         terms_comp = zip(vocab,comp)
#         sorted_terms = sorted(terms_comp, key= lambda x:x[1], reverse=True)[:7]
#         topic=" "
#         for t in sorted_terms:
#             topic= topic + ' ' + t[0]
#         topic_word_list.append(topic.strip())
#
#     print(topic_word_list)
#     return topic_word_list
#
#
# @app.route('/get_number_of_coffee_reviews', methods=['GET'])
# def get_number_of_coffee_reviews():
#     unpacked_coffee_reviews_json = r.get('coffee_reviews_json').decode('utf-8')
#     unpacked_coffee_roasters_json = r.get('coffee_roasters_json').decode('utf-8')
#     coffee_reviews = json.loads(unpacked_coffee_reviews_json)
#     coffee_roasters = json.loads(unpacked_coffee_roasters_json)
#
#     number_of_coffee_review_text = {"number_of_coffee_reviews": str(len(coffee_reviews))}
#
#     countVect = CountVectorizer(min_df=20)
#     countVect_blind = countVect.fit_transform(coffee_reviews[0:])
#
#     tfidfVect = TfidfVectorizer(min_df=20)
#     tfidf_blind = tfidfVect.fit_transform(coffee_reviews[0:])
#
#     # top_tfidf = pd.DataFrame(tfidf_blind.toarray(), index=coffee_roasters[0:], columns=tfidfVect.get_feature_names())
#     # # print(top_tfidf.stack().reset_index())
#     # top_tfidf = top_tfidf.stack().reset_index()
#     # renamed_top_tfidf = top_tfidf.rename(
#     #     columns={0: 'tfidf', 'level_0': 'coffee_roasters', 'level_1': 'feature_term', 'level_2': 'feature_term'})
#     # top_tfidf_2 = renamed_top_tfidf.sort_values(by=['coffee_roasters', 'tfidf'], ascending=[True, False]).groupby(
#     #     ['coffee_roasters']).head(5)
#     # # print(top_tfidf_2)
#     #
#     # top_tfidf_plusRand = top_tfidf_2.copy()
#     # top_tfidf_plusRand['tfidf'] = top_tfidf_plusRand['tfidf'] + np.random.rand(top_tfidf_2.shape[0]) * 0.0001
#     #
#     # # top_tfidf_plusRand['tfidf'] = top_tfidf_plusRand['tfidf'] + np.random.rand(top_tfidf.shape[0]) * 0.0001
#     #
#     # # base for all visualizations, with rank calculation
#     # base = alt.Chart(top_tfidf_plusRand).encode(
#     #     x='rank:O',
#     #     y='coffee_roasters:N'
#     # ).transform_window(
#     #     rank="rank()",
#     #     sort=[alt.SortField("tfidf", order="descending")],
#     #     groupby=["coffee_roasters"],
#     # )
#     #
#     # # heatmap specification
#     # heatmap = base.mark_rect().encode(
#     #     color='tfidf:Q'
#     # )
#     #
#     # # text labels, white for darker heatmap colors
#     # text = base.mark_text(baseline='middle').encode(
#     #     text='feature_term:N',
#     #     color=alt.condition(alt.datum.tfidf >= 0.23, alt.value('white'), alt.value('black'))
#     # )
#
#     # coffee_reviews_words = []
#     # for review in coffee_reviews:
#     #     coffee_reviews_words.append(process_text(review))
#     #
#     # # print(coffee_reviews_words)
#     #
#     # dictionary = Dictionary(coffee_reviews_words)
#     # # Filter out extremes to limit the number of features
#     # dictionary.filter_extremes(
#     #     no_below=3,
#     #     no_above=0.85,
#     #     keep_n=5000
#     # )
#     #
#     # print(dictionary.values())
#     #
#     # corpus = [dictionary.doc2bow(text) for text in coffee_reviews_words]
#
#     print("corpus-ing" )
#
#
#     # Create a list of the topic numbers we want to try
#     # topic_nums = list(np.arange(9, 36, 3))
#
#     # Run the nmf model and calculate the coherence score
#     # for each number of topics
#     # coherence_scores = []
#     # k_values = []
#     # i = 9
#     #
#     # for num in topic_nums:
#     #     nmf = Nmf(
#     #         corpus=corpus,
#     #         num_topics=num,
#     #         id2word=dictionary,
#     #         chunksize=2000,
#     #         passes=5,
#     #         kappa=.1,
#     #         minimum_probability=0.01,
#     #         w_max_iter=300,
#     #         w_stop_condition=0.0001,
#     #         h_max_iter=100,
#     #         h_stop_condition=0.001,
#     #         eval_every=10,
#     #         normalize=True,
#     #         random_state=42
#     #     )
#     #
#     #     # Run the coherence model to get the score
#     #     cm = CoherenceModel(
#     #         model=nmf,
#     #         texts=coffee_reviews_words,
#     #         dictionary=dictionary,
#     #         coherence='c_v'
#     #     )
#     #
#     #     coherence_scores.append(round(cm.get_coherence(), 5))
#     #     k_values.append(i)
#     #     i += 3
#     #
#     # # Get the number of topics with the highest coherence score
#     # scores = list(zip(topic_nums, coherence_scores))
#     # best_num_topics = sorted(scores, key=itemgetter(1), reverse=True)[0][0]
#     #
#     # print(scores)
#     # print(coherence_scores)
#     # print(k_values)
#     #
#     # print(best_num_topics)
#     #
#     # fig = plt.figure(figsize=(13, 7))
#     # # create the line plot
#     # ax = plt.plot(k_values, coherence_scores)
#     # plt.xticks(k_values)
#     # plt.xlabel("Number of Topics")
#     # plt.ylabel("Mean Coherence")
#     # # add the points
#     # plt.scatter(k_values, coherence_scores, s=120)
#     # # find and annotate the maximum point on the plot
#     # ymax = max(coherence_scores)
#     # xpos = coherence_scores.index(ymax)
#     # best_k = k_values[xpos]
#     # plt.annotate("k=%d" % best_k, xy=(best_k, ymax), xytext=(best_k, ymax), textcoords="offset points", fontsize=16)
#     # # show the plot
#     # plt.show()
#     #
#     # print("done!")
#
#     nmf_tfidfblind = NMF(9)
#     blindtfidf_topic = nmf_tfidfblind.fit_transform(countVect_blind)
#     blindtopic_tfidf = pd.DataFrame(nmf_tfidfblind.components_.round(3),
#                                     #              index = ["component_1","component_2"],
#                                     columns=countVect.get_feature_names_out())
#     # print(blindtopic_tfidf)
#     # get_topics(blindtfidf_topic, tfidfVect.get_feature_names_out(), 3)
#     components_df = pd.DataFrame(nmf_tfidfblind.components_, columns=countVect.get_feature_names_out())
#     top_topics = []
#     for topic in range(components_df.shape[0]):
#         tmp = components_df.iloc[topic]
#         # print(f'For topic {topic + 1} the words with the highest value are:')
#         # print(tmp.nlargest(5))
#         top_topics.append(tmp.nlargest(5))
#         print('\n')
#
#     print(top_topics[0])
#     top_topics_1 = []
#     top_frequency_1 = []
#     for topics in top_topics:
#         topicx = ""
#         for name, val in topics.iteritems():
#             topicx += name + ", "
#         print("topic contains : " + topicx)
#
#
#     for name, val in top_topics[3].iteritems():
#         top_topics_1.append(name)
#         top_frequency_1.append(val)
#
#     df = pd.DataFrame({'word': top_topics_1,
#                        'count': top_frequency_1})
#
#     # method 1: convert to dict
#     data = dict(zip(df['word'].tolist(), df['count'].tolist()))
#
#     # method 2: convert to dict
#     data = df.set_index('word').to_dict()['count']
#
#     print(data)
#
#     # words = np.array(tfidfVect.get_feature_names())
#     # for i, topic in enumerate(nmf_tfidfblind.components_):
#     #     print("Topic {}: {}".format(i + 1, ",".join([str(x) for x in words[topic.argsort()[-10:]]])))
#
#     # get_topics(components, vocab)
#     # components = nmf_tfidfblind.components_
#     # vocab = tfidfVect.get_feature_names()
#     # get_topics(components, vocab)
#     #
#     # print("doneing?!")
#     #
#     # print("start")
#     wc = WordCloud(width=1000, height=600, margin=3, prefer_horizontal=0.7, scale=1, background_color='white',
#                    relative_scaling=0).generate_from_frequencies(data)
#     plt.imshow(wc, interpolation='bilinear')
#     plt.axis("off")
#     plt.show()
#     print("end")
#
#
#     print("done?")
#
#     # wordcloud = WordCloud(width=800, height=800,
#     #                       background_color='white',
#     #                       min_font_size=10).generate(topics)
#     # plt.imshow(wordcloud, interpolation='bilinear')
#     # plt.axis("off")
#     # plt.show()
#
#     # wordcloud = WordCloud().generate(text)
#
#     # Display the generated image:
#
#
#
#     # display the three superimposed visualizations
#     # print((heatmap).properties(width=600))
#     # (heatmap + text).properties(width=720).show()
#
#     # word_list = countVect.get_feature_names_out()
#     # count_list = countVect_blind.toarray().sum(axis=0)
#     #
#     # tfidf_word_list = tfidfVect.get_feature_names_out()
#     # tfidf_count_list = tfidf_blind.toarray().sum(axis=0)
#     #
#     # cnt = Counter()
#     # i = 0
#     # for word in tfidf_word_list:
#     #     cnt[word] = tfidf_word_list[i]
#     #     i += 1
#     #
#     # word_freq = pd.DataFrame(cnt.most_common(50),
#     #                          columns=['words', 'count'])
#     # word_freq.head()
#     #
#     # fig, ax = plt.subplots(figsize=(12, 8))
#     #
#     # # Plot horizontal bar graph
#     # word_freq.sort_values(by='count').plot.barh(x='words',
#     #                                             y='count',
#     #                                             ax=ax,
#     #                                             color="brown")
#     # ax.set_title("Common Feature Words Appeared Throughout the Coffee Reviews")
#     # plt.show()
#
#     return number_of_coffee_review_text
#
##
#
# if __name__ == '__main__':
#     readCoffeeReviewData()
#     app.run()
#
