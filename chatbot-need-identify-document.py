import streamlit as st
import asyncio

from kai_sdk_python.index import KaiStudio, KaiStudioCredentials

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

if 'isFinal' not in st.session_state:
    st.session_state.isFinal = False

st.title("KAI Chatbot")

messages = st.session_state.chat_history
for message in messages:
    st.chat_message(message['from']).write(message['message'])

if question := st.chat_input(placeholder="Ask me anything..."):
    messages.append({"from": "user", "message": question})
    st.chat_message("user").write(question)

    async def handle_chat():
        response = await search.identify_specific_document(messages)
        if response and 'response' in response:
            answer_content = response["response"]
            messages.append({"from": "assistant", "message": answer_content['question']})

            if not answer_content['isFinal']:
                st.chat_message("assistant").write(answer_content['question'])
            else:
                st.session_state.isFinal = True
                st.chat_message("assistant").write("Your question is comfirmed: " + answer_content['question'] + "\n\n please wait for the answer...")
        else:
            st.info("Please add your correct key to initialize the chatbot")
            st.stop()

    asyncio.run(handle_chat())

if st.session_state.isFinal:
    async def send_final_query():
        final_response = await search.query(
            st.session_state.chat_history[-1]['message'], 
            "userid",
            'knowledge manager',  
            need_multi_documents,
            need_following_questions
        )
        if final_response and final_response.answer != '':
            messages.append({"from": "assistant", "message": final_response.answer})
            answer_content = 'Answer:\n\n"' + final_response.answer
            if need_following_questions:
                answer_content += '\n\nFollowing questions:\n\n' + json.dumps(final_response.followingQuestions) 
            if need_multi_documents:
                answer_content += '\n\nDocuments:\n\n' + json.dumps(final_response.documents)
            st.chat_message("assistant").write(answer_content)
        elif final_response and final_response.answer == '':
            st.chat_message("assistant").write("Sorry, I don't have an answer for your question.")

        st.session_state.isFinal = False

    asyncio.run(send_final_query())

