from qdrant_client import QdrantClient
import os
import cohere
from dotenv import load_dotenv
import openai
from langsmith import traceable, get_current_run_tree
load_dotenv()

qdrant_client = QdrantClient(url="http://localhost:6333")
co = cohere.ClientV2(api_key=os.getenv("COHERE_API_KEY"))
client = openai.OpenAI(
    base_url="https://api.cerebras.ai/v1",
    api_key=os.environ.get("CEREBRAS_API_KEY")
)
@traceable(
    name="embed_query",
    run_type="embedding",
    metadata={"model":"embed-v4.0","input_type":"classification","output_dimension":1536,"embedding_types":["float"]}
)
def generate_embedding(text):
    response = co.embed(
        model="embed-v4.0",
        inputs=[
            {
                "content": [
                    {
                        "type": "text",
                        "text": text
                    }
                ]
            }
        ],
        input_type="classification",
        output_dimension=1536,
        embedding_types=["float"],
    )
    current_run = get_current_run_tree()
    if current_run and hasattr(response, "usage"):
        current_run.metadata["usage_metadata"] = {
            "input_tokens": response.usage.prompt_tokens,
            "total_tokens": response.usage.total_tokens,
        }

    return response.embeddings.float[0]

@traceable(
    name="retrieving_data",
    run_type="retriever"
)
def retrieve_data(query,k=5):
    query_embedding = generate_embedding(query)
    results = qdrant_client.query_points(
        collection_name="Amazon-items-collection-01",
        query=query_embedding,
        limit=k
    )
    retrieved_context_ids=[]
    retrieved_context=[]
    similarity_scores=[]
    retrieved_context_ratings=[]

    for result in results.points:
        retrieved_context_ids.append(result.payload["parent_asin"])
        retrieved_context.append(result.payload["description"])
        similarity_scores.append(result.score)
        retrieved_context_ratings.append(result.payload["average_rating"])
    return {
        "retrieved_context_ids":retrieved_context_ids,
        "retrieved_context":retrieved_context,
        "similarity_scores":similarity_scores,
        "retrieved_context_ratings":retrieved_context_ratings

    }


@traceable(
    name="processing_context",
    run_type="prompt"
)
def process_context(context):
    formated_context=""
    for id,chunk,rating in zip(context["retrieved_context_ids"],context["retrieved_context"],context["retrieved_context_ratings"]):
        formated_context += f"-ID: {id}, rating: {rating}, context:{chunk}\n"
    return formated_context

@traceable(
    name="building_prompt",
    run_type="prompt"
)
def build_prompt(preprocessed_data,question):
    prompt = f"""
    You are a shopping assistant that can answer questions about the products in stock.
    You will be given a question and a list of context.

    Instructions:
    - You need to answer the question based on the provided context only.
    - Never use the word context and refer to it as the available products.

    Context:{preprocessed_data}

    Question:{question}
     """
    return prompt

@traceable(
    name="generating_answer",
    run_type="llm"
)
def generate_answer(prompt):
    response = client.chat.completions.create(
    model="gpt-oss-120b",
    messages=[{"role":"system", "content":prompt}],
    reasoning_effort="low"
)
    current_run = get_current_run_tree()
    if current_run:
        current_run.metadata["usage_metadata"] = {
            "input_tokens":response.usage.prompt_tokens,
            "output_tokens":response.usage.completion_tokens,
            "total_tokens":response.usage.total_tokens
        }
    return response.choices[0].message.content


@traceable(
    name="rag_pipeline"
)
def rag_pipeline(query):
    retrieved_data = retrieve_data(query)
    preprocessed_data = process_context(retrieved_data)
    prompt = build_prompt(preprocessed_data,query)
    response = generate_answer(prompt)
    return {
        "answer":response,
        "context_ids":retrieved_data["retrieved_context_ids"],
        "context":retrieved_data["retrieved_context"],
        "score":retrieved_data["similarity_scores"],
        "rating":retrieved_data["retrieved_context_ratings"]
    }
    