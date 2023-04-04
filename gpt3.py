import openai
import re
import streamlit as st
from time import time, sleep

with open("openaikey.txt", "r") as key_file:
    openai.api_key = key_file.read().strip()

def gpt3_completion(prompt, engine='text-davinci-003', temp=0.5, top_p=1.0, tokens=2000, freq_pen=0.25, pres_pen=0.0, stop=['<<END>>']):
    max_retry = 5
    retry = 0
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            text = re.sub('\s+', ' ', text)
            
            # Remove prompt from summary
            text = re.sub(r'^.*?RESPONSE:\n\n', '', text, flags=re.DOTALL)
            filename = '%s_gpt3.txt' % time()
            with open('gpt3_logs/%s' % filename, 'w') as outfile:
                outfile.write('PROMPT:\n\n' + prompt + '\n\n==========\n\nRESPONSE:\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                st.error("GPT3 error: %s" % oops)
                return None

            print('Error communicating with OpenAI:', oops)
            sleep(1)

def read_file(file):
    # Read in the file
    if file.name.endswith('.docx'):
        st.error('Error: Microsoft Word files (.docx) are not currently supported. Please upload a text file (.txt) instead.')
        return None
    else:
        # Assume the file is a text file
        text = file.read().decode('utf-8')
        return text
