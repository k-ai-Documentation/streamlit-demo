# streamlit-demo
In this repo, you will find two demo files, which are used to demonstrate how to use the Streamlit with [KAI SDK PYTHON](https://github.com/k-ai-Documentation/sdk-python/tree/version2.0).
## chatbot-need-identify-document.py
This file is used to demonstrate how to use the Streamlit with KAI SDK PYTHON to create a chatbot with 2 steps. The first step is to correct and identify the question from user, the second step is to search the correct question from the knowledge base and get an answer.
## chatbot-query.py
This file is used to demonstrate how to use the Streamlit with KAI SDK PYTHON to create a chatbot with 1 step. The first step is to search the question from the knowledge base and get an answer.

## How to use
1. Clone the repo to your local machine.
2. Install the required packages.
```bash
pip install -r requirements.txt
```
Our kai_sdk_python package is on github, you can install it by:
```bash
pip install git+https://github.com/k-ai-Documentation/sdk-python.git@version2.0
```
or you can install it by:
```bash
pip install -r requirements.txt
```

3. Set the environment variables.
You can set the environment variables in the env.sh file or in the terminal.
```bash
#!/bin/bash
export ORGANIZATION_ID="Your Organization ID"
export INSTANCE_ID="Your Instance ID"
export API_KEY="Your API Key"

export NEED_MULTI_DOCUMENTS="True" # Set this to "True" if you want to search multiple documents, otherwise set it to "False"
export NEED_FOLLOWING_QUESTIONS="True" # Set this to "True" if you want to ask following questions, otherwise set it to "False"
```
#### Run and set your env
- local
```
source env.sh # Mac or Linux
```
or
```
. .\env.sh # Windows
source ./env.sh # If you have installed git for windows
```
- docker
```
docker run -e ORGANIZATION_ID="Your Organization ID" -e INSTANCE_ID="Your Instance ID" -e API_KEY="Your API Key" -e NEED_MULTI_DOCUMENTS="True" -e NEED_FOLLOWING_QUESTIONS="True" -p 8501:8501 kai-studio-python:latest
```
- kubernetes
You need to delfine a deployment.yaml file with env variables.
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: kai-studio-python
spec:
  containers:
  - name: kai-studio-python
    image: kai-studio-python:latest
    env:
    - name: ORGANIZATION_ID
      value: "Your Organization ID"
    - name: INSTANCE_ID
      value: "Your Instance ID"
    - name: API_KEY
      value: "Your API Key"
    - name: NEED_MULTI_DOCUMENTS
      value: "True"
    - name: NEED_FOLLOWING_QUESTIONS
      value: "True"
```
4. Run the Streamlit app.
```bash
streamlit run chatbot-need-identify-document.py
```
or
```bash
streamlit run chatbot-query.py
```
5. Open the Streamlit app in your browser.

## Process
### chatbot-gptlike.py
1. Send user message 

chatbot.conversation return data like :
```json 
{
  "id": "conversation_id",
  "message": {
    "action": "QUALIFY_QUESTION or SEARCH", // represent the step of action of the chatbot, it will indicate you if the chatbot search across your KB or he is asking you more contextual information to identify exactly what you are looking for
    "content": "chat message",
    "datas": {} // response from the search.query sub endpoint 
  }
}
```
### chatbot-need-identify-document.py
1. Send user message to search.identify_specific_document.

search.identify_specific_document return data like :
```json
{
    "isFinal": false,
    "question": "Could you please specify what 'key' refers to? Are you asking about a specific document, method, or concept?"
}
```
This step will correct and help user find the right question.
If isFinal is False, repeat step 1.

2. If isFinal is True, send question found by search.identify_specific_document to search.query.
### chatbot-query.py
1. Send user message to search.query.

## Code explanation
### Importing Dependencies
```python
import streamlit as st
import asyncio

from kai_sdk_python.index import KaiStudio, KaiStudioCredentials

import json
import os
```
You need to import KaiStudio and KaiStudioCredentials from the kai_sdk_python package.
The KAI Studio SDK, used to interact with the KAI platform through API calls.

### Initializing KAI Studio Credentials
```python
credentials = KaiStudioCredentials(organizationId=os.environ.get("ORGANIZATION_ID"),
                                   instanceId=os.environ.get("INSTANCE_ID"),
                                   apiKey=os.environ.get("API_KEY"))
```
You can initialize the KAI Studio Credentials by setting the environment variables.

For Saas users, you need to set the environment variables as follows:
```bash
export ORGANIZATION_ID="Your Organization ID"
export INSTANCE_ID="Your Instance ID"
export API_KEY="Your API Key"
```
For On-Premise users, you need to set the environment variables as follows:
```bash
export HOST="Your Host"
export API_KEY="Your API Key" # This is optional depending on your deployment
```

### Conversation Configuration Settings
```python
need_multi_documents = os.environ.get("NEED_MULTI_DOCUMENTS") == "True"
need_following_questions = os.environ.get("NEED_FOLLOWING_QUESTIONS") == "True"
```
chatbot.conversation need 4 arguments

    >conversation_id: 'id of the conversation if you already setup a conversation'

    >user_message: 'message of the user'

    >multi_documents: 'true if you want to search across multiple documents, false if you want to retrieve an answer following only one document'

    >user_id: '(optional) user identifier to log for this query'


### Searching Configuration Settings
```python
need_multi_documents = os.environ.get("NEED_MULTI_DOCUMENTS") == "True"
need_following_questions = os.environ.get("NEED_FOLLOWING_QUESTIONS") == "True"
```
search.query need 5 arguments, you can set the environment variables to control the behavior of the search.query function.

    >query: 'query to search on the semantic index'

    >user: '(optional) user identifier to log for this query'

    >impersonate: 'name a profile to imitate the style of answer. eg: Knowledge manager or Sales man'

    >multiDocuments: 'true if you want to search across multiple documents, false if you want to retrieve an answer following only one document'
    
    >needFollowingQuestions: 'true if you want to the API purpose multiple next questions, else false'


### Creating Search Object
```python
search = KaiStudio(credentials).search()
```
Here, the KaiStudio class is instantiated using the credentials, and the .search() method creates a search object.

This search object allows interaction with the KAI API, particularly to execute searches based on user queries.

### Initializing Session State
```python
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'isFinal' not in st.session_state:
    st.session_state.isFinal = False
```
st.session_state is a Streamlit feature used to persist variables across interactions (like a conversation history).

chat_history holds the entire conversation (messages).

### Save messages in chat_history
```python
messages = st.session_state.chat_history
for message in messages:
    st.chat_message(message['from']).write(message['message'])
```

### Handling User Input and Messages
```python
if question := st.chat_input(placeholder="Ask me anything..."):
    messages.append({"from": "user", "message": question})
    st.chat_message("user").write(question)
```

### Asynchronous Chat Logic
```python
async def handle_chat():
    response = await search.identify_specific_document(messages)
    messages.append({"from": "assistant", "message": response['question']})

    if not response['isFinal']:
        st.chat_message("assistant").write(response['question'])
    else:
        st.session_state.isFinal = True
        st.chat_message("assistant").write("Your question is confirmed: " + response['question'] + "\n\n please wait for the answer...")
asyncio.run(handle_chat())
```
- This function handle_chat() handles the user query asynchronously.
- search.identify_specific_document(messages) sends the user’s message history to the KAI platform to identify specific question relevant to the conversation.
- The platform returns a response with a question and an isFinal flag:
  - If isFinal is False, the chatbot asks a follow-up question to clarify the query.
  - If isFinal is True, the query is confirmed, and the bot prepares to retrieve the final answer.

### Handling Final Query and Displaying the Answer
```python
if st.session_state.isFinal:
    async def send_final_query():
        final_response = await search.query(
            st.session_state.chat_history[-1]['message'],
            "userid",
            'knowledge manager',
            need_multi_documents,
            need_following_questions
        )
        messages.append({"from": "assistant", "message": final_response.answer})
        ...
    asyncio.run(send_final_query())
```
- After the user’s query is fully clarified, this section is triggered to send the final query to KAI using search.query().
- The query() function takes the last user message, a user ID, and the flags for multi-document responses and follow-up questions. It returns a final_response containing the final answer.
- The chatbot appends the answer to the conversation history and displays it to the user.
