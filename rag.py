import json
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.prompts import PromptTemplate
from argparse import ArgumentParser

load_dotenv()

client = OpenAI()
embedding_model = "text-embedding-3-large"
chroma_client = chromadb.PersistentClient(path="./chroma_db/")
collection = chroma_client.get_or_create_collection(
    name="it_tickets", metadata={"hnsw:space": "cosine"})


def get_embeddings(text: str):
    response = client.embeddings.create(
        input=text,
        model=embedding_model
    )
    return response.data[0].embedding


def ticket_lookup(query: str):
    results = collection.query(
        query_embeddings=[get_embeddings(query)],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )
    output = ""
    documents = results.get("documents")
    metadatas = results.get("metadatas")
    ids = results.get("ids")
    if documents and metadatas:
        for id, doc, meta in zip(ids[0], documents[0], metadatas[0]):
            contributors_str = meta.get("contributors", "[]")
            contributors = []
            for c in json.loads(contributors_str):
                name = c.get("contributor_name", "")
                action = c.get("action_taken", "")
                contributors.append(f"{name}: {action}")
            output += (f"ID: {id}\n"
                       f"Title: {meta.get('title')}\n"
                       f"Description: {doc}\n"
                       f"Contributors: {contributors}\n"
                       f"Status: {meta.get('status')}\n"
                       "----\n")
    return output if output else "No relevant tickets found."


def RAG_pipeline(query: str):
    llm = init_chat_model(model="gpt-4o-mini", temperature=0)
    template = """
    You are an IT support assistant. 
    You have the following similar tickets:

    {tickets}

    Your job:
    - Summarize the likely issue in one paragraph.
    - Suggest clear, actionable troubleshooting steps.
    - Prioritize the steps.
    - Include escalation guidance if needed.
    - Write in plain language, do not repeat contributor actions verbatim.

    Output a complete troubleshooting guide.
    """
    prompt = PromptTemplate(
        input_variables=["tickets"],
        template=template
    )
    tickets_text = ticket_lookup(query)
    response = llm.invoke([
        {"role": "user", "content": prompt.format(tickets=tickets_text)}
    ])
    return response.content


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--query", type=str, required=True)
    args = parser.parse_args()
    response = RAG_pipeline(args.query)
    print(response)
    exit(0)
