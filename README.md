# streamlit-demo
In this repo, you will find two demo files, which are used to demonstrate how to use the Streamlit with KAI SDK PYTHON.
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
4. Run the Streamlit app.
```bash
streamlit run chatbot-need-identify-document.py
```
or
```bash
streamlit run chatbot-query.py
```
5. Open the Streamlit app in your browser.
