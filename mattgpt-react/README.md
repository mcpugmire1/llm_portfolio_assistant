# MattGPT React - AI Portfolio Assistant

A modern React-based AI portfolio assistant powered by RAG (Retrieval-Augmented Generation), deployed on AWS infrastructure.

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   React     │─────▶│ API Gateway  │─────▶│   Lambda    │
│  Frontend   │      │  (REST API)  │      │ (RAG Logic) │
└─────────────┘      └──────────────┘      └─────────────┘
      │                                            │
      │                                            ▼
      ▼                                     ┌─────────────┐
┌─────────────┐                            │  Pinecone   │
│ CloudFront  │                            │  (Vectors)  │
│   + S3      │                            └─────────────┘
└─────────────┘                                   │
                                                  ▼
                                           ┌─────────────┐
                                           │   OpenAI    │
                                           │   GPT-4o    │
                                           └─────────────┘
```

## 🛠️ Tech Stack

**Frontend:**
- React 18 + Vite + TypeScript
- Tailwind CSS (purple theme: #8B5CF6)
- Modern chat UI with suggestion chips

**Backend:**
- Python 3.11 Lambda functions
- RAG pipeline with Pinecone vector search
- OpenAI GPT-4o-mini for response generation
- Nonsense query filtering

**Infrastructure:**
- AWS CDK (TypeScript)
- API Gateway (REST API with CORS)
- S3 (static hosting + data storage)
- CloudFront (CDN)

**Data:**
- Pinecone vector database (existing index)
- 115+ STAR-formatted career stories
- Nonsense filter patterns (JSONL)

---

## 📁 Project Structure

```
mattgpt-react/
├── frontend/              # React app
│   ├── src/
│   │   ├── components/    # Chat UI components
│   │   ├── services/      # API client
│   │   ├── App.tsx        # Main app with state
│   │   └── main.tsx       # Entry point
│   ├── package.json
│   └── vite.config.ts
├── backend/               # Lambda functions
│   ├── lambdas/
│   │   ├── rag_handler.py # Main RAG logic
│   │   └── requirements.txt
│   └── prompts/
│       └── agy_system.txt # Agy system prompt
├── infrastructure/        # AWS CDK
│   ├── lib/
│   │   ├── backend-stack.ts    # Lambda + API Gateway
│   │   ├── frontend-stack.ts   # S3 + CloudFront
│   │   └── storage-stack.ts    # S3 buckets
│   └── bin/app.ts         # CDK app entry
├── data/
│   └── nonsense_filters.jsonl
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

1. **Node.js 18+** and **npm**
2. **Python 3.11+**
3. **AWS CLI** configured with credentials
4. **AWS CDK** installed globally:
   ```bash
   npm install -g aws-cdk
   ```
5. **OpenAI API Key**
6. **Pinecone API Key** and existing index

---

## 📦 Installation

### 1. Clone and Setup

```bash
cd mattgpt-react
```

### 2. Configure Environment Variables

```bash
# Copy and edit the environment template
cp .env.example .env

# Edit .env with your actual credentials
nano .env
```

**Required variables:**
```env
OPENAI_API_KEY=sk-your-key-here
PINECONE_API_KEY=your-key-here
PINECONE_INDEX=mattgpt
PINECONE_NAMESPACE=default
CDK_DEFAULT_ACCOUNT=123456789012
CDK_DEFAULT_REGION=us-east-1
```

---

## 🏗️ Deployment

### Step 1: Deploy Infrastructure (CDK)

```bash
cd infrastructure

# Install dependencies
npm install

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy all stacks
cdk deploy --all --require-approval never
```

**This will create:**
- ✅ S3 bucket for stories data
- ✅ Lambda function for RAG handler
- ✅ API Gateway REST API
- ✅ S3 bucket for frontend
- ✅ CloudFront distribution

**Save the outputs:**
- `APIEndpoint`: Your API Gateway URL
- `WebsiteURL`: Your CloudFront URL

---

### Step 2: Upload Stories Data to S3

```bash
# Get the stories bucket name from CDK output
BUCKET_NAME="mattgpt-stories-123456789012"

# Upload nonsense filters
aws s3 cp ../data/nonsense_filters.jsonl s3://$BUCKET_NAME/nonsense_filters.jsonl

# If you have stories data, upload it too
# aws s3 cp ../../echo_star_stories_nlp.jsonl s3://$BUCKET_NAME/stories.jsonl
```

---

### Step 3: Build and Deploy Frontend

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env file with API URL
echo "VITE_API_BASE_URL=https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod" > .env

# Build the app
npm run build

# Deploy to S3
FRONTEND_BUCKET="mattgpt-frontend-123456789012"
aws s3 sync dist/ s3://$FRONTEND_BUCKET/ --delete

# Invalidate CloudFront cache
DISTRIBUTION_ID="E1234567890ABC"
aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*"
```

---

## 🧪 Local Development

### Run Frontend Locally

```bash
cd frontend
npm install
npm run dev
```

Visit: `http://localhost:3000`

