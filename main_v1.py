from flask import Flask, jsonify, request
from getpass import getpass
from genai_stack.stack.stack import Stack
from genai_stack.etl.langchain import LangchainETL
from genai_stack.embedding.langchain import LangchainEmbedding
from genai_stack.vectordb.chromadb import ChromaDB
from genai_stack.prompt_engine.engine import PromptEngine
from genai_stack.model.gpt3_5 import OpenAIGpt35Model
from genai_stack.retriever import LangChainRetriever
from genai_stack.memory.langchain import ConversationBufferMemory
import os

app = Flask(__name__)
container = ['Document-GPT']
retriever = None

@app.route('/', methods=["GET", "POST"])
def mainpage():
	return jsonify(container)

@app.route('/upload', methods=["POST"])
def upload():
	pdf_file = request.files['pdf file']
	pdf_name = pdf_file.filename
	save_path = os.path.join("docs", pdf_name)
	pdf_file.save(save_path)
	document_path = save_path
	etl = LangchainETL.from_kwargs(name="PyPDFLoader", fields={"file_path": save_path})
	finetune(etl)
	return jsonify({"Status": 1, 'message': "Uploaded Successfully!"})


@app.route('/url', methods=["POST"])
def url_fetch():
	doc_link = request.form['url']
	etl = LangchainETL.from_kwargs(name="WebBaseLoader",
                               fields={"web_path": [
                                doc_link
                               ]
                        }
						)
	finetune(etl)
	return jsonify({"Status": 1, 'message': "Uploaded Successfully!"})

def finetune(etl):
	
	api_key = "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"
	
	llm = OpenAIGpt35Model.from_kwargs(parameters={"openai_api_key": api_key})
	config = {
		"model_name": "sentence-transformers/all-mpnet-base-v2",
		"model_kwargs": {"device": "cpu"},
		"encode_kwargs": {"normalize_embeddings": False},
		}
	global retriever

	embedding = LangchainEmbedding.from_kwargs(name="HuggingFaceEmbeddings", fields=config)
	chromadb = ChromaDB.from_kwargs()
	retriever = LangChainRetriever.from_kwargs()
	promptengine = PromptEngine.from_kwargs(should_validate=False)
	memory = ConversationBufferMemory.from_kwargs()
	stack = Stack(
		etl=etl,
        embedding=embedding,
        vectordb=chromadb,
        model=llm,
        prompt_engine=promptengine,
        retriever=retriever,
        memory=memory,
		)
	etl.run()

@app.route('/query', methods=["POST"])
def query():
	global retriever
	question = request.form['question']
	question = question + ' in 2-3 lines'
	response = retriever.retrieve(question)
	return jsonify({"Response": response})
	

if __name__ == '__main__':
	app.run(debug=True)