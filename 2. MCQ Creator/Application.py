import streamlit as st
import os
from dotenv import load_dotenv
from pinecone import Pinecone as PineconeClient
from langchain.llms import GooglePalm
from langchain.chains.question_answering import load_qa_chain
from langchain.schema import HumanMessage
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from utils import load_docs, split_docs
from langchain_community.vectorstores import Pinecone 
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings



load_dotenv()

# Applying Styling
st.markdown(""" 
<style>
div.stButton > button:first-child {
    background-color: #0099ff;
    color:#ffffff;
}
div.stButton > button:hover {
    background-color: #00ff00;
    color:#FFFFFF;
}
</style>""", unsafe_allow_html=True)

# Initialize the Pinecone client
Pinecone_API = os.environ["PINECONE_API_KEY"]
PineconeClient(api_key=Pinecone_API, environment="gcp-starter")

# Creating Session State Variable
if 'Google Palm API' not in st.session_state:
    st.session_state['Google Palm API'] = ''

st.title('🧠 MCQ Wizard')

# Sidebar to capture the Pinecone API key
st.sidebar.title("😎🗝️")
st.session_state['Pinecone Client Index'] = st.sidebar.text_input("Pinecone Client Index")
st.sidebar.image('2. MCQ Creator/pinecone_logo.png', width=200, use_column_width=True)

# Sidebar to capture the Google Palm API key
st.sidebar.title("😎🗝️")
st.session_state['Google Palm API'] = st.sidebar.text_input("Google API Key:", type="password")
st.sidebar.image('2. MCQ Creator/google_api.jpg', width=200, use_column_width=True)

# Input for directory
directory = st.text_input('Enter the directory containing PDF files:')
# submitted1 = st.button('Submit')
question_content = st.text_input("Could you kindly share the content from your document? I'd be delighted to help generate MCQs from it! 😊📄")
# question_content = "Brain"
submitted2 = st.button('GO')

# Load documents if directory is provided and button is clicked
if submitted2:
    if directory:
        if st.session_state['Google Palm API']:
            pdf_files = load_docs(directory)
            if pdf_files:
                splitted_pdf_files = split_docs(pdf_files)

                # Hugging Face LLM for creating Embeddings for documents
                embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

                index_name = st.session_state['Pinecone Client Index']
                index = Pinecone.from_documents(splitted_pdf_files, embeddings, index_name=index_name)
                
                Google_API = st.session_state['Google Palm API']

                # Create Google Palm LLM model
                llm = GooglePalm(google_api_key=Google_API, temperature=0.2)

                chain = load_qa_chain(llm, chain_type="stuff")
                
                relevant_docs = index.similarity_search(question_content, k=2)
                response = chain.run(input_documents=relevant_docs, question=question_content)

                response_schemas = [
                    ResponseSchema(name="question", description="Question generated from provided input text data."),
                    ResponseSchema(name="choices", description="Available options for a multiple-choice question in comma separated."),
                    ResponseSchema(name="answer", description="Correct answer for the asked question.")
                ]

                output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
                format_instructions = output_parser.get_format_instructions()

                prompt = ChatPromptTemplate( 
                    messages=[HumanMessagePromptTemplate.from_template(
                        """When a text input is given by the user, 
                        please generate five multiple choice questions from it along with the correct answer. 
                        \n{format_instructions}\n{user_prompt}"""
                    )], input_variables=["user_prompt"], partial_variables={"format_instructions": format_instructions})

                final_query = prompt.format_prompt(user_prompt=response)
                final_query_output = llm.invoke(final_query.to_messages())
                st.write(final_query_output)
            else:
                st.error("No PDF files found in the directory. Please enter a valid directory.")
        else:
            st.error("Please provide Google Palm API key.")
    else:
        st.warning("Please enter the directory.")
