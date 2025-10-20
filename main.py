#!/usr/bin/env python3
"""
Main execution script for LangGraph Prospect-to-Lead Workflow
Run this to execute the complete workflow
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from langgraph_builder import LangGraphBuilder
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'workflow_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def print_banner():
    """Print welcome banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     LangGraph Autonomous Prospect-to-Lead Workflow        ║
    ║                                                           ║
    ║                                                           ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_step_summary(step_name: str, data: dict):
    """Print summary of step execution"""
    print(f"\n{'='*60}")
    print(f"Step: {step_name}")
    print(f"{'='*60}")
    
    if step_name == "prospect_search":
        print(f"✓ Leads found: {data.get('count', 0)}")
        print(f"✓ Sources: {', '.join(data.get('sources', []))}")
    
    elif step_name == "enrichment":
        print(f"✓ Leads enriched: {len(data.get('enriched_leads', []))}")
    
    elif step_name == "scoring":
        print(f"✓ Leads scored: {len(data.get('ranked_leads', []))}")
        print(f"✓ Average score: {data.get('average_score', 0):.2f}")
        print(f"✓ Top leads (Grade A): {sum(1 for l in data.get('ranked_leads', []) if l.get('grade') == 'A')}")
    
    elif step_name == "outreach_content":
        print(f"✓ Messages generated: {data.get('count', 0)}")
    
    elif step_name == "send":
        print(f"✓ Emails sent: {data.get('success_count', 0)}/{data.get('total', 0)}")
        print(f"✓ Campaign ID: {data.get('campaign_id', 'N/A')}")
    
    elif step_name == "response_tracking":
        metrics = data.get('metrics', {})
        print(f"✓ Open rate: {metrics.get('open_rate', 0):.1f}%")
        print(f"✓ Click rate: {metrics.get('click_rate', 0):.1f}%")
        print(f"✓ Reply rate: {metrics.get('reply_rate', 0):.1f}%")
        print(f"✓ Meeting rate: {metrics.get('meeting_rate', 0):.1f}%")
    
    elif step_name == "feedback_trainer":
        recs = data.get('recommendations', [])
        print(f"✓ Recommendations: {len(recs)}")
        for rec in recs:
            print(f"  - [{rec['priority'].upper()}] {rec['type']}: {rec['suggestion'][:50]}...")

def print_final_summary(result: dict):
    """Print final execution summary"""
    print("\n" + "="*60)
    print("WORKFLOW EXECUTION COMPLETED")
    print("="*60)
    
    success = result['success']
    status_icon = "✓" if success else "✗"
    status_text = "SUCCESS" if success else "FAILED"
    
    print(f"\n{status_icon} Status: {status_text}")
    print(f"✓ Steps executed: {len(result['history'])}")
    
    if result['errors']:
        print(f"\n⚠ Errors encountered: {len(result['errors'])}")
        for error in result['errors']:
            print(f"  - {error}")
    
    # Calculate key metrics
    data = result['data']
    
    if 'prospect_search' in data:
        leads_found = data['prospect_search']['output'].get('count', 0)
        print(f"\n📊 Key Metrics:")
        print(f"   Prospects discovered: {leads_found}")
    
    if 'scoring' in data:
        avg_score = data['scoring']['output'].get('average_score', 0)
        print(f"   Average lead score: {avg_score:.2f}/100")
    
    if 'send' in data:
        success_count = data['send']['output'].get('success_count', 0)
        total = data['send']['output'].get('total', 0)
        success_rate = (success_count / total * 100) if total > 0 else 0
        print(f"   Email delivery rate: {success_rate:.1f}%")
    
    if 'response_tracking' in data:
        metrics = data['response_tracking']['output'].get('metrics', {})
        meetings = metrics.get('meetings_booked', 0)
        print(f"   Meetings booked: {meetings}")
    
    print(f"\n📁 Results saved to: workflow_results.json")
    print(f"📁 Full logs saved to: workflow_*.log")

def save_pretty_results(result: dict):
    """Save formatted results to JSON file"""
    output_file = Path('workflow_results.json')
    
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    # Also save a human-readable summary
    summary_file = Path('workflow_summary.txt')
    with open(summary_file, 'w') as f:
        f.write("LANGGRAPH WORKFLOW EXECUTION SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Success: {result['success']}\n")
        f.write(f"Steps: {len(result['history'])}\n\n")
        
        for step in result['history']:
            f.write(f"Step: {step['step']}\n")
            f.write(f"Agent: {step['agent']}\n")
            f.write(f"Output: {json.dumps(step['output'], indent=2, default=str)[:200]}...\n")
            f.write("-" * 60 + "\n\n")

def main():
    """Main execution function"""
    try:
        print_banner()
        
        logger.info("Starting workflow execution...")
        
        # Check if workflow.json exists
        if not Path('workflow.json').exists():
            logger.error("workflow.json not found!")
            print("\n❌ Error: workflow.json not found in current directory")
            sys.exit(1)
        
        # Initialize builder
        logger.info("Initializing LangGraph builder...")
        builder = LangGraphBuilder("workflow.json")
        
        # Load and validate workflow
        logger.info("Loading workflow configuration...")
        builder.load_workflow()
        print(f"\n✓ Loaded workflow: {builder.workflow_config['workflow_name']}")
        print(f"✓ Steps: {len(builder.workflow_config['steps'])}")
        
        # Build graph
        logger.info("Building LangGraph...")
        builder.build_graph()
        print("✓ LangGraph constructed successfully")
        
        # Execute workflow
        print("\n" + "="*60)
        print("EXECUTING WORKFLOW")
        print("="*60)
        
        result = builder.execute()
        
        # Print step summaries
        for step in result['history']:
            print_step_summary(step['step'], step['output'])
        
        # Print final summary
        print_final_summary(result)
        
        # Save results
        save_pretty_results(result)
        
        # Exit with appropriate code
        sys.exit(0 if result['success'] else 1)
        
    except KeyboardInterrupt:
        logger.warning("Execution interrupted by user")
        print("\n\n⚠ Execution interrupted by user")
        sys.exit(130)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n\n❌ Fatal error: {e}")
        print("Check log files for details")
        sys.exit(1)

if __name__ == "__main__":
    main()