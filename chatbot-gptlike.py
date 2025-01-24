import streamlit as st
import asyncio

from kai_sdk_python.index import KaiStudio, KaiStudioCredentials
import random
import os

credentials = KaiStudioCredentials(organizationId=os.environ.get("ORGANIZATION_ID"),
                                   instanceId=os.environ.get("INSTANCE_ID"),
                                   apiKey=os.environ.get("API_KEY"))

need_multi_documents = os.environ.get("NEED_MULTI_DOCUMENTS") == "True"
need_following_questions = os.environ.get("NEED_FOLLOWING_QUESTIONS") == "False"

chatbot = KaiStudio(credentials).chatbot()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.conversation_id = ""

st.title("KAI Chatbot for CEVA Logistics")

for message in st.session_state.chat_history:
    st.chat_message(message['from']).write(message['message'])    

if user_message := st.chat_input(placeholder="Write your message here", key="user_input"):
    st.session_state.chat_history.append({ "from": "user", "message": user_message })
    st.chat_message("user").write(user_message)
    async def handle_chat():
        progress_bar = st.progress(0)  
        progress_text = st.empty()  
        progress = 0

        async def update_progress():
            nonlocal progress
            while progress < 90:
                await asyncio.sleep(2)  
                progress += 3 + random.randint(0, 4)  
                progress = min(progress, 90)  
                progress_bar.progress(progress / 100)
                progress_text.text(f"Searching... {progress}%")

        asyncio.create_task(update_progress())

        response = await chatbot.conversation(conversation_id=st.session_state.conversation_id, user_message=user_message, multi_documents=need_multi_documents, user_id="")
        st.session_state.conversation_id = response['id']

        progress = 100
        progress_bar.progress(1.0)
        progress_text.text("Searching... 100%")

        await asyncio.sleep(0.5)  #wait 0.5s to see the 100% progress bar
        progress_bar.empty()
        progress_text.empty()

        if response['message']['action'] == 'SEARCH' and response['message']['datas']['isAnswered']:
            answer_content = "Sources:\n"
            for i, doc in enumerate(response['message']['datas']['documents'], 1):
                answer_content += f"{i}. [{doc['name']}]({doc['url']})\n"
            content = response['message']['content'] + '\n\n' + answer_content
            st.session_state.chat_history.append({ "from": "assistant", "message": content })
            st.chat_message("assistant").write(content)
        else:
            st.session_state.chat_history.append({ "from": "assistant", "message": response['message']['content'] })
            st.chat_message("assistant").write(response['message']['content'])

            
    asyncio.run(handle_chat())