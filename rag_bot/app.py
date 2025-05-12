import streamlit as st
from rag_chatbot import Vectorstore, AnswerQuery

st.set_page_config(page_title="PDF Q&A Bot", page_icon="📄", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: #4CAF50;'>📄 PDF Q&A Chatbot</h1>
    <p style='text-align: center;'>Upload a PDF, then ask questions and get AI-powered answers.</p>
    <hr>
""", unsafe_allow_html=True)

# Session state setup
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "pdf_ready" not in st.session_state:
    st.session_state.pdf_ready = False

# Upload section (once)
if not st.session_state.pdf_ready:
    uploaded_file = st.file_uploader("📎 Upload your PDF", type=["pdf"])

    if uploaded_file:
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.read())

        st.success("✅ Document uploaded successfully!")

        vs = Vectorstore()
        with st.spinner("🔍 Embedding and indexing your PDF..."):
            vs.create_vectorstore("temp.pdf")

        st.session_state.vectorstore = vs
        st.session_state.pdf_ready = True

# Q&A Section (only after PDF is processed)
if st.session_state.pdf_ready:
    st.markdown("### 💬 Ask a question related to your document:")
    query = st.text_input("Your question:")
    if st.button("Get Answer") and query:
        qa = AnswerQuery()
        with st.spinner("🤖 Generating your answer..."):
            answer = qa.answer_query(vectorembedding=st.session_state.vectorstore, query=query)

        st.markdown("#### ✅ Answer:")
        st.markdown(
            f"""
            <div style='background-color: #e6f4ea; padding: 16px; border-radius: 10px;
                        color: #1a1a1a; font-size: 16px; border: 1px solid #b6d7c9;
                        white-space: pre-wrap; font-family: monospace;'>
                {answer}
            </div>
            """,
            unsafe_allow_html=True
        )
