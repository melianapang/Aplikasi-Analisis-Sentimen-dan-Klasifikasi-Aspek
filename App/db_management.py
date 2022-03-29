import streamlit as st
import pandas as pd
import mysql.connector

# DB Management
config = {
	'user': 'root',
	'password':'',
	'host': 'localhost',
	'database':'sentiment_sql',
	'raise_on_warnings': True
}

# Uses st.cache to only run once.
# @st.cache(allow_output_mutation=True)
conn = mysql.connector.connect(**config)
c = conn.cursor()


# DB  Functions
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS user(username TEXT,password TEXT)')


# def add_userdata(username,password):
# 	sql = 'INSERT INTO user (username,password) VALUES (%s, %s)'
# 	data = (username,password)
# 	c.execute(sql,data)
# 	conn.commit()


# Uses st.cache to only rerun when the query changes or after 10 min.
@st.cache(ttl=600)
def view_all_users():
	c.execute('SELECT * FROM users')
	data = c.fetchall()
	return data
	

def add_classified_result_individu_opinion(opinion, aspect_pred, sentiment_pred):
	# Get idFile for individu opinion
	cursor= conn.cursor(buffered=True)
	cursor.execute("SELECT idFile FROM files WHERE namaFile = 'Individu'")
	idFile= cursor.fetchone()
	conn.commit()

	# Insert opinion
	sql = "INSERT INTO opinion (sentence, aspek, sentiment, idFile_fk) VALUES (%s, %s, %s, %s)"
	data = (opinion, aspect_pred,sentiment_pred, idFile[0])
	c.execute(sql,data)
	conn.commit()


def add_classified_result_file_opinion(df, nama_file,file_path):
	PATH = 'data_pendapat/'

	# Save path file
	sql = "INSERT INTO files (namaFile, filePath) VALUES (%s, %s)"
	data = (nama_file, PATH+file_path)
	c.execute(sql,data)
	conn.commit()

	# Get idFile for file opinion
	sql = "SELECT idFile FROM files WHERE namaFile = %s AND filePath = %s"
	data = (nama_file, PATH+file_path)
	cursor= conn.cursor(buffered=True)
	cursor.execute(sql,data)
	idFile= cursor.fetchone()
	conn.commit()

	# Insert to database
	for index, row in df.iterrows():
		opinion = str(row["Opinion"])
		aspect = str(row["Aspect"])
		sentiment = str(row["Sentiment"])

		sql = "INSERT INTO opinion (sentence, aspek, sentiment, idFile_fk) VALUES (%s, %s, %s, %s)"
		data = (opinion, aspect,sentiment, idFile[0])
		c.execute(sql,data)
		conn.commit()

	return st.success("File opinion dan hasil prediksi berhasil disimpan pada database.")

def get_all_file_properties():
	c.execute('SELECT * FROM files')
	data = c.fetchall()
	return data

def get_all_individu_data():
	c.execute("SELECT * FROM opinion WHERE idFile_fk = (SELECT idFile FROM files WHERE namaFile = 'Individu')")
	data = c.fetchall()
	return data

def get_file_data(id_file):
	sql = "SELECT * FROM opinion WHERE idFile_fk = " + str(id_file)
	c.execute(sql)
	file_data = c.fetchall()
	
	return file_data