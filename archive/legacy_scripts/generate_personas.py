import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # Load .env file

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_personas_for_story(story):
    """Use GPT-4 to derive personas from story context."""
    prompt = f"""Given this professional story context, identify which stakeholder personas it addresses.

Person: {story.get('Person', '')}
Industry: {story.get('Industry', '')}
Domain: {story.get('Category', '')} / {story.get('Sub-category', '')}
Role: {story.get('Role', '')}

Available personas: Execs, Product Leaders, Eng Leaders, Data/AI, Compliance, Operations, Go-To-Market, Finance/Payments, Healthcare, Transportation/Logistics, End Users, Leaders, Stakeholders

Return ONLY a JSON array of applicable personas, like: ["Execs", "Finance/Payments"]"""

    response = client.chat.completions.create(
        model="gpt-4", messages=[{"role": "user", "content": prompt}], temperature=0
    )

    result = response.choices[0].message.content.strip()
    return json.loads(result)


# Read existing JSONL
input_file = "echo_star_stories_nlp.jsonl"
output_file = "echo_star_stories_nlp_with_personas.jsonl"

with open(input_file) as f_in, open(output_file, 'w') as f_out:
    for line in f_in:
        story = json.loads(line)

        # Generate personas if not already present
        if 'personas' not in story or not story['personas']:
            try:
                story['personas'] = generate_personas_for_story(story)
                print(f"Generated personas for: {story.get('Title', 'Unknown')}")
            except Exception as e:
                print(f"Error for {story.get('Title')}: {e}")
                story['personas'] = ["Stakeholders"]

        f_out.write(json.dumps(story) + '\n')

print("Done. Output written to:", output_file)
