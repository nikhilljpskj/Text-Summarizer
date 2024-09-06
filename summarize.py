# Importing Libraries
import re
import nltk
import math
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import os

# CLEANING  TEXT 
# Converting the text file into individual sentences which will be our document

def  clean_text(file_name):
    # if not os.path.exists(file_name):
    #     print("File '{}' not found. Creating an empty file.".format(file_name))
    #     with open(file_name, 'w') as f:
    #         f.write('')
    with open(file_name, "r")as file:
        filedata= file.readlines()
        if not filedata:  # Check if the list is empty
            print("File is empty or does not contain any data.")
            return []
        article = filedata[0].split(". ")
        sentences = []
    #  removing special characters and extra witespaces
        for sentence in article:
            sentence = re.sub('[^a-zA-Z]', ' ',str(sentence))
            sentence = re.sub('[\s+]', ' ',sentence)
            sentences.append(sentence)
        sentences.pop()
        display = " ".join(sentences)
        print('Initial Text: ')
        print(display)
        print('\n')
        return sentences


# Number of Words in Each Sentence
def cnt_words(sent):
    cnt=0
    words= word_tokenize(sent)
    for word in words:
        cnt = cnt +1
    return cnt
# getting data about each sentence(frequency of words)
def cnt_in_sent(sentences):
    txt_data =[]
    i =0
    for sent in sentences:
        i = i+1
        cnt= cnt_words(sent)
        temp = {'id': i, 'word_cnt':cnt}
        txt_data.append(temp)
    return txt_data

# Creating List of Frequencies for each Word in all Documents
# Here, we create a list which stores the frequency of each word of the document
def freq_dict(sentences):
    i=0
    freq_list= []
    for sent in sentences:
        i =i +1
        freq_dict = {}
        words = word_tokenize(sent)
        for word in words:
            word= word.lower()
            if word in freq_dict:
                freq_dict[word] = freq_dict[word]+1
            else:
                freq_dict[word]= 1
            temp={ 'id':i, 'freq_dict' : freq_dict}
        freq_list.append(temp)
    return freq_list


# calculating TF and IDF Values
# The first function calculates the term frequency of words in each document (here, sentences). The second function calculates the inverse document frequency for each word in the sentences.
def calc_TF(text_data, freq_list):
    tf_score=[]
    for item in freq_list:
        ID= item['id']
        for k in item['freq_dict']:
            temp={
                'id': item['id'],
                'tf_score': item['freq_dict'][k]/text_data[ID-1]['word_cnt'],
                'key':k
            }
            tf_score.append(temp)
    return (tf_score)
# calculating inverse document frequency
def calc_IDF(text_data, freq_list):
    idf_scores=[]
    cnt=0
    for item in freq_list:
        cnt= cnt +1
        for k in item['freq_dict']:
            val=sum([k in it['freq_dict'] for it in freq_list])
            temp={
                'id':cnt,
                'idf_score': math.log(len(text_data)/(val+1)),
                'key':k
            }
            idf_scores.append(temp)
    return idf_scores

# calculating TF-IDF Values
# Computing the TF-IDF scores for each term
def calc_TFIDF(tf_scores, idf_scores):
    tfidf_scores=[]
    for j in idf_scores:
        for i in tf_scores:
            if j['key']==i['key'] and j['id']== i['id']:
                temp={
                    'id':j['id'],
                    'tfidf_score':j['idf_score']*i['tf_score'],
                    'key':j['key']
                    }
                tfidf_scores.append(temp)
    return tfidf_scores

# ranking all the documents
# We calculate the score for each sentence based on the TF-IDF value for each word in the sentence
def sent_scores(tfidf_scores, sentences, text_data):
    sent_data=[]
    for txt in text_data:
        score =0
        for i in range(0, len(tfidf_scores)):
            t_dict = tfidf_scores[i]
            if txt['id']==t_dict['id']:
                score=score+t_dict['tfidf_score']
        temp={
            'id':txt['id'],
            'score': score,
            'sentence': sentences[txt['id']-1]}
        sent_data.append(temp)
    return sent_data

# GENERATE SUMMARY
# The threshold is calculated as a linear function of the average of the TF-IDF scores
# @app.route('/summarize', methods=['POST'])
def summary(sent_data):
    if not sent_data:
        print("No data to summarize.")
        return ""
    cnt=0
    summary=[]
    for t_dict in sent_data:
        cnt=cnt + t_dict['score']
    avg=cnt/len(sent_data)
    for sent in sent_data:
        if sent['score'] >=(avg * 0.9):
            summary.append(sent['sentence'])
    summary =". ".join(summary)
    return summary

# CALLING ALL THE FUNCTIONS
sentences= clean_text('test.txt')
text_data= cnt_in_sent(sentences)

freq_list= freq_dict(sentences)
tf_scores= calc_TF(text_data, freq_list)
idf_scores=calc_IDF(text_data, freq_list)

tfidf_scores=calc_TFIDF(tf_scores, idf_scores)
sent_data= sent_scores(tfidf_scores, sentences, text_data)
result = summary(sent_data)

# print('Final Summary: ')
# print(result)


# /////////////////////////////////////
# Importing Libraries
# import re
# import nltk
# import math
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize, sent_tokenize
# import os

