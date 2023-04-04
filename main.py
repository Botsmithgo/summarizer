import os
from time import time
import textwrap
import streamlit as st
from file_operations import open_file, save_file
from gpt3 import gpt3_completion, read_file

def main():
    st.title('Botsmith Summarizer')

    session_id = str(time()).replace('.', '')  # Create a unique identifier for the current session
    uploaded_file = st.file_uploader('Upload a file to summarize and watch the magic happen!', type='txt', accept_multiple_files=False)
    file_contents = None
    if uploaded_file is not None:
        if uploaded_file.type == 'text/plain':
            file_contents = uploaded_file.read().decode('utf-8')
        else:
            st.error('Please upload a plain text file (txt).')
    #else:
       #st.info('Upload a file to summarize and watch the magic happen!');
        
    prompt_options = {
        'Interview Summary': 'prompts/firstprompt.txt',
        'General Summary': 'prompts/generalsummary.txt'
    }
    prompt_selection = st.selectbox(
        'Select the type of sumary you want Botsmith to generate!',
        ['Select your the type of summary', *list(prompt_options.keys())],
        index=0
    )
    user_input1 = ''
    user_input2 = ''
    user_input3 = ''

    if prompt_selection != 'Select your the type of summary':
        selected_prompt = prompt_options[prompt_selection]
        summary_prompt = open_file(selected_prompt)
        
        # Show the text boxes only when "Interview Summary" is selected
        if prompt_selection == 'Interview Summary':
            col1, col2, col3 = st.columns(3)
            with col1:
                user_input1 = st.text_input('Enter key word/sentence 1', '')
            with col2:
                user_input2 = st.text_input('Enter key word/sentence 2', '')
            with col3:
                user_input3 = st.text_input('Enter key word/sentence 3', '')

    if st.button('Summarize'):
        if file_contents is not None:
            chunks = textwrap.wrap(file_contents, width=4000)
            result = ''
            with st.spinner('Botsmith is churning through your text faster than a caffeinated cheetah!'):
                progress_bar = st.progress(0)
                for count, chunk in enumerate(chunks, 1):
                    print(f"Processing chunk {count}/{len(chunks)}")
                    prompt = summary_prompt.replace('<<SUMMARY>>', chunk)
                    prompt = prompt.encode(encoding='ASCII', errors='ignore').decode()
                    summary = gpt3_completion(prompt)
                    print(f"Generated summary for chunk {count}: {summary}")

                    if summary is not None:
                        result += summary + '\n\n'
                    else:
                        st.error("Error generating summary. Please try again.")

                    progress = int(count / len(chunks) * 100)
                    progress_bar.progress(progress)
                    print(f"Combined result: {result}")

                if prompt_selection == 'General Summary':
                    # Use the combined result of summarized chunks for the general summary prompt
                    generalsummary_prompt = open_file('prompts/generalsummary.txt')
                    formatted_generalsummary = generalsummary_prompt.replace('<<SUMMARY>>', result)
                    final_output = gpt3_completion(formatted_generalsummary)
                    print(f"Final output: {final_output}")
                else:  # This will be executed when prompt_selection is not 'General Summary'
                    promptinput_prompt = open_file('prompts/secondprompt.txt')
                    formatted_summary = promptinput_prompt.replace('<<SUMMARY>>', result)
                    final_output = gpt3_completion(formatted_summary)

                st.write('Final output:')
                st.write(final_output)

                if final_output is not None:
                    filename = f'output_{time()}.txt'
                    save_file(final_output, filename)
                    st.success(f'Summary saved to {filename}.')
                else:
                    st.error('An error occurred during the summarization process. Please try again.')

    if st.button('Reset'):
        st.experimental_rerun()

if __name__ == '__main__':
    main()
