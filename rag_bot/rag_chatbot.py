from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from settings import settings
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough



embedding_instance = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},  # change to "cuda" for GPU
)

def all_minilm_l6_v2():
    """
    Return the embedding instance.
    """
    return embedding_instance


class Vectorstore:
    """
    Class to handle the creation and loading of the vector store."""
    def __init__(self):
        self.embedding = all_minilm_l6_v2()
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    def create_vectorstore(self, pdf_path: str, persist_directory: str = "./chroma_db", collection_name: str = "recipe"):
        """
        Load a PDF, split text, and store in Chroma vector DB.
        """
        loader = PyMuPDFLoader(pdf_path)
        documents = loader.load()
        docs = self.text_splitter.split_documents(documents)
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=self.embedding,
            persist_directory=persist_directory,
            collection_name=collection_name,
        )
        vectorstore.persist()
        return vectorstore

    def load_existing_vectorstore(self, persist_directory: str = "./chroma_db", collection_name: str="" ):
        """
        Load existing Chroma vector store from disk.
        """
        return Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embedding,
            collection_name=collection_name,
        )


class AnswerQuery:
    """
    Class to handle the query and answer process.
    """

    def __init__(self, model_name: str = "llama3-70b-8192"):
        self.llm = ChatGroq(
            model_name=model_name,
            temperature=0.3,
            max_tokens=512,
            api_key=settings.GROQ_API_KEY,
        )

    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def answer_query(
        self, vectorembedding, query: str, collection_name: str = "recipe"
    ):
        vector_store = vectorembedding.load_existing_vectorstore(collection_name=collection_name)

        retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 3, "lambda_mult": 0.5},
        )

        template = """
        Answer using ONLY the context below:
        Context: {context}
        Question: {question}
        If context doesn't match with the question, say: I couldn’t find information about this.
        """

        prompt = PromptTemplate.from_template(template)
        chain = (
            {
                "context": retriever | self.format_docs,
                "question": RunnablePassthrough(),
            }
            | prompt
            | self.llm
        )

        response = chain.invoke(query)
        return response.content
    