# # CLEANING TEXT FUNCTION
# def clean_text(file_name):
#     # Ensure the file exists, or create it if not
#     if not os.path.exists(file_name):
#         print("File '{}' not found. Creating an empty file.".format(file_name))
#         with open(file_name, 'w') as f:
#             f.write('')

#     # Read the file content
#     with open(file_name, 'r') as file:
#         filedata = file.read()  # Read the whole content as a single string
#         if not filedata:  # If the file is empty
#             print("File is empty or does not contain any data.")
#             return []

#         # Remove special characters and allow only a-z, A-Z, 0-9, '.', ','
#         cleaned_text = re.sub(r'[^a-zA-Z., ]', '', filedata)

#         # Remove paragraph spacing by replacing newline characters with spaces
#         cleaned_text = cleaned_text.replace('\n', ' ')
#         cleaned_text = cleaned_text.replace('\r', ' ')  # In case of carriage returns

#         # Optionally, reduce multiple spaces to a single space
#         cleaned_text = re.sub(r'\s+', ' ', cleaned_text)

#         # Tokenize the cleaned text into sentences
#         sentences = cleaned_text.split(". ")
        
#         # Remove any trailing/empty sentences if needed
#         sentences = [s.strip() for s in sentences if s.strip()]

#         # Display cleaned text
#         display = " ".join(sentences)
#         print('Initial Cleaned Text:')
#         print(display)
#         print('\n')

#         return sentences


# # Number of Words in Each Sentence
# def cnt_words(sent):
#     cnt = 0
#     words = word_tokenize(sent)
#     for word in words:
#         cnt += 1
#     return cnt


# # Getting data about each sentence (frequency of words)
# def cnt_in_sent(sentences):
#     txt_data = []
#     i = 0
#     for sent in sentences:
#         i += 1
#         cnt = cnt_words(sent)
#         temp = {'id': i, 'word_cnt': cnt}
#         txt_data.append(temp)
#     return txt_data


# # Creating a list of frequencies for each word in all documents
# def freq_dict(sentences):
#     i = 0
#     freq_list = []
#     for sent in sentences:
#         i += 1
#         freq_dict = {}
#         words = word_tokenize(sent)
#         for word in words:
#             word = word.lower()
#             if word in freq_dict:
#                 freq_dict[word] += 1
#             else:
#                 freq_dict[word] = 1
#         temp = {'id': i, 'freq_dict': freq_dict}
#         freq_list.append(temp)
#     return freq_list


# # Calculating TF and IDF values
# def calc_TF(text_data, freq_list):
#     tf_score = []
#     for item in freq_list:
#         ID = item['id']
#         for k in item['freq_dict']:
#             temp = {
#                 'id': ID,
#                 'tf_score': item['freq_dict'][k] / text_data[ID - 1]['word_cnt'],
#                 'key': k
#             }
#             tf_score.append(temp)
#     return tf_score


# # Calculating inverse document frequency
# def calc_IDF(text_data, freq_list):
#     idf_scores = []
#     cnt = 0
#     for item in freq_list:
#         cnt += 1
#         for k in item['freq_dict']:
#             val = sum([k in it['freq_dict'] for it in freq_list])
#             temp = {
#                 'id': cnt,
#                 'idf_score': math.log(len(text_data) / (val + 1)),
#                 'key': k
#             }
#             idf_scores.append(temp)
#     return idf_scores


# # Calculating TF-IDF values
# def calc_TFIDF(tf_scores, idf_scores):
#     tfidf_scores = []
#     for j in idf_scores:
#         for i in tf_scores:
#             if j['key'] == i['key'] and j['id'] == i['id']:
#                 temp = {
#                     'id': j['id'],
#                     'tfidf_score': j['idf_score'] * i['tf_score'],
#                     'key': j['key']
#                 }
#                 tfidf_scores.append(temp)
#     return tfidf_scores


# # Ranking all the documents
# def sent_scores(tfidf_scores, sentences, text_data):
#     sent_data = []
#     for txt in text_data:
#         score = 0
#         for i in range(0, len(tfidf_scores)):
#             t_dict = tfidf_scores[i]
#             if txt['id'] == t_dict['id']:
#                 score += t_dict['tfidf_score']
#         temp = {
#             'id': txt['id'],
#             'score': score,
#             'sentence': sentences[txt['id'] - 1]
#         }
#         sent_data.append(temp)
#     return sent_data


# # Generate summary based on a linear threshold
# def summary(sent_data):
#     if not sent_data:
#         print("No data to summarize.")
#         return ""
#     cnt = 0
#     summary = []
#     for t_dict in sent_data:
#         cnt += t_dict['score']
#     avg = cnt / len(sent_data)
#     for sent in sent_data:
#         if sent['score'] >= avg * 0.9:
#             summary.append(sent['sentence'])
#     summary = ". ".join(summary)
#     return summary


# # Calling all the functions with the cleaned text
# file_name = 'test.txt'
# sentences = clean_text(file_name)
# text_data = cnt_in_sent(sentences)

# freq_list = freq_dict(sentences)
# tf_scores = calc_TF(text_data, freq_list)
# idf_scores = calc_IDF(text_data, freq_list)

# tfidf_scores = calc_TFIDF(tf_scores, idf_scores)
# sent_data = sent_scores(tfidf_scores, sentences, text_data)
# result = summary(sent_data)

# # Print the final summary
# print('Final Summary:')
# print(result)
