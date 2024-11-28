import streamlit as st
import asyncio

from kai_sdk_python.index import KaiStudio, KaiStudioCredentials

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
            'knowledge manager',  
            need_multi_documents,
            need_following_questions
        )
        if final_response:

            if final_response['answer'] == '':
                messages.append({"from": "assistant", "message": "I don't know the answer to that question."})
                st.chat_message("assistant").write("I don't know the answer to that question.")
            else:
                answer_content = 'Answer:\n\n"' + final_response['answer']
                if need_following_questions:
                    following_questions = "\n\nFollowing questions:\n"
                    for i, question in enumerate(final_response['followingQuestions'], 1):
                        following_questions += f"{i}. {question}\n"
                    answer_content += following_questions
                
                if need_multi_documents:
                    documents = "\n\nDocuments:\n"
                    for i, doc in enumerate(final_response['documents'], 1):
                        documents += f"{i}. [{doc['name']}]({doc['url']})\n"
                    answer_content += documents
                messages.append({"from": "assistant", "message": answer_content})
                st.chat_message("assistant").write(answer_content)
        else:
            st.info("Please add your correct key to initialize the chatbot")
            st.stop()

    asyncio.run(send_final_query())
