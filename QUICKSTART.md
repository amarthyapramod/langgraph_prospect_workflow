# Quick Start Guide

Get up and running with the LangGraph Prospect-to-Lead Workflow in 5 minutes!

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies (1 min)

```bash
# Clone and navigate to project
cd langgraph-prospect-workflow

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Configure gemini Key (1 min)

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your gemini key
# GEMINI_API_KEY=sk-your-key-here
```

Get your Gemini API key from: https://aistudio.google.com/api-keys

### Step 3: Run the Workflow (3 min)

```bash
# Execute the complete workflow
python main.py
```

That's it! The workflow will:
1. Search for 10 mock prospects (no API keys needed for demo)
2. Enrich their data
3. Score and rank them
4. Generate personalized emails
5. Simulate sending
6. Track engagement metrics
7. Provide improvement recommendations

## 📊 Understanding the Output

After execution, check these files:

### workflow_results.json
Complete execution data with all intermediate outputs

```json
{
  "success": true,
  "data": {
    "prospect_search": { "leads": [...], "count": 10 },
    "scoring": { "average_score": 68.5 },
    "send": { "success_count": 18 }
  }
}
```

### workflow_summary.txt
Human-readable summary of the execution

### workflow_*.log
Detailed logs with reasoning traces from each agent

## 🎯 Next Steps

### 1. Add Real API Keys (Optional)

To use real data instead of mocks, add these to `.env`:

```bash
# For prospect discovery
APOLLO_API_KEY=your-key-here      # apollo.io - Free tier
CLAY_API_KEY=your-key-here         # clay.com - Free trial

# For enrichment
CLEARBIT_KEY=your-key-here         # clearbit.com - Free trial

# For email sending
SENDGRID_API_KEY=your-key-here     # sendgrid.com - 100/day free
```

### 2. Customize Your ICP

Edit `workflow.json` to target your ideal customers:

```json
{
  "inputs": {
    "icp": {
      "industry": "FinTech",           // Change industry
      "location": "USA",
      "employee_count": { "min": 50, "max": 500 },  // Adjust size
      "revenue": { "min": 10000000, "max": 100000000 }  // Revenue range
    },
    "signals": ["recent_funding", "hiring_for_sales"]  // Add signals
  }
}
```

### 3. Adjust Scoring Criteria

Modify scoring weights in `workflow.json`:

```json
{
  "config": {
    "scoring": {
      "seniority_weight": 0.4,      // Prioritize decision-makers
      "company_size_weight": 0.2,
      "tech_stack_weight": 0.1,
      "signal_weight": 0.3
    }
  }
}
```

### 4. Customize Messaging

Change outreach tone and persona:

```json
{
  "inputs": {
    "persona": "CEO",               // Options: SDR, CEO, Founder
    "tone": "professional"          // Options: friendly, professional, casual
  }
}
```

## 🔍 Inspecting Agent Reasoning

Each agent uses ReAct (Reasoning + Acting) prompting. View their thought process:

```python
from langgraph_builder import LangGraphBuilder

builder = LangGraphBuilder("workflow.json")
builder.load_workflow()
builder.build_graph()
result = builder.execute()

# Get reasoning from specific agent
prospect_agent = builder.agents.get('ProspectSearchAgent')
if prospect_agent:
    reasoning_history = prospect_agent.get_reasoning_history()
    print(reasoning_history)
```

## 🧪 Testing Individual Agents

Test agents independently before running full workflow:

```python
from agents.prospectsearchagent import ProspectSearchAgent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
agent = ProspectSearchAgent(llm)

result = agent.execute(
    inputs={
        "icp": {
            "industry": "SaaS",
            "location": "USA"
        },
        "signals": ["recent_funding"]
    },
    instructions="Find 5 prospects",
    tools=[]
)

print(result)
```

## 📈 Monitoring Performance

### View Live Logs

```bash
tail -f workflow_*.log
```

### Check Campaign Metrics

```python
import json

with open('workflow_results.json') as f:
    results = json.load(f)

metrics = results['data']['response_tracking']['output']['metrics']
print(f"Open Rate: {metrics['open_rate']}%")
print(f"Reply Rate: {metrics['reply_rate']}%")
print(f"Meetings: {metrics['meetings_booked']}")
```

## 🐛 Troubleshooting

### Issue: Import errors

```bash
# Ensure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: OpenAI API errors

```bash
# Check your API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"

# Verify it starts with 'sk-'
```

### Issue: Workflow fails at specific step

Check the error in `workflow_results.json`:

```python
import json

with open('workflow_results.json') as f:
    results = json.load(f)

for error in results.get('errors', []):
    print(error)
```

## 🚀 Production Deployment

### 1. Environment Variables

Use proper secret management:

```bash
# AWS
aws secretsmanager create-secret --name openai-key --secret-string "sk-..."

# Or use environment-specific .env files
.env.development
.env.staging
.env.production
```

### 2. Add Error Handling

Wrap execution in try-catch:

```python
from langgraph_builder import LangGraphBuilder

try:
    builder = LangGraphBuilder("workflow.json")
    result = builder.execute()
    
    if not result['success']:
        # Send alert
        send_alert(result['errors'])
        
except Exception as e:
    # Log and notify
    logger.error(f"Critical failure: {e}")
    send_critical_alert(e)
```

### 3. Schedule Execution

Use cron or task scheduler:

```bash
# Run daily at 9 AM
0 9 * * * cd /path/to/project && ./venv/bin/python main.py
```

Or use Celery for async execution:

```python
from celery import Celery

app = Celery('workflow')

@app.task
def run_workflow():
    builder = LangGraphBuilder("workflow.json")
    return builder.execute()
```

## 📚 Learn More

- **Full Documentation**: See [README.md](README.md)
- **API Reference**: Check individual agent files in `/agents/`
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **Workflow Customization**: Edit `workflow.json`

## 💡 Pro Tips

1. **Start Small**: Test with 5-10 prospects before scaling
2. **Monitor Costs**: Track OpenAI API usage at platform.openai.com
3. **A/B Testing**: Create multiple workflow.json files for different approaches
4. **Iterate Fast**: Use mock data to test logic before spending API credits
5. **Review Feedback**: Always check FeedbackTrainer recommendations

## 🎥 Demo Script

Want to create a demo video? Follow this script:

1. **Introduction** (30 sec)
   - Show project structure
   - Explain the 7-agent workflow

2. **Configuration** (1 min)
   - Open workflow.json
   - Highlight ICP settings
   - Show scoring criteria

3. **Execution** (2 min)
   - Run `python main.py`
   - Narrate each step as it executes
   - Show terminal output

4. **Results** (1 min)
   - Open workflow_results.json
   - Highlight key metrics
   - Show recommendations

5. **Customization** (30 sec)
   - Demonstrate changing ICP
   - Re-run to show different results

## ✅ Checklist

Before submission, ensure you have:

- [ ] Installed all dependencies
- [ ] Configured OpenAI API key
- [ ] Run workflow successfully
- [ ] Generated workflow_results.json
- [ ] Reviewed logs for errors
- [ ] Tested with custom ICP settings
- [ ] Created demo video (2-5 mins)
- [ ] Prepared GitHub repository
- [ ] Updated README with your details

## 🎓 Learning Path

1. **Day 1**: Setup and run with defaults
2. **Day 2**: Understand each agent's role
3. **Day 3**: Customize ICP and scoring
4. **Day 4**: Add real API integrations
5. **Day 5**: Create demo and optimize workflow

## 📞 Support

Questions? Check:
- README.md for detailed docs
- workflow_*.log for execution details
- GitHub Issues for common problems

Happy coding! 🚀