**Note:** You'll need the backend API deployed to test queries.

---

### Test Backend Lambda Locally

```bash
cd backend/lambdas

# Install dependencies
pip install -r requirements.txt

# Test the handler
python -c "
from rag_handler import lambda_handler
event = {'body': '{\"query\": \"Tell me about agile transformation\"}'}
result = lambda_handler(event, None)
print(result)
"
```

---

## 🎨 Frontend Features

### Landing Page (Empty State)
- Purple gradient header with Agy avatar (🐾)
- 6 suggestion chips (2 columns)
- Centered max-width design (900px)

### Conversation View
- User messages: light blue bubbles, right-aligned
- Agy messages: white bubbles, left-aligned with avatar
- Source cards below answers (max 3, purple links)
- Thinking indicator with animated dots
- Sticky input at bottom

### Styling
- Purple primary: `#8B5CF6`
- Background: `#F9FAFB`
- Borders: `#E5E7EB`
- Font: `system-ui`

---

## 🔧 Backend Logic

### RAG Pipeline Flow

1. **Input**: User query via API Gateway
2. **Nonsense Filter**: Check against patterns in `nonsense_filters.jsonl`
   - If matched: return canned response (greeting, identity, etc.)
3. **Vector Search**: Query Pinecone for top 7 relevant stories
   - Uses `sentence-transformers/all-MiniLM-L6-v2` embeddings
4. **Context Formation**: Format top 3 stories with STAR structure
5. **LLM Generation**: Call OpenAI GPT-4o-mini with:
   - Agy system prompt
   - Formatted context
   - User query
6. **Response**: Return answer + sources

---

## 📊 API Reference

### POST /ask

**Request:**
```json
{
  "query": "How did Matt scale engineering teams?"
}
```

**Response:**
```json
{
  "answer": "Matt scaled engineering teams from 4 to 150+ people at JPMorgan...",
  "sources": [
    {
      "id": "story-123",
      "title": "Agile Transformation at JPMorgan",
      "client": "JPMorgan Chase",
      "score": 0.89
    }
  ],
  "isNonsense": false
}
```

---

## 🗂️ Data Files

### nonsense_filters.jsonl

Pattern-based filter for non-portfolio queries:

```json
{"category": "greeting", "patterns": ["hello", "hi", "hey"]}
{"category": "identity", "patterns": ["who are you", "what are you"]}
```

---

## 🚢 Deployment Workflow

1. **Make changes** to frontend or backend code
2. **Test locally** if possible
3. **Deploy backend** (if Lambda changed):
   ```bash
   cd infrastructure
   cdk deploy MattGPTBackendStack
   ```
4. **Build and deploy frontend**:
   ```bash
   cd frontend
   npm run build
   aws s3 sync dist/ s3://mattgpt-frontend-ACCOUNT/ --delete
   aws cloudfront create-invalidation --distribution-id DIST_ID --paths "/*"
   ```

---

## 🔒 Security Notes

- **API Keys**: Stored in environment variables (not committed)
- **S3 Buckets**: Block public access, CloudFront OAI only
- **CORS**: Configured for all origins (tighten for production)
- **Lambda Permissions**: Least privilege (read-only S3 access)

---

## 📝 Customization

### Change Agy's Personality

Edit: `backend/prompts/agy_system.txt`

### Update Suggestion Chips

Edit: `frontend/src/App.tsx` → `SUGGESTION_CHIPS` array

### Adjust Theme Colors

Edit: `frontend/tailwind.config.js` → `theme.extend.colors`

---

## 🐛 Troubleshooting

### "No stories found" errors
- ✅ Check Pinecone index exists and has data
- ✅ Verify `PINECONE_INDEX` and `PINECONE_NAMESPACE` env vars
- ✅ Ensure embeddings are uploaded to Pinecone

### CORS errors in frontend
- ✅ Verify API Gateway CORS settings
- ✅ Check `VITE_API_BASE_URL` in frontend `.env`

### Lambda timeout errors
- ✅ Increase timeout in `backend-stack.ts` (currently 30s)
- ✅ Check OpenAI API latency
- ✅ Optimize Pinecone query (reduce `top_k`)

---

## 📈 Future Enhancements

- [ ] Add authentication (Cognito)
- [ ] Implement conversation history
- [ ] Add feedback mechanism (thumbs up/down)
- [ ] Create admin panel for story management
- [ ] Add analytics dashboard
- [ ] Support for multi-language queries
- [ ] Implement caching for common queries

---

## 🤝 Contributing

This is a personal portfolio project. For questions or collaboration:

**Matt Pugmire**
📧 [mcpugmire@gmail.com](mailto:mcpugmire@gmail.com)
🔗 [linkedin.com/in/matthewpugmire](https://linkedin.com/in/matthewpugmire)

---

## 📄 License

Personal use only. Not licensed for redistribution.

---

**Built with ❤️ and 🐾 by Matt Pugmire**
