import streamlit as st
import db_management
import pandas as pd

def app():
    st.title('Data')

    # Initialization session state
    if 'pagination' not in st.session_state:
        st.session_state['pagination'] = False
    if 'page_number' not in st.session_state:
        st.session_state['page_number'] = 0
    
    # Get all file's name from database
    all_metadata = db_management.get_all_file_properties()
    data_names=[row[1] for row in all_metadata]
    file_choice = st.selectbox("Pilih file yang ingin ditampilkan", data_names)


    global data, data_path

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

            data = df_temp
        except Exception as e:
            st.write(e)

    else:
        # Get chosen file's path
        for i in range(len(all_metadata)):
            if file_choice in all_metadata[i][1]:
                # data_path = all_metadata[i][2]
                id_file = all_metadata[i][0]

        # data = pd.read_excel(data_path)
        df = db_management.get_file_data(id_file)

        # Convert to dataframe
        opinion = []; aspect = [];sentiment = []
        for row in df:
            opinion.append(row[1])
            aspect.append(row[2])
            sentiment.append(row[3])

        df_temp = pd.DataFrame({'Opinion': opinion,
                                'Aspect': aspect,
                                'Sentiment': sentiment
                                })
        data = df_temp

        

    # PAGINATION
    # Number of entries per screen
    N = 15
    last_page = len(data) // N

    # Add a next button and a previous button
    prev, _ ,next = st.columns([1, 10, 1])

    if next.button("Next"):
        if st.session_state['page_number'] + 1 > last_page:
            st.session_state['page_number'] = 0
        else:
            st.session_state['page_number'] += 1

    if prev.button("Previous"):
        if st.session_state['page_number'] - 1 < 0:
            st.session_state['page_number'] = last_page
        else:
            st.session_state['page_number'] -= 1

    # Get start and end indices of the next page of the dataframe
    start = st.session_state['page_number'] * N 
    end = (1 + st.session_state['page_number']) * N

    # Index into the sub dataframe
    sub_df = data.iloc[start:end]
    st.table(sub_df)