import streamlit as st
import numpy as np
import pandas as pd
import os
import db_management
from preprocessing import preprocessing_data
import pickle
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import metrics

def app():
    st.title('Input Data')

    #Opinions in a file
    file_name = st.text_input("Nama File")
    uploaded_file = st.file_uploader("Pilih file", type = ['xlsx'])
    file_ml_choice = st.selectbox("Machine Learning Method", ["Naive Bayes (Kuesioner)","SVM (Kuesioner)", "LGBM (Kuesioner)","Random Forest (Kuesioner)", "Naive Bayes (Medsos)","SVM (Medsos)", "LGBM (Medsos)","Random Forest (Medsos)"])
    submit_file = st.button("Submit")

    #check the file
    global data
    global opinion, aspect, sentiment
    global accuracy_sentiment, precision_sentiment, recall_sentiment, fscore_sentiment
    global accuracy_aspect, precision_aspect, recall_aspect, fscore_aspect

    if submit_file:

        col1, col2, col3, col4, col5 = st.columns(5)

        # Reading file, Validating file (unclassified or classified)
        if uploaded_file is not None and file_name != "":
            try:
                data = pd.read_excel(uploaded_file)
                columns_name = data.columns

                # Classified File
                if (len(columns_name) > 1 and columns_name[0] == 'Opinion' and columns_name[1] == 'Aspect' and columns_name[2] == "Sentiment" and data[columns_name[0]].isnull().values.any() == False and data[columns_name[1]].isnull().values.any() == False and data[columns_name[2]].isnull().values.any() == False):
                    # Save to folder first, then classify to test the model
                    save_uploaded_data(uploaded_file)

                    # Get, prepare, and predict data
                    opinion = data.iloc[:, 0]
                    aspect = data.iloc[:, 1]
                    sentiment = data.iloc[:, 2]
                    aspect_pred, sentiment_pred = predict_data(opinion,file_ml_choice,"Classified")

                    # Convert to dataframe
                    df_temp = pd.DataFrame({'Opinion': opinion,
                                'Aspect': aspect_pred,
                                'Sentiment': sentiment_pred
                                })

                    #Save prediction result to database
                    db_management.add_classified_result_file_opinion(df_temp, file_name,uploaded_file.name)

                    # Model Evaluation 
                    try:
                        accuracy_sentiment = metrics.accuracy_score(sentiment, sentiment_pred)
                        precision_sentiment = metrics.precision_score(sentiment, sentiment_pred,average='macro')
                        recall_sentiment = metrics.recall_score(sentiment, sentiment_pred, average='macro')
                        fscore_sentiment = metrics.f1_score(sentiment, sentiment_pred, average='macro')

                        col1.metric("File Type", "Classified")
                        col2.metric("Accuracy", str(round(accuracy_sentiment*100,3))+"%")
                        col3.metric("Precision", str(round(precision_sentiment*100,3))+"%")
                        col4.metric("Recall", str(round(recall_sentiment*100,3))+"%")
                        col5.metric("F-1 Score", str(round(fscore_sentiment*100,3))+"%")

                        accuracy_aspect = metrics.accuracy_score(aspect, aspect_pred)
                        precision_aspect = metrics.precision_score(aspect, aspect_pred, average='macro')
                        recall_aspect = metrics.recall_score(aspect, aspect_pred, average='macro')
                        fscore_aspect = metrics.f1_score(aspect, aspect_pred, average='macro')

                        col2.metric("Accuracy Aspect", str(round(accuracy_aspect*100,3))+"%")
                        col3.metric("Precision Aspect", str(round(precision_aspect*100,3))+"%")
                        col4.metric("Recall Aspect", str(round(recall_aspect*100,3))+"%")
                        col5.metric("F-1 Score Aspect", str(round(fscore_aspect*100,3))+"%")
                    except Exception as e:
                        st.write(e)
                    
                # Unclassified file
                elif ((len(columns_name) == 1 and columns_name[0] == 'Opinion' and len(data[columns_name[0]]) >= 1 and data[columns_name[0]].isnull().values.all() == False) or (len(columns_name) > 1 and columns_name[0] == 'Opinion' and columns_name[1] == 'Aspect' and columns_name[2] == "Sentiment" and len(data[columns_name[0]]) >= 1 and data[columns_name[0]].isnull().values.any() == False and data[columns_name[1]].isnull().values.all() == True and data[columns_name[1]].isnull().values.all() == True)):
                    col1.metric("File Type", "Unclassified")
                    opinion = data.iloc[:, 0]

                    # Classify first, then save
                    aspect_pred, sentiment_pred = predict_data(opinion,file_ml_choice,"Unclassified")

                    # Convert to dataframe
                    df_temp = pd.DataFrame({'Opinion': opinion,
                                'Aspect': aspect_pred,
                                'Sentiment': sentiment_pred
                                })

                    # Save to Database
                    db_management.add_classified_result_file_opinion(df_temp, file_name,uploaded_file.name)
                    save_uploaded_data(uploaded_file)

                else:
                    st.write("Mohon unggah file dengan format dengan header Opinion atau Opinion, Aspect, dan Sentiment.")

            except Exception as e:
                st.write(e)

        else:
            st.write("Mohon isi semua informasi yang ada.")

    # Line
    st.markdown("""<hr style="height:10px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)
    
    #Individu opinion
    st.subheader("Tuliskan pendapat Anda dibawah ini")
    sentence_op = st.text_input("Pendapat anda")
    ml_choice = st.selectbox("Machine Learning", ["Naive Bayes (Kuesioner)","SVM (Kuesioner)", "LGBM (Kuesioner)","Random Forest (Kuesioner)", "Naive Bayes (Medsos)","SVM (Medsos)", "LGBM (Medsos)","Random Forest (Medsos)"])
    submit_opinion = st.button("Submit untuk Klasifikasi")

    if submit_opinion:
        # Save and Classify the opinion to Database
        aspect_pred, sentiment_pred = predict_data(sentence_op,ml_choice,"Sentence")

        col1, col2, col3, col4 = st.columns(4)
        col1.write("Aspect")
        col2.write("Sentiment")
        for i in aspect_pred:
            col1.header(i)
        for i in sentiment_pred:
            col2.header(i)

        try:
            op_tokenized = sent_tokenize(sentence_op)   
            for i in range(len(op_tokenized)):
                opinion_p = str(op_tokenized[i])
                aspect_p = str(aspect_pred[i])
                sentiment_p = str(sentiment_pred[i])
                db_management.add_classified_result_individu_opinion(opinion_p,aspect_p,sentiment_p)
                st.success("Kalimat pendapat dan hasil prediksi berhasil disimpan pada database.")
        except Exception as e:
            st.write(e) 



def save_uploaded_data(uploadedFile):
    with open(os.path.join("data_pendapat", uploadedFile.name), "wb") as f:
        f.write(uploadedFile.getbuffer())
    return st.success("Berhasil menyimpan file dengan nama {} di folder".format(uploadedFile.name))



def predict_data(opinion,method,file_type):
    #Prepare data and Loading our ML & CountVect model
    global aspect_model, sentiment_model
    isKuesionerModel = False

    if method == "Naive Bayes (Kuesioner)":
        aspect_model = pickle.load(open('model/model_baru/nb_aspect_K.sav','rb'))
        sentiment_model = pickle.load(open('model/model_baru/nb_sentiment_K.sav','rb'))
        isKuesionerModel = True
                
    elif method == "SVM (Kuesioner)":
        aspect_model = pickle.load(open('model/model_gridsearch_2/svm_aspect_K.sav','rb'))
        sentiment_model = pickle.load(open('model/svm_sentiment_RUS_K.sav','rb'))
        isKuesionerModel = True

    elif method == "LGBM (Kuesioner)":
        aspect_model = pickle.load(open('model/model_gridsearch_2/lgbm_aspect_K_2.sav','rb'))
        sentiment_model = pickle.load(open('model/lgbm_sentiment_RUS_K.sav','rb'))
        isKuesionerModel = True

    elif method == "Random Forest (Kuesioner)":
        aspect_model = pickle.load(open('model/model_gridsearch_2/rf_aspect_K.sav','rb'))
        sentiment_model = pickle.load(open('model/rf_sentiment_RUS_K.sav','rb'))
        isKuesionerModel = True

    elif method == "Naive Bayes (Medsos)":
        aspect_model = pickle.load(open('model/model_baru_82/nb_aspect_M.sav','rb'))
        sentiment_model = pickle.load(open('model/model_baru_82/nb_sentiment_M.sav','rb'))

    elif method == "SVM (Medsos)":
        aspect_model = pickle.load(open('model/model_gridsearch/svm_aspect_M.sav','rb'))
        sentiment_model = pickle.load(open('model/model_gridsearch/svm_sentiment_M.sav','rb'))

    elif method == "LGBM (Medsos)":
        aspect_model = pickle.load(open('model/model_gridsearch/lgbm_aspect_M_2.sav','rb'))
        sentiment_model = pickle.load(open('model/model_gridsearch/lgbm_sentiment_M_2.sav','rb'))

    elif method == "Random Forest (Medsos)":
        aspect_model = pickle.load(open('model/model_gridsearch/rf_aspect_M_2.sav','rb'))
        sentiment_model = pickle.load(open('model/model_gridsearch/rf_sentiment_M_2.sav','rb'))

    count_vect = CountVectorizer(lowercase='false')
    FILE_VOCAB_PATH = 'dataset/vocabulary_ya3.txt' if isKuesionerModel else 'dataset/vocab_ya1.txt'
    with open(FILE_VOCAB_PATH) as f:
        vocabulary = f.read()
    vocabulary = [vocabulary]
    count_vect.fit(vocabulary)

    # Checking whether the opinion is individu or not
    result_aspect = []
    result_sentiment = []
    global X_processed_text
    if file_type == "Unclassified" or file_type == "Classified":
        X_processed_text = [preprocessing_data(row) for row in opinion]    

    else:
        opinion_tokenized = sent_tokenize(opinion)
        X_processed_text = [preprocessing_data(opinion) for opinion in opinion_tokenized]


    for row in X_processed_text:
        row = [row]
        new_vect = count_vect.transform(row)
        new_vect = new_vect.toarray().astype(float)
        new_vect = np.array(new_vect, dtype='float64')
            
        try:
            aspect_pred = aspect_model.predict(new_vect)
            sentiment_pred = sentiment_model.predict(new_vect)
            result_aspect.extend(aspect_pred)
            result_sentiment.extend(sentiment_pred)
        except Exception as e:
            st.write(e)  
        
    return result_aspect, result_sentiment
    