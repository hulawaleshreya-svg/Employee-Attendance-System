
import streamlit as st

def style_background_home():
    st.markdown("""
        <style>
        .stApp {
            background: #713F4A !important;
        }
        </style>
    """, unsafe_allow_html=True)


def style_background_dashboard():
    st.markdown("""
        <style>
        .stApp {
            background: #C9828C !important;
        }
        </style>
    """, unsafe_allow_html=True)


def style_base_layout():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&display=swap');

        #MainMenu, footer, header {
            visibility: hidden;
        }

        .block-container {
            padding-top: 1.5rem !important;
            max-width: 1000px;
        }

        h1, h2, h3 {
            font-family: 'DM Serif Display', serif !important;
        }

        body, p, label, button, input {
            font-family: 'Manrope', sans-serif !important;
        }
        </style>
    """, unsafe_allow_html=True)
