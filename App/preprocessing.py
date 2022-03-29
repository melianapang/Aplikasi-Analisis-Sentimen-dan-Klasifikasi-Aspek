import numpy as np
import pandas as pd
import io
import nltk, re, string, ast
from nltk.tokenize import word_tokenize
from string import punctuation
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory, StopWordRemover, ArrayDictionary
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory


def normalisasi(texts):
    FILE_NORMALISASI_PATH = 'dataset/normalisasi.txt'

    with open(FILE_NORMALISASI_PATH) as f:
        data_normalisai = f.read()
    normalization_words = ast.literal_eval(data_normalisai)

    finalText = []
    splitted_text = texts.split()
    for text in splitted_text:
        if text in normalization_words:
            finalText.append(normalization_words[text])
        else:
            finalText.append(text)
      
    return " ".join(finalText)

def case_folding(text):
    text = text.lower()
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r"\d+", " ", text)
    for i in text:
        if i in list(string.punctuation):
            text = text.replace(i, " ")

    return text

def hapus_stopword(text):
    FILE_STOPWORDS_PATH = 'dataset/stopwords.txt'
    
    with open(FILE_STOPWORDS_PATH) as f:
        data_stopwords = f.read()
    stopwords = ast.literal_eval(data_stopwords)

    stopword_factory = stopwords

    sw_dict = ArrayDictionary(stopword_factory)
    temp = StopWordRemover(sw_dict)

    text = temp.remove(text)
    return text

def hapus_duplikasi_kata(text):
    res = []
    text = text.split()
    for i in text:
        if i in res:
            text.remove(i)
        else:
            res.append(i)
    return " ".join(text)

def stemming(text):
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    text = stemmer.stem(text)
    return text

def preprocessing_data(opinion):
    opinion = case_folding(opinion)
    opinion = normalisasi(opinion)
    opinion = hapus_stopword(opinion)
    opinion = hapus_duplikasi_kata(opinion)
    opinion = stemming(opinion)
    return opinion
