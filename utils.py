from langchain_core.prompts.chat import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders.text import TextLoader
from langchain_text_splitters.latex import LatexTextSplitter
from langchain_openai.chat_models.base import ChatOpenAI
import requests
import tarfile
import os
import gzip


openai_api_key = "Replace with your api key"


chat_model = ChatOpenAI(api_key=openai_api_key,
                        model='gpt-4-turbo')

system_prompt = """
You are now a Mathematical Article Summarization Expert. Your task is to provide a concise and insightful summary of mathematical articles. For each article, please include the following sections:

Overview:
A brief summary of the article's main topics and objectives.
The key questions or problems addressed in the article.

Description of Main Results:
A comprehensive explanation of the primary theorems, propositions, or findings presented in the article.
Include any important definitions, lemmas, or corollaries that support the main results.
Use formal mathematical notation and terminology where appropriate.

Brief Explanation of Proofs:
A concise outline of the proof strategies or methods used to establish the main results.
Highlight any innovative techniques, complex arguments, or notable lemmas employed in the proofs.
Avoid excessive detail but ensure the explanation is informative and accurate.

Maintain a clear and structured format, using bullet points or numbered lists as needed.
\n\n
{context}
"""

prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "Summarize the article: {input}")
])


def get_retriever_from_ref(reference: str,
                           delete: bool = True):
    ltx_splitter = LatexTextSplitter()
    r = requests.get('https://arxiv.org/src/{}'.format(reference))

    s = r.headers['content-disposition']
    index = s.find('filename=')
    filename = s[index + len('filename='):].replace('"', '')
    with open(filename, 'wb') as file:
        file.write(r.content)

    # at this point "filename" is the .gz or .tar.gz archive

    # if .tar.gz, fuse every tex file
    if filename[-6:] == 'tar.gz':

        extract_path = 'temp_folder/'
        with tarfile.open(filename, 'r:gz') as tar:
            tar.extractall(path=extract_path)

        potential_targets = [name for name in os.listdir(path=extract_path) if name[-4:] == '.tex']

        if len(potential_targets) == 1:
            target_file = potential_targets[0]
            loader = TextLoader(extract_path + target_file)
            doc = loader.load()
            splits = ltx_splitter.split_documents(doc)

        else:
            loaded_text = []
            for item in potential_targets:
                loader = TextLoader(extract_path + item)
                for loaded_item in loader.load():
                    loaded_text.append(loaded_item)

            splits = ltx_splitter.split_documents(loaded_text)

        if delete:
            def recursive_removal(directory):
                for name in os.listdir(directory):
                    try:
                        os.remove(directory + '/' + name)
                    except PermissionError:
                        recursive_removal(directory + '/' + name)
                        os.removedirs(directory + '/' + name)

            recursive_removal(extract_path)
            os.removedirs(extract_path)
            os.remove(filename)

    # else its a .gz (other possibilities ??) write the content in a txt file and load it
    else:
        with gzip.open(filename, 'rt') as gz_file:
            with open(filename[:-2] + 'txt', 'w') as file:
                for line in gz_file:
                    file.write(line)

        loader = TextLoader(filename[:-2] + 'txt')
        doc = loader.load()
        splits = ltx_splitter.split_documents(doc)

        if delete:
            os.remove(filename)
            os.remove(filename[:-2] + 'txt')

    vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings(api_key=openai_api_key))
    retriever = vectorstore.as_retriever()

    return retriever


def answer_with_rag(reference: str, article_name: str):
    retriever = get_retriever_from_ref(reference=reference)
    question_answer_chain = create_stuff_documents_chain(chat_model, prompt_template)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    response = rag_chain.invoke({'input': article_name})
    return response['answer']
