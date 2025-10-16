import json
import chromadb
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
from argparse import ArgumentParser

load_dotenv()


class TicketManager:
    def __init__(self, db_path: str = "./chroma_db/", collection_name: str = "it_tickets", openai_client: Optional[OpenAI] = None, embedding_model: str = "text-embedding-3-large"):
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name, metadata={"hnsw:space": "cosine"})
        self.openai_client = openai_client or OpenAI()
        self.embedding_model = embedding_model

    def get_embeddings(self, text: str):
        response = self.openai_client.embeddings.create(
            input=text,
            model=self.embedding_model
        )
        return response.data[0].embedding

    def ingest_tickets(self, file_path: str):
        with open(file_path, 'r') as f:
            tickets = json.load(f)
        for ticket in tickets:
            ticket['ticket_info'] = f"{ticket['title']}: {ticket['description']}"
            ticket_id = ticket['id']
            embedding = self.get_embeddings(ticket['ticket_info'])
            contributors = ticket.get('contributors', [])
            metadata = {
                "title": ticket['title'],
                "description": ticket['description'],
                "status": ticket['status'],
                "contributors": json.dumps(contributors)
            }
            self.collection.add(
                ids=[ticket_id],
                documents=[ticket['ticket_info']],
                metadatas=[metadata],
                embeddings=[embedding]
            )
        print("Ingestion complete.")

    def upsert_ticket(self, ticket_id: str, title: str, description: str, status: str, contributors: List[Dict[str, Any]]):
        embedding = self.get_embeddings(description)
        metadata = {
            "title": title,
            "status": status,
            "contributors": json.dumps(contributors)
        }
        self.collection.upsert(
            ids=[ticket_id],
            documents=[description],
            metadatas=[metadata],
            embeddings=[embedding])
        print(f"Ticket {ticket_id} upserted.")

    def search_tickets(self, query: str, n_results: int = 3):
        query_embedding = self.get_embeddings(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        return results


if __name__ == "__main__":
    parser = ArgumentParser()
    # pass arguments for ingestion, upsert, search, db path
    parser.add_argument("--ingestion", type=str, required=False)
    parser.add_argument("--search", type=str, required=False)
    parser.add_argument("--file_path", type=str, required=False)
    args = parser.parse_args()
    ticket_manager = TicketManager()
    if args.ingestion:
        ticket_manager.ingest_tickets(args.file_path)
    elif args.search:
        results = ticket_manager.search_tickets(args.search)
        print(results)
    else:
        print("No action specified")
    print("Done")

    exit(0)
