import streamlit as st
import asyncio

from kai_sdk_python.index import KaiStudioInstance, KaiStudioCredentials

import os

credentials = KaiStudioCredentials(instance_id=os.environ.get("INSTANCE_ID"),
                                   api_key=os.environ.get("API_KEY"))

need_multi_documents = os.environ.get("NEED_MULTI_DOCUMENTS") == "True"
need_following_questions = os.environ.get("NEED_FOLLOWING_QUESTIONS") == "True"

search = KaiStudioInstance(credentials).search()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

st.title("KAI Chatbot")

messages = st.session_state.chat_history
for message in messages:
    st.chat_message(message['from']).write(message['message'])

if question := st.chat_input(placeholder="Ask me anything..."):
    messages.append({"from": "user", "message": question})
    st.chat_message("user").write(question)

    async def send_final_query():
        final_response = await search.query(
            st.session_state.chat_history[-1]['message'], 
            "userid",
        )
        if final_response:
            if final_response.answer == '':
                messages.append({"from": "assistant", "message": "I don't know the answer to that question."})
                st.chat_message("assistant").write("I don't know the answer to that question.")
            else:
                answer_content = 'Answer:\n\n"' + final_response.answer
                messages.append({"from": "assistant", "message": answer_content})
                st.chat_message("assistant").write(answer_content)
        else:
            st.info("Please add your correct key to initialize the chatbot")
            st.stop()

    asyncio.run(send_final_query())
