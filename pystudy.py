import streamlit as st
import google.generativeai as genai
import os

# 이 부분은 주석 처리하거나, st.secrets로 키 설정하세요.
# genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
genai.configure(api_key=st.secrets["AIzaSyCaSoDBTZzWkSQOszY-g7Iked8_OaQr944"])

st.title("Gemini API Test")
st.write("If you see this, google-generativeai was imported successfully.")

try:
    model = genai.GenerativeModel('gemini-pro')
    st.success("Gemini model loaded successfully!")
except Exception as e:
    st.error(f"Failed to load Gemini model: {e}")

user_input = st.text_input("Ask Gemini:")
if user_input:
    with st.spinner("Generating response..."):
        try:
            response = model.generate_content(user_input)
            st.write(response.text)
        except Exception as e:
            st.error(f"Error generating content: {e}")
