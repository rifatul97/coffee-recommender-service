# @app.route('/get_topics', methods=['GET'])
# def getTopics():
#     topics = get_topics(model, tfidfVect.get_feature_names_out(), 9);
#     display_topics = ''
#     for topic in topics:
#         print('topic: \n')
#         print(''.join(map(str, topic)))
#
#
#     return 'displayed!'

# ----------------------------------------------------------------------

# def get_topics(model, feature_names, no_top_words, topic_names=None):
#     topics = []
#     for ix, topic in enumerate(model.components_):
#         if not topic_names or not topic_names[ix]:
#             print("hello")
#             # print("\nTopic ", ix)
#         else:
#             print("\nTopic: '", topic_names[ix], "'")
#         topics.append(", ".join([feature_names[i]
#                           for i in topic.argsort()[:-no_top_words - 1:-1]]))
#     return topics

# ---------------------------------------------------------------------------------

# tfidfVect = TfidfVectorizer(min_df=10)
# tfidf_blind = tfidfVect.fit_transform(coffee_reviews)
#
# nmf_tfidfblind = NMF(9)
# blindtfidf_topic = nmf_tfidfblind.fit_transform(tfidf_blind)
# blindtopic_tfidf = pd.DataFrame(nmf_tfidfblind.components_.round(3),
#                                 #              index = ["component_1","component_2"],
#                                 columns=tfidfVect.get_feature_names_out())
# model = nmf_tfidfblind
# tfidfVect = tfidfVect