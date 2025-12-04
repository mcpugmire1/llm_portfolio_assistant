import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Extract API credentials
api_key = os.getenv("OPENAI_API_KEY")
project_id = os.getenv("OPENAI_PROJECT_ID")
org_id = os.getenv("OPENAI_ORG_ID")

# Show what's being loaded for verification
print("🔍 DEBUG")
print(f"API Key: {api_key[:12]}... (len={len(api_key)})")
print(f"Project ID: {project_id}")
print(f"Org ID: {org_id}")

# Initialize OpenAI client
client = OpenAI(
    api_key=api_key,
    project=project_id,
    organization=org_id
)

# Test listing models
try:
    print("🔧 Contacting OpenAI API...")
    models = client.models.list()
    print("✅ Connection successful! Models available:")
    for model in models.data:
        print("-", model.id)
except Exception as e:
    print("❌ Connection failed:")
    print(e)