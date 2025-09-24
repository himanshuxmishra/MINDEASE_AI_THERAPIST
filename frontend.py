
import streamlit as st
import requests


BACKEND_URL = "http://localhost:8000/ask"



st.set_page_config(page_title="AI Mental Health Therapist", layout="wide")
st.title("🧠 MindEase")



if "chat_history" not in st.session_state:
    st.session_state.chat_history = []



user_input = st.chat_input("What's on your mind today?")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    try:
        response = requests.post(BACKEND_URL, json={"message": user_input})
        response.raise_for_status()
        data = response.json()

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": f'{data["response"]} WITH TOOL: [{data["tool_called"]}]',
            }
        )

    except Exception as e:
        st.session_state.chat_history.append(
            {"role": "assistant", "content": f"⚠️ Error connecting to backend: {e}"}
        )


# ------------------ DISPLAY CHAT ------------------
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
