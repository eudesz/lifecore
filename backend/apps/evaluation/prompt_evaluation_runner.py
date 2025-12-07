"""
Prompt Evaluation Runner
Executes prompts through the chat pipeline and collects responses
"""
import os
import sys
import json
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.models import User
from apps.agents_v2.views import analyze


def run_prompt_batch(user_id, prompts):
    """
    Execute a batch of prompts through the chat pipeline
    
    Args:
        user_id: User ID to test with
        prompts: List of prompt dictionaries
        
    Returns:
        List of results with responses
    """
    results = []
    user = User.objects.get(id=user_id)
    
    print(f"\n=== Running {len(prompts)} prompts for user: {user.username} ===\n")
    
    for i, prompt_data in enumerate(prompts, 1):
        prompt = prompt_data["prompt"]
        data_type = prompt_data["data_type"]
        complexity = prompt_data["complexity"]
        
        print(f"[{i}/{len(prompts)}] Testing: {data_type} ({complexity})")
        print(f"  Prompt: {prompt[:60]}...")
        
        start_time = time.time()
        
        try:
            # Call analyze function directly
            payload = {
                'query': prompt,
                'user_id': str(user_id)
            }
            
            response_data = analyze(payload, request=None)
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            result = {
                "data_type": data_type,
                "complexity": complexity,
                "expected_agent": prompt_data.get("expected_agent", "unknown"),
                "prompt": prompt,
                "response": response_data.get("final_text", ""),
                "references": response_data.get("references", []),
                "agent_used": response_data.get("category", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "execution_time_ms": execution_time_ms,
                "success": True
            }
            
            print(f"  ✓ Response: {result['response'][:80]}...")
            print(f"  Agent: {result['agent_used']} | Time: {execution_time_ms}ms")
            
        except Exception as e:
            import traceback
            execution_time_ms = int((time.time() - start_time) * 1000)
            result = {
                "data_type": data_type,
                "complexity": complexity,
                "expected_agent": prompt_data.get("expected_agent", "unknown"),
                "prompt": prompt,
                "response": "",
                "references": [],
                "agent_used": "error",
                "timestamp": datetime.now().isoformat(),
                "execution_time_ms": execution_time_ms,
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            print(f"  ✗ Error: {str(e)[:60]}...")
        
        results.append(result)
        print()
        
        # Small delay to avoid overwhelming the system
        time.sleep(0.5)
    
    return results


def save_results(results, output_file):
    """Save results to JSON file"""
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        output_file
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Results saved to: {output_path}")
    return output_path


def save_results_markdown(results, output_file):
    """Save results as markdown table"""
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        output_file
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Prompt Evaluation Results\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Prompts:** {len(results)}\n\n")
        
        # Summary statistics
        success_count = sum(1 for r in results if r['success'])
        avg_time = sum(r['execution_time_ms'] for r in results) / len(results)
        
        f.write(f"**Success Rate:** {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)\n")
        f.write(f"**Avg Execution Time:** {avg_time:.0f}ms\n\n")
        
        f.write("---\n\n")
        
        # Group by data type
        by_type = {}
        for r in results:
            if r['data_type'] not in by_type:
                by_type[r['data_type']] = []
            by_type[r['data_type']].append(r)
        
        for data_type, type_results in by_type.items():
            f.write(f"## {data_type.upper()}\n\n")
            
            for i, r in enumerate(type_results, 1):
                f.write(f"### {i}. {r['complexity']}\n\n")
                f.write(f"**Prompt:** {r['prompt']}\n\n")
                
                if r['success']:
                    f.write(f"**Response:** {r['response']}\n\n")
                    f.write(f"**Agent:** {r['agent_used']}\n")
                    f.write(f"**Time:** {r['execution_time_ms']}ms\n")
                    f.write(f"**References:** {len(r['references'])}\n\n")
                else:
                    f.write(f"**ERROR:** {r.get('error', 'Unknown error')}\n\n")
                
                f.write("---\n\n")
    
    print(f"✓ Markdown saved to: {output_path}")
    return output_path


def print_summary(results):
    """Print summary statistics"""
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    
    success_count = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"\nTotal Prompts: {total}")
    print(f"Successful: {success_count} ({success_count/total*100:.1f}%)")
    print(f"Failed: {total - success_count}")
    
    # Average execution time
    avg_time = sum(r['execution_time_ms'] for r in results) / total
    print(f"\nAvg Execution Time: {avg_time:.0f}ms")
    
    # By data type
    print("\n--- By Data Type ---")
    by_type = {}
    for r in results:
        if r['data_type'] not in by_type:
            by_type[r['data_type']] = []
        by_type[r['data_type']].append(r)
    
    for data_type, type_results in by_type.items():
        success = sum(1 for r in type_results if r['success'])
        print(f"{data_type}: {success}/{len(type_results)}")
    
    # By agent
    print("\n--- By Agent ---")
    agent_counts = {}
    for r in results:
        if r['success']:
            agent = r['agent_used']
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
    
    for agent, count in sorted(agent_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{agent}: {count}")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    from prompt_generator import get_all_prompts
    
    # Get all prompts
    prompts = get_all_prompts()
    print(f"Loaded {len(prompts)} prompts")
    
    # Run evaluation
    results = run_prompt_batch(user_id=5, prompts=prompts)
    
    # Save results
    save_results(results, "evaluation_results.json")
    save_results_markdown(results, "evaluation_results.md")
    
    # Print summary
    print_summary(results)
