# ==============================================================================
# FIX FOR CHROMA TELEMETRY
# ==============================================================================
def _patch_chroma_telemetry():
    """
    Attempts to find and override the buggy 'capture' function in ChromaDB
    by checking multiple possible module paths.
    """
    def _do_nothing(*args, **kwargs):
        pass

    try:
        import chromadb.telemetry.product.posthog
        chromadb.telemetry.product.posthog.Posthog.capture = _do_nothing
        print("ChromaDB telemetry forcefully disabled by patching.")
        return
    except ImportError:
        pass

    try:
        import chromadb.telemetry.posthog
        chromadb.telemetry.posthog.Posthog.capture = _do_nothing
        print("ChromaDB telemetry forcefully disabled by patching.")
        return
    except ImportError:
        pass
    
    print("Could not find ChromaDB telemetry module to patch.")

_patch_chroma_telemetry()
# ==============================================================================
# ==============================================================================
import os
from dotenv import load_dotenv
import google.generativeai as genai
from chromadb.config import Settings
import chromadb
from chromadb.utils import embedding_functions

# Load environment variables
load_dotenv()

#Configuration
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is required. Please set it in your .env file.")

genai.configure(api_key=api_key)

#Loading the knowledge base


def load_knowledge_base(folder_path):
    all_text_blocks = []
    print(f"Loading knowledge from: {os.path.abspath(folder_path)}")
    try:
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
                    all_text_blocks.extend(f.read().split('---'))
        print(f"Successfully loaded {len(all_text_blocks)} knowledge blocks.")
        return all_text_blocks
    except FileNotFoundError:
        print(f"ERROR: The folder '{folder_path}' was not found.")
        print("Please make sure your .txt files are in a folder named 'knowledge_base' inside your project folder.")
        return []
    
knowledge_base = load_knowledge_base('info')
if not knowledge_base:
    raise SystemExit("Couldn’t load KB")

client = chromadb.PersistentClient(path="./chroma_db", settings=Settings(anonymized_telemetry=False))

sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")

collection = client.get_or_create_collection(
    name="rdr2_knowledge",
    embedding_function=sentence_transformer_ef
)

if collection.count() == 0:
    texts = [blk.strip() for blk in knowledge_base if len(blk.strip()) >= 20]
    ids = [f"doc_{i}" for i in range(len(texts))]
    
    collection.add(
        documents=texts,
        ids=ids
    )
    print("Knowledge base embedded and stored in ChromaDB.")
else:
    print(f"ChromaDB already has {collection.count()} documents.")


#The retrieval system

def find_best_context(user_question, collection, top_n=5):
    results = collection.query(
        query_texts=[user_question],
        n_results=top_n
    )
    
    if not results['documents'] or not results['documents'][0]:
        return "", float('inf')

    top_blocks = results['documents'][0]
    combined = "\n---\n".join(top_blocks)
    best_score = results['distances'][0][0]

    print(f"--> Retrieved {len(top_blocks)} blocks (best distance={round(best_score, 3)}).")
    return combined, best_score





#The generation system

def generate_answer(context, question):
    prompt_template = """
    You are a helpful and knowledgeable assistant whose only purpose is to answer questions and provide pro tips about the video game Red Dead Redemption 2.

    Assume that any mention of 'the game' or similar vague references mean 'Red Dead Redemption 2'.
    
    Use the following CONTEXT to answer the user's QUESTION.

    Your answer must be based *only* on the information within the provided CONTEXT.

    If the CONTEXT does not contain the information needed to answer the QUESTION you MUST respond with: "Sorry, I don't have enough information to answer that question."
    
    if the user asks about anything other than Red Dead Redemption 2, you MUST respond with: "I'm sorry, I can only answer questions about Red Dead Redemption 2." Do not add any other explanation.

    CONTEXT:
    ---
    {retrieved_context}
    ---

    QUESTION:
    {user_question}

    YOUR ANSWER:
    """
    
    prompt = prompt_template.format(retrieved_context=context, user_question=question)
    
    
    try:
        
        model = genai.GenerativeModel('gemini-2.5-pro') 
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while contacting the API: {e}"
# def get_or_create_local_embeddings(knowledge_base, cache_path="embeddings.pkl"):
#     if os.path.exists(cache_path):
#         print(f"Loading embeddings from cache: {cache_path}")
#         return pickle.load(open(cache_path, "rb"))

#     print("No cache found—computing local embeddings...")
    
    
#     def clean(text):
#         return re.sub(r'\s+', ' ', text.strip().lower())

#     texts = [clean(blk) for blk in knowledge_base if len(blk.strip()) >= 20]

#     embeddings = embedding_model.encode(texts, convert_to_tensor=True)
    
#     embedded = [(embeddings[i].cpu().numpy(), texts[i]) for i in range(len(texts))]
#     pickle.dump(embedded, open(cache_path, "wb"))
#     print("Embedding complete and cached.")
#     return embedded

#The main agent loop
def run_agent():
    if not knowledge_base:
        return
    
    print("\nWelcome! I am your Red Dead Redemption 2 expert agent.")
    print("Ask me anything about the game, or type 'quit' to exit.")
    
    while True:
        user_question = input("\n[YOU] Ask a question: ")
        
        if user_question.lower() == 'quit':
            print("Thanks for playing! Goodbye.")
            break
            
        print("--> Searching knowledge base...")
        
        retrieved_context, distance = find_best_context(user_question, collection)


        
        
        if distance > 2.2:
            print("[AGENT] I'm sorry, I can only answer questions about Red Dead Redemption 2.")
            continue
            
        print("--> Asking the AI...")
        answer = generate_answer(retrieved_context, user_question)
        
        print(f"\n[AGENT] {answer}")


if __name__ == "__main__":
    run_agent()

    
