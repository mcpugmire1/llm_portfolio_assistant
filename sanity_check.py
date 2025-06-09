from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
project_id = os.getenv("OPENAI_PROJECT_ID")
org_id = os.getenv("OPENAI_ORG_ID")

print("🔍 OPENAI_API_KEY:", repr(api_key))
print("📏 Length:", len(api_key))
print("🔍 PROJECT_ID:", repr(project_id))
print("🔍 ORG_ID:", repr(org_id))