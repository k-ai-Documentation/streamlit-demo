import streamlit as st
import asyncio

from kai_sdk_python.index import KaiStudio
from kai_sdk_python.index import KaiStudioCredentials

import json
import os

credentials = KaiStudioCredentials(organizationId=os.environ.get("ORGANIZATION_ID"),
                                   instanceId=os.environ.get("INSTANCE_ID"),
                                   apiKey=os.environ.get("API_KEY"))

need_multi_documents = os.environ.get("NEED_MULTI_DOCUMENTS") == "True"
need_following_questions = os.environ.get("NEED_FOLLOWING_QUESTIONS") == "True"

search = KaiStudio(credentials).search()

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
            '',  
            need_multi_documents,
            need_following_questions
        )
        messages.append({"from": "assistant", "message": final_response.answer})

        if need_multi_documents and need_following_questions:
            st.chat_message("assistant").write("Answer:\n\n" + final_response.answer + "\n\n" + "Follow up questions:\n\n" + '\n\n'.join(final_response.followingQuestions) + "\n\n" + "Documents: \n\n" + json.dumps(final_response.documents))
        elif need_multi_documents and not need_following_questions:
            st.chat_message("assistant").write("Answer:\n\n" + final_response.answer + "\n\n" + "Documents: \n\n" + json.dumps(final_response.documents))
        elif not need_multi_documents and need_following_questions:
            st.chat_message("assistant").write("Answer:\n\n" + final_response.answer + "\n\n" + "Follow up questions:\n\n" + '\n\n'.join(final_response.followingQuestions))
        else:
            st.chat_message("assistant").write("Answer:\n\n" + final_response.answer)

    asyncio.run(send_final_query())

