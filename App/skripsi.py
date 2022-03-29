import streamlit as st
import streamlit_authenticator as stauth
import extra_streamlit_components as stx
import input, report, dataset, db_management

# Initialization session state
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = False

#Page Config
st.set_page_config(
    page_title="Sentiment App",
    layout="wide",
    initial_sidebar_state="expanded",
)
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

#Get all users for authentication
all_user_rows = db_management.view_all_users()
usernames = []
passwords = []

for row in all_user_rows:
    usernames.append(row[1])
    passwords.append(row[2])

hashed_passwords = stauth.hasher(passwords).generate()
authenticator = stauth.authenticate(usernames,usernames,hashed_passwords,
    'some_cookie_name','some_signature_key',cookie_expiry_days=1)
name, authentication_status = authenticator.login('Login','main')


#Page After Login
if authentication_status:
    # st.success('Logged in as *%s*' % (name))

    #State session Login true
    st.session_state['authentication_status'] = True 

    #session username
    if 'session_user' not in st.session_state:
      st.session_state['session_user'] = name

    chosen_id = stx.tab_bar(data=[
        stx.TabBarItemData(id=1, title="Input Data", description="Input dan klasifikasi data baru"),
        stx.TabBarItemData(id=2, title="Report", description="Visualisasi Data"),
        stx.TabBarItemData(id=3, title="Data", description="Setiap data yang telah tersimpan"),
    ], default=1)
     
    if chosen_id == '1':
        input.app()
    elif chosen_id == '2':
        report.app()
    else:
        dataset.app()

elif authentication_status == False:
    st.error('Username/password is incorrect')

# elif authentication_status == None:
#     st.warning('Please enter your username and password')