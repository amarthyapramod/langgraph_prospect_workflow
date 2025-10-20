# LangGraph Autonomous Prospect-to-Lead Workflow

An end-to-end AI agent system that autonomously discovers, enriches, scores, and contacts B2B prospects using LangGraph. Built to target B2B companies in the USA with revenues between $20M–$200M.

## 🎯 Features

- **Dynamic Workflow Construction**: Build agent workflows from JSON configuration
- **7 Specialized AI Agents**: Each handling a specific part of the lead generation pipeline
- **ReAct Prompting**: Agents use reasoning + acting pattern for intelligent decision-making
- **Feedback Loop**: Automatically analyzes performance and suggests improvements
- **Modular Architecture**: Easy to extend and customize
- **API Integrations**: Clay, Apollo, Clearbit, SendGrid, Google Sheets

> **Note:** This workflow can fully run using mock data even if API keys are not provided. Real API integrations (Apollo, Clay, Clearbit, SendGrid, etc.) are optional and only needed for live testing. This allows you to test the complete workflow without consuming API credits.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    workflow.json                            │
│              (Single Source of Truth)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              LangGraph Builder                              │
│         (Dynamically constructs workflow)                   │
└────────────────────┬────────────────────────────────────────┘
                     │
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Prospect │→ │Enrichment│→ │ Scoring  │
│  Search  │  │  Agent   │  │  Agent   │
└──────────┘  └──────────┘  └──────────┘
                     │
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Outreach │→ │ Outreach │→ │ Response │
│ Content  │  │ Executor │  │ Tracker  │
└──────────┘  └──────────┘  └──────────┘
                     │
                     ▼
            ┌─────────────────┐
            │    Feedback     │
            │     Trainer     │
            └─────────────────┘
```

## 📦 Project Structure

```
langgraph-prospect-workflow/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py              # Base agent class with ReAct pattern
│   ├── prospectsearchagent.py     # Clay + Apollo prospect discovery
│   ├── dataenrichmentagent.py     # Clearbit data enrichment
│   ├── scoringagent.py            # ICP-based lead scoring
│   ├── outreachcontentagent.py    # Gemini personalized messaging
│   ├── outreachexecutoragent.py   # Email delivery via SendGrid/Apollo
│   ├── responsetrackeragent.py    # Campaign metrics tracking
│   └── feedbacktraineragent.py    # Performance analysis & recommendations
├── langgraph_builder.py           # Main workflow orchestrator
├── workflow.json                  # Workflow configuration
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .env                          # Your API keys (not in git)
├── README.md                     # This file
└── workflow_results.json         # Execution results (generated)
```

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd langgraph-prospect-workflow
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Keys

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your actual API keys:

```bash
# Required
GEMINI_API_KEY=your-gemini-api-key

# Optional (for full functionality)
APOLLO_API_KEY=your-apollo-key
CLAY_API_KEY=your-clay-key
CLEARBIT_KEY=your-clearbit-key
SENDGRID_API_KEY=your-sendgrid-key
SHEET_ID=your-google-sheet-id
GOOGLE_CREDENTIALS_PATH=./credentials.json
```

### 5. Get API Keys (Free Tiers Available)

#### Required:
- **GEMINI**: [https://aistudio.google.com/api-keys](https://aistudio.google.com/api-keys)

#### Optional (system works with mock data if not provided):
- **Apollo**: [https://apollo.io](https://apollo.io) - Free tier: 50 credits/month
- **Clay**: [https://clay.com](https://clay.com) - Free trial available
- **Clearbit**: [https://clearbit.com](https://clearbit.com) - Free trial
- **SendGrid**: [https://sendgrid.com](https://sendgrid.com) - Free tier: 100 emails/day

#### Google Sheets Setup:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Sheets API
4. Create service account credentials
5. Download JSON credentials file
6. Share your Google Sheet with the service account email

## 🎮 How to Run

### Basic Execution

```bash
python langgraph_builder.py
```

This will:
1. Load `workflow.json`
2. Build the LangGraph workflow
3. Execute all 7 agents sequentially
4. Save results to `workflow_results.json`

### Custom Workflow

You can modify `workflow.json` to customize:
- ICP criteria (industry, revenue, location)
- Scoring weights
- Outreach messaging tone
- Signal triggers

Example modification:

```json
{
  "inputs": {
    "icp": {
      "industry": "FinTech",
      "location": "USA",
      "employee_count": { "min": 50, "max": 500 },
      "revenue": { "min": 10000000, "max": 100000000 }
    }
  }
}
```

### Programmatic Usage

```python
from langgraph_builder import LangGraphBuilder

