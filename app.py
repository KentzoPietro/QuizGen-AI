import streamlit as st
import os
import json
import tempfile
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.llms.groq import Groq



def save_uploaded_file(uploaded_file):
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return temp_dir

def quiz_generator(file_dir): 
    Settings.llm = Groq(model="llama3-70b-8192", api_key="YOUR_API_KEY_HERE")
    prompt = '''Generate 10 Multiple Choice Questions based off the uploaded file. 
                Prefix the choices with letters with A,B,C,D
                Format your answer in JSON. Return the raw output only. The answer is the index of the correct option. 
                [{'question': ''}, {'options': []}, {'answer': 0}]'''
    
    docs = SimpleDirectoryReader(file_dir).load_data()
    print(f"Loaded {len(docs)} documents.")

    index = VectorStoreIndex.from_documents(docs)
    print("Index created.")

    query_engine = index.as_query_engine()
    result = query_engine.query(prompt)
    print(result.response)
    return json.loads(result.response)

def main():
        st.markdown(
        """
        <style>
        .stApp {
            background-color: black;
        }
        .stApp * {
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
st.title("QuizGen AI")
st.write("Upload a PDF document, and this app will generate quiz questions from it.")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if st.button("Start") and uploaded_file:
        file_dir = save_uploaded_file(uploaded_file)
        quiz = quiz_generator(file_dir)
        if 'quiz' not in st.session_state:
            st.session_state.quiz = quiz
        if 'answers' not in st.session_state:
            st.session_state.answers = [None] * len(quiz)
        if 'show_answers' not in st.session_state:
            st.session_state.show_answers = False
    
if 'quiz' in st.session_state:
        quiz = st.session_state.quiz
        st.header("Generated Quiz")
        for i, num in enumerate(quiz):
            st.radio(f'{i + 1} | ' + num['question'], options=num['options'], key=f'question_{i}', 
                     on_change=lambda i=i: st.session_state.answers.__setitem__(i, st.session_state[f'question_{i}']))
        
        if st.button("Submit Quiz"):
            score = 0
            for i, answer in enumerate(st.session_state.answers):
                if answer == quiz[i]['options'][quiz[i]['answer']]:
                    score += 1
            st.session_state.show_answers = True
            st.write(f'Your score: {score} out of {len(quiz)}')

if 'show_answers' in st.session_state and st.session_state.show_answers:
        st.header("Correct Answers")
        for i, num in enumerate(st.session_state.quiz):
            st.write(f'Question {i + 1}: {num["question"]}')
            st.write(f'Correct Answer: {num["options"][num["answer"]]}')

if __name__ == "__main__":
    main()
