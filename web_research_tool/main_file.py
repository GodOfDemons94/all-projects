import os
import streamlit as st
import pickle
import time
import langchain
from langchain.llms import HuggingFaceHub
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import WebBaseLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

st.title("VietBot: Travel Research Tool 📈")
st.sidebar.title("Vietnam Blog URLs")

urls = []
for i in range(3):
    url = st.sidebar.text_input(f"URL {i+1}")
    urls.append(url)

process_url_clicked = st.sidebar.button("Process URLs")
file_path = "faiss_store_llama.pkl"

main_placeholder = st.empty()
llm = ChatGroq(
  temperature = 0.7,
  groq_api_key = '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',
  model_name = "llama3-8b-8192",
  max_tokens=512
)

if process_url_clicked:
    all_docs = []
    for url in urls:
        if url:  # Check if the URL is not empty
            try:
                main_placeholder.text(f"Loading {url}...")
                loader = WebBaseLoader(url)
                docs_from_url = loader.load()
                for doc in docs_from_url:
                    doc.metadata["source"] = url #Correctly set source
                all_docs.extend(docs_from_url)
                main_placeholder.text(f"Loaded {url} ✅")
            except Exception as e:
                main_placeholder.text(f"Error loading {url}: {e} ❌")
        else:
            main_placeholder.text("Skipping empty URL.")

    if all_docs: #Check if any document was loaded
        main_placeholder.text("Splitting text...")
        text_splitter = RecursiveCharacterTextSplitter(
            separators=['\n\n', '\n', '.', ','],
            chunk_size=500,
            chunk_overlap=0
        )
        docs = text_splitter.split_documents(all_docs)

        main_placeholder.text("Creating embeddings...")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore_openai = FAISS.from_documents(docs, embeddings)
        time.sleep(2)

        main_placeholder.text("Saving vectorstore...")
        with open(file_path, "wb") as f:
            pickle.dump(vectorstore_openai, f)
        main_placeholder.text("Vectorstore saved! ✅")
    else:
        main_placeholder.text("No valid URLs provided.")

query = main_placeholder.text_input("Question: ")

if query:
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0: #Check if the file exists before opening
        with open(file_path, "rb") as f:
            vectorstore = pickle.load(f)
            template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

            {context}

            Question: {question}
            Helpful Answer:"""
            QA_CHAIN_PROMPT = PromptTemplate(input_variables=["context", "question"],template=template,)
            qa_chain = RetrievalQA.from_chain_type(llm, retriever=vectorstore.as_retriever(), chain_type_kwargs={"prompt": QA_CHAIN_PROMPT})
            result = qa_chain({"query": query})
            st.header("Answer")
            st.write(result["result"])

            # Display sources, if available
            sources = result.get("sources", "")
            if sources:
                st.subheader("Sources:")
                sources_list = sources.split("\n")  # Split the sources by newline
                for source in sources_list:
                    st.write(source)
    else:
        st.write("Please process URLs first.")