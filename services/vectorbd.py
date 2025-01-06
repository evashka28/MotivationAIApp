import bs4
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.conf import OPENAI_API_KEY

#это работа с векторной бд у нас ее нет, но можешь просто глянуть
def embed_textt():
    pdf_path = r"..\sourсe\withouttables.pdf"
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    print("KKL")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=70, separators=["\n\n"])
    splits = text_splitter.split_documents(docs)
    print("JI")
    datastore = FAISS.from_documents(documents=splits, embedding=OpenAIEmbeddings(
        openai_api_key=OPENAI_API_KEY))
    datastore.save_local(r"..\vector_database")
    return datastore

def embed_text():
    pdf_path = r"..\sourсe\licence.txt"
    with open(pdf_path, encoding='utf-8') as f:
        docs = f.read()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50, separators=["\n\n"])
    #splits = text_splitter.create_documents([docs])
    splits = text_splitter.split_text(docs)
    #for i in splits:
    for i, s in enumerate(splits):
        splits[i] = s.replace("\n\n", "\n")
    print("JI")
    datastore = FAISS.from_texts(texts=splits, embedding=OpenAIEmbeddings(model="text-embedding-3-large",
        openai_api_key=OPENAI_API_KEY))
    datastore.save_local(r"..\vector_database")
    return datastore

#embed_text()


