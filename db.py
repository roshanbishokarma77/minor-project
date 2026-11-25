import sqlite3
import streamlit as st

#@st.cache_resource
def get_connection():
    conn = sqlite3.connect(
        "project.db",
        check_same_thread=False
    )
    return conn