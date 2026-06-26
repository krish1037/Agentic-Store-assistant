import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Load environment variables
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    # Use a dummy key to prevent validation errors at module load time during test collection
    api_key = "DUMMY_KEY_FOR_TESTS"

# Instantiate LLM (gemini-2.5-flash as requested)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key,
    temperature=0.0,
)

# Instantiate Embeddings (gemini-embedding-001 with output_dimensionality=768 as requested)
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=api_key,
    output_dimensionality=768,
)
