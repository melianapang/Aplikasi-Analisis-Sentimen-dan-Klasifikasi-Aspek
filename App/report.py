import streamlit as st
import pandas as pd
import numpy as np
import math
import db_management
import matplotlib.pyplot as plt

def app():
    st.title('Report')

    # Get all file's name from database
    all_metadata = db_management.get_all_file_properties()
    # st.write(all_metadata[0][1])
    data_names=[row[1] for row in all_metadata]
    file_choice = st.selectbox("Pilih file yang ingin ditampilkan", data_names)
    sort_by = st.radio(
        "Sort By",
        ('Negatif Data', 'Positif Data'))

    global data_path, df, sort
    
    sort = 'Negatif' if sort_by == 'Negatif Data' else 'Positif'
    if file_choice == 'Individu':
            try:
                # Get individu opinion from database
                individu_data = db_management.get_all_individu_data()

                # Convert to dataframe
                opinion = []; aspect = [];sentiment = []
                for row in individu_data:
                    opinion.append(row[1])
                    aspect.append(row[2])
                    sentiment.append(row[3])

                df_temp = pd.DataFrame({'Opinion': opinion,
                                    'Aspect': aspect,
                                    'Sentiment': sentiment
                                    })

                df = df_temp
            except Exception as e:
                st.write(e)

    else:
        # Get chosen file's path
        for i in range(len(all_metadata)):
            if file_choice in all_metadata[i][1]:
                # data_path = all_metadata[i][2]
                id_file = all_metadata[i][0]

        # df = pd.read_excel(data_path)
        file_data = db_management.get_file_data(id_file)

        # Convert to dataframe
        opinion = []; aspect = [];sentiment = []
        for row in file_data:
            opinion.append(row[1])
            aspect.append(row[2])
            sentiment.append(row[3])

        df_temp = pd.DataFrame({'Opinion': opinion,
                                'Aspect': aspect,
                                'Sentiment': sentiment
                                })

        df = df_temp



    # CHARTS
    aspects=df['Aspect'].unique()
    jumlah = []
    jumlah_ticks = []
    for r in aspects:
        data = df[(df['Sentiment'] == sort) & (df['Aspect'] == r)]
        jumlah.append(len(data))
        data_ticks = df[(df['Sentiment'] == 'Positif') & (df['Aspect'] == r)]
        jumlah_ticks.append(len(data_ticks))
        

    df_temp = pd.DataFrame({'Aspect': aspects,'Jumlah': jumlah})
    df_temp = pd.DataFrame(df_temp)
    final_sort=df_temp.sort_values(['Jumlah'], ascending=False)
    final_sort=final_sort.reset_index(drop=True)

    max_value_ytick = max(jumlah_ticks)
    print(max_value_ytick)

    col1, col2 = st.columns(2)
    for i in range(len(final_sort)):
        if i % 2 == 0:
            col1.write(plot_bar(df,"Sentiment",final_sort["Aspect"][i],max_value_ytick))
        else:
            col2.write(plot_bar(df,"Sentiment",final_sort["Aspect"][i],max_value_ytick))

    # col1.write(plot_bar(df,"Sentiment","Informasi"))
    # col2.write(plot_bar(df,"Sentiment","Waktu"))
    # col1.write(plot_bar(df,"Sentiment","Tempat"))
    # col2.write(plot_bar(df,"Sentiment","Protokol"))
    # col1.write(plot_bar(df,"Sentiment","Sertifikat"))

    # col1.write(plot_pie(df,"Sentiment","Informasi"))
    # col2.write(plot_pie(df,"Sentiment","Waktu"))
    # col1.write(plot_pie(df,"Sentiment","Tempat"))
    # col2.write(plot_pie(df,"Sentiment","Protokol"))
    # col1.write(plot_pie(df,"Sentiment","Sertifikat"))


def plot_bar(df,col,aspect,max_value_ytick):
    df = df.loc[df["Aspect"] == aspect]
    data = df[col].value_counts() 
    data = pd.DataFrame(data)
    
    sentiments = df["Sentiment"].unique()
    if len(sentiments) == 2:
        colors = ["green", "red"]
    else:
        colors = ["green" if i == "Positif" else "red" for i in sentiments]

    fig, ax = plt.subplots(figsize=(15, 8))
    ax.bar(data.index.values,
           data[col], color=colors)

    if max_value_ytick < 50:
        ax.set_yticks(range(0, math.ceil(max_value_ytick)+5, 5))
    elif max_value_ytick > 50 and max_value_ytick < 250:
        ax.set_yticks(range(0, math.ceil(max_value_ytick)+5, 20))
    elif max_value_ytick > 250 and max_value_ytick < 1000:
        ax.set_yticks(range(0, math.ceil(max_value_ytick)+5, 50))
    else:
        ax.set_yticks(range(0, math.ceil(max_value_ytick)+5, 100))
        

    fsize = 32
    plt.rc('xtick', labelsize=24)
    plt.rc('ytick', labelsize=24)
    
    plt.xlabel("{}".format(col),fontsize = fsize)
    plt.ylabel("Jumlah Aspek {}".format(aspect),fontsize = fsize)
    plt.title("{} dari Aspek {}".format(col,aspect),fontsize = fsize)

    return fig


def plot_pie(df,col,aspect):
    df = df.loc[df["Aspect"] == aspect]
    data = df[col].value_counts()
    data = pd.DataFrame(data)

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(data[col],labels=data.index.values, autopct='%1.1f%%',
        shadow=True, startangle=90)

    fsize = 16
    plt.xlabel("{}".format(col),fontsize = fsize)
    plt.title("{} dari Aspek {}".format(col,aspect),fontsize = fsize)

    return fig
        

# https://towardsdatascience.com/dashboard-using-streamlit-with-data-from-sql-database-f5c1ee36b51