# Initialize
builder = LangGraphBuilder("workflow.json")

# Build workflow
builder.load_workflow()
builder.build_graph()

# Execute with custom initial data
result = builder.execute(initial_data={
    "campaign_name": "Q4_2024_SaaS_Outreach"
})

# Access results
print(f"Success: {result['success']}")
print(f"Leads found: {len(result['data']['prospect_search']['output']['leads'])}")
print(f"Emails sent: {result['data']['send']['output']['success_count']}")
```

## 🤖 Agent Details

### 1. ProspectSearchAgent
**Purpose**: Discover B2B prospects matching ICP criteria

**APIs Used**:
- Clay API (company discovery)
- Apollo API (contact discovery)

**Inputs**:
```json
{
  "icp": { "industry": "SaaS", "location": "USA", ... },
  "signals": ["recent_funding", "hiring_for_sales"]
}
```

**Output**:
```json
{
  "leads": [
    {
      "company": "TechCorp Solutions",
      "contact_name": "John Doe",
      "email": "john@techcorp.com",
      "linkedin": "https://linkedin.com/in/johndoe",
      "title": "VP of Sales",
      "signal": "recent_funding"
    }
  ]
}
```

### 2. DataEnrichmentAgent
**Purpose**: Enrich leads with additional company and contact data

**APIs Used**: Clearbit Enrichment API

**Enrichment Fields**:
- Seniority level (Executive, Manager, IC)
- Technologies used (CRM, marketing tools)
- Company size and funding stage
- Department and role verification

### 3. ScoringAgent
**Purpose**: Score and rank leads based on ICP fit

**Scoring Criteria** (configurable weights):
- Seniority (30%)
- Company size (20%)
- Tech stack match (20%)
- Buying signals (30%)

**Output**: Ranked leads with letter grades (A, B, C, D)

### 4. OutreachContentAgent
**Purpose**: Generate personalized email messages using gemini-2.5-flash

**Features**:
- ReAct reasoning for message strategy
- Company-specific context integration
- Pain point identification
- 3-4 sentence concise emails
- Compelling subject lines

**Example Output**:
```json
{
  "subject": "Quick question about TechCorp's analytics",
  "body": "Hi John,\n\nI noticed TechCorp raised Series B recently..."
}
```

### 5. OutreachExecutorAgent
**Purpose**: Send emails and track delivery

**APIs Used**: 
- Apollo API (primary)
- SendGrid (alternative)

**Tracking**:
- Delivery status
- Campaign ID generation
- Error logging
- Timestamp tracking

### 6. ResponseTrackerAgent
**Purpose**: Monitor email engagement metrics

**Metrics Tracked**:
- Open rate
- Click rate
- Reply rate
- Meeting booking rate
- Response sentiment

### 7. FeedbackTrainerAgent
**Purpose**: Analyze performance and suggest improvements

**Recommendations Include**:
- Subject line optimization
- ICP refinement
- Messaging adjustments
- Volume scaling suggestions

**Output Format**:
```json
{
  "type": "subject_line",
  "priority": "high",
  "suggestion": "Test more personalized subject lines...",
  "expected_impact": "+10-15% open rate",
  "status": "pending_approval"
}
```

## 📊 Workflow Configuration (workflow.json)

The `workflow.json` file is the single source of truth. Key sections:

### Step Definition

```json
{
  "id": "unique_step_id",
  "agent": "AgentClassName",
  "inputs": {
    "field": "value",
    "reference": "{{previous_step.output.field}}"
  },
  "instructions": "What the agent should do",
  "tools": [
    {
      "name": "APIName",
      "config": { "api_key": "{{ENV_VAR}}" }
    }
  ],
  "output_schema": { "expected_output": "type" }
}
```

### Variable Resolution

- **Environment variables**: `{{GEMINI_API_KEY}}` → resolved from `.env`
- **Step outputs**: `{{step_id.output.field}}` → resolved from previous step results
- **Config references**: `{{config.scoring}}` → resolved from workflow config section

## 🧪 Testing

### Run with Mock Data

The system automatically uses mock data if API keys are not configured. This allows you to:
- Test the complete workflow
- Understand data flow between agents
- Verify logic without API costs

### Unit Tests

```bash
pytest tests/
```

### Integration Tests

```bash
pytest tests/integration/ -v
```

## 📈 Example Results

After execution, check `workflow_results.json`:

```json
{
  "success": true,
  "data": {
    "prospect_search": {
      "output": {
        "leads": [...],
        "count": 25
      }
    },
    "scoring": {
      "output": {
        "ranked_leads": [...],
        "average_score": 68.5
      }
    },
    "send": {
      "output": {
        "campaign_id": "campaign_1234567890",
        "success_count": 18,
        "total": 20
      }
    },
    "response_tracking": {
      "output": {
        "metrics": {
          "open_rate": 35.2,
          "reply_rate": 8.5,
          "meeting_rate": 2.8
        }
      }
    },
    "feedback_trainer": {
      "output": {
        "recommendations": [...]
      }
    }
  }
}
```

## 🔧 Extension Guide

### Adding a New Agent

1. **Create agent class** in `agents/newagent.py`:

```python
from agents.base_agent import BaseAgent

class NewAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__("NewAgent", llm)
    
    def _act(self, reasoning, inputs, tools):
        # Your agent logic here
        return {"result": "data"}
```

2. **Add to workflow.json**:

```json
{
  "id": "new_step",
  "agent": "NewAgent",
  "inputs": {...},
  "instructions": "What to do",
  "tools": [...]
}
```

3. **Update workflow edges** if needed (for conditional flows)

### Adding a New API Tool

1. **Add configuration** to step's tools array:

```json
{
  "name": "NewAPI",
  "config": {
    "api_key": "{{NEW_API_KEY}}",
    "endpoint": "https://api.example.com"
  }
}
```

2. **Implement in agent's `_act` method**:

```python
def _act(self, reasoning, inputs, tools):
    new_api_tool = next((t for t in tools if t['name'] == 'NewAPI'), None)
    if new_api_tool:
        result = self._call_new_api(new_api_tool['config'])
```

### Customizing Scoring Logic

Edit `agents/scoringagent.py`:

```python
def _calculate_score(self, lead, criteria):
    score = 0.0
    
    # Add your custom scoring logic
    if lead.get('custom_field') == 'preferred_value':
        score += 30
    
    return score
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'langgraph'`
**Solution**: 
```bash
pip install -r requirements.txt
```

**Issue**: `KeyError: 'GEMINI_API_KEY'`
**Solution**: 
- Ensure `.env` file exists
- Check API key is set correctly
- Restart terminal/IDE after adding `.env`

**Issue**: API rate limits
**Solution**:
- Use mock data for testing
- Implement exponential backoff
- Upgrade to higher API tier

**Issue**: Workflow fails at specific step
**Solution**:
- Check `workflow_results.json` errors array
- Review agent logs
- Validate input/output schemas match

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Best Practices

1. **Start with Mock Data**: Test workflow logic before using real APIs
2. **Incremental Testing**: Test each agent individually before full workflow
3. **Monitor API Usage**: Track API calls to avoid unexpected costs
4. **Version Control**: Keep `workflow.json` in git for A/B testing
5. **Human Review**: Always review FeedbackTrainer recommendations before applying
6. **Gradual Scaling**: Start with small batches, scale up after validation

## 🔒 Security

- **Never commit `.env`**: Add to `.gitignore`
- **Use environment variables**: Don't hardcode API keys
- **Rotate keys regularly**: Especially after development
- **Limit permissions**: Use read-only keys where possible
- **Monitor usage**: Set up alerts for unusual API activity

## 📚 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Gemini API Reference](https://ai.google.dev/api)
- [Apollo API Docs](https://apolloio.github.io/apollo-api-docs/)
- [Clearbit API Docs](https://clearbit.com/docs)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request


## 👥 Authors
Amarthya Pramod k-– Creator


**Note**: This system uses AI-generated code with human review and testing. Always validate outputs before using in production environments.