"""
Evaluation Report Generator
Generates comprehensive reports from evaluated results
"""
import json
import csv
from datetime import datetime
from collections import defaultdict


def generate_report(evaluated_results, output_file="evaluation_report.md"):
    """
    Generate a comprehensive markdown report
    
    Args:
        evaluated_results: List of evaluated result dictionaries
        output_file: Output filename
    """
    successful = [r for r in evaluated_results if r.get('success', False)]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Header
        f.write("# LifeCore Prompt Evaluation Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Executive Summary
        f.write("## Executive Summary\n\n")
        
        total = len(evaluated_results)
        success_count = len(successful)
        
        if successful:
            avg_overall = sum(r['overall_score'] for r in successful) / len(successful)
            data_usage_pct = sum(1 for r in successful if r['uses_data']) / len(successful) * 100
            
            f.write(f"- **Total Prompts Tested:** {total}\n")
            f.write(f"- **Successful Executions:** {success_count} ({success_count/total*100:.1f}%)\n")
            f.write(f"- **Average Overall Score:** {avg_overall:.2f}/10\n")
            f.write(f"- **Data Usage Rate:** {data_usage_pct:.1f}%\n\n")
            
            # Score interpretation
            if avg_overall >= 8:
                f.write("**Assessment:** ✅ **Excellent** - System performs very well\n")
            elif avg_overall >= 7:
                f.write("**Assessment:** ✓ **Good** - System performs well with minor issues\n")
            elif avg_overall >= 5:
                f.write("**Assessment:** ⚠️ **Fair** - System needs improvement\n")
            else:
                f.write("**Assessment:** ❌ **Poor** - System requires significant work\n")
        else:
            f.write("- **Total Prompts Tested:** {total}\n")
            f.write("- **Successful Executions:** 0\n")
            f.write("\n**Assessment:** ❌ **Critical** - No successful executions\n")
        
        f.write("\n---\n\n")
        
        if not successful:
            f.write("## No successful results to analyze\n\n")
            return
        
        # Overall Statistics
        f.write("## Overall Statistics\n\n")
        
        avg_relevance = sum(r['relevance_score'] for r in successful) / len(successful)
        avg_context = sum(r['context_score'] for r in successful) / len(successful)
        avg_completeness = sum(r['completeness_score'] for r in successful) / len(successful)
        avg_time = sum(r['execution_time_ms'] for r in successful) / len(successful)
        
        f.write("| Metric | Score/Value |\n")
        f.write("|--------|-------------|\n")
        f.write(f"| Relevance Score | {avg_relevance:.2f}/10 |\n")
        f.write(f"| Context Score | {avg_context:.2f}/10 |\n")
        f.write(f"| Completeness Score | {avg_completeness:.2f}/10 |\n")
        f.write(f"| Overall Score | {avg_overall:.2f}/10 |\n")
        f.write(f"| Avg Execution Time | {avg_time:.0f}ms |\n")
        f.write(f"| Data Usage Rate | {data_usage_pct:.1f}% |\n\n")
        
        # Score Distribution
        f.write("### Score Distribution\n\n")
        excellent = sum(1 for r in successful if r['overall_score'] >= 9)
        good = sum(1 for r in successful if 7 <= r['overall_score'] < 9)
        fair = sum(1 for r in successful if 5 <= r['overall_score'] < 7)
        poor = sum(1 for r in successful if r['overall_score'] < 5)
        
        f.write("| Category | Count | Percentage |\n")
        f.write("|----------|-------|------------|\n")
        f.write(f"| Excellent (9-10) | {excellent} | {excellent/len(successful)*100:.1f}% |\n")
        f.write(f"| Good (7-8) | {good} | {good/len(successful)*100:.1f}% |\n")
        f.write(f"| Fair (5-6) | {fair} | {fair/len(successful)*100:.1f}% |\n")
        f.write(f"| Poor (0-4) | {poor} | {poor/len(successful)*100:.1f}% |\n\n")
        
        f.write("---\n\n")
        
        # Per Data Type Analysis
        f.write("## Analysis by Data Type\n\n")
        
        by_type = defaultdict(list)
        for r in successful:
            by_type[r['data_type']].append(r)
        
        for data_type in sorted(by_type.keys()):
            type_results = by_type[data_type]
            f.write(f"### {data_type.upper()}\n\n")
            
            avg_score = sum(r['overall_score'] for r in type_results) / len(type_results)
            data_usage = sum(1 for r in type_results if r['uses_data']) / len(type_results) * 100
            avg_time = sum(r['execution_time_ms'] for r in type_results) / len(type_results)
            
            f.write(f"- **Prompts:** {len(type_results)}\n")
            f.write(f"- **Avg Score:** {avg_score:.2f}/10\n")
            f.write(f"- **Data Usage:** {data_usage:.0f}%\n")
            f.write(f"- **Avg Time:** {avg_time:.0f}ms\n\n")
            
            # Agent distribution for this type
            agent_counts = defaultdict(int)
            for r in type_results:
                agent_counts[r['agent_used']] += 1
            
            f.write("**Agents Used:**\n")
            for agent, count in sorted(agent_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- {agent}: {count}\n")
            
            f.write("\n")
        
        f.write("---\n\n")
        
        # Per Complexity Analysis
        f.write("## Analysis by Complexity\n\n")
        
        by_complexity = defaultdict(list)
        for r in successful:
            by_complexity[r['complexity']].append(r)
        
        f.write("| Complexity | Count | Avg Score | Data Usage |\n")
        f.write("|------------|-------|-----------|------------|\n")
        
        for complexity in sorted(by_complexity.keys()):
            comp_results = by_complexity[complexity]
            avg_score = sum(r['overall_score'] for r in comp_results) / len(comp_results)
            data_usage = sum(1 for r in comp_results if r['uses_data']) / len(comp_results) * 100
            f.write(f"| {complexity} | {len(comp_results)} | {avg_score:.2f}/10 | {data_usage:.0f}% |\n")
        
        f.write("\n---\n\n")
        
        # Agent Performance
        f.write("## Agent Performance\n\n")
        
        by_agent = defaultdict(list)
        for r in successful:
            by_agent[r['agent_used']].append(r)
        
        f.write("| Agent | Requests | Avg Score | Avg Time |\n")
        f.write("|-------|----------|-----------|----------|\n")
        
        for agent in sorted(by_agent.keys()):
            agent_results = by_agent[agent]
            avg_score = sum(r['overall_score'] for r in agent_results) / len(agent_results)
            avg_time = sum(r['execution_time_ms'] for r in agent_results) / len(agent_results)
            f.write(f"| {agent} | {len(agent_results)} | {avg_score:.2f}/10 | {avg_time:.0f}ms |\n")
        
        f.write("\n---\n\n")
        
        # Top Performing Prompts
        f.write("## Top Performing Prompts\n\n")
        
        top_results = sorted(successful, key=lambda x: x['overall_score'], reverse=True)[:5]
        
        for i, r in enumerate(top_results, 1):
            f.write(f"### {i}. {r['data_type']} - Score: {r['overall_score']:.1f}/10\n\n")
            f.write(f"**Prompt:** {r['prompt']}\n\n")
            f.write(f"**Response:** {r['response'][:200]}...\n\n")
            f.write(f"**Agent:** {r['agent_used']} | **Time:** {r['execution_time_ms']}ms\n\n")
            f.write(f"**Strengths:** {', '.join(r['strengths'])}\n\n")
        
        f.write("---\n\n")
        
        # Lowest Performing Prompts
        f.write("## Prompts Needing Improvement\n\n")
        
        bottom_results = sorted(successful, key=lambda x: x['overall_score'])[:5]
        
        for i, r in enumerate(bottom_results, 1):
            f.write(f"### {i}. {r['data_type']} - Score: {r['overall_score']:.1f}/10\n\n")
            f.write(f"**Prompt:** {r['prompt']}\n\n")
            f.write(f"**Response:** {r['response'][:200]}...\n\n")
            f.write(f"**Agent:** {r['agent_used']} | **Time:** {r['execution_time_ms']}ms\n\n")
            f.write(f"**Weaknesses:** {', '.join(r['weaknesses'])}\n\n")
            f.write(f"**Explanation:** {r['explanation']}\n\n")
        
        f.write("---\n\n")
        
        # Recommendations
        f.write("## Recommendations\n\n")
        
        # Based on scores
        if avg_overall < 7:
            f.write("### Critical Improvements Needed\n\n")
            f.write("1. **Response Quality:** Average score below 7/10 indicates significant issues\n")
            f.write("2. **Review Agent Logic:** Check routing and response generation\n")
            f.write("3. **Improve Context:** Ensure agents have access to relevant data\n\n")
        
        if data_usage_pct < 80:
            f.write("### Data Utilization\n\n")
            f.write(f"- Current data usage: {data_usage_pct:.1f}%\n")
            f.write("- **Action:** Ensure agents query and reference actual patient data\n")
            f.write("- **Target:** >90% data usage rate\n\n")
        
        # Agent-specific recommendations
        for agent, agent_results in by_agent.items():
            avg_score = sum(r['overall_score'] for r in agent_results) / len(agent_results)
            if avg_score < 7:
                f.write(f"### {agent.capitalize()} Agent\n\n")
                f.write(f"- Score: {avg_score:.2f}/10 (below target)\n")
                f.write(f"- **Action:** Review and improve {agent} agent logic\n\n")
        
        f.write("---\n\n")
        f.write("*End of Report*\n")
    
    print(f"✓ Report saved to: {output_file}")
    return output_file


def generate_csv_summary(evaluated_results, output_file="evaluation_summary.csv"):
    """Generate CSV summary for spreadsheet analysis"""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'data_type', 'complexity', 'prompt', 'agent_used', 'expected_agent',
            'relevance_score', 'context_score', 'completeness_score', 'overall_score',
            'uses_data', 'execution_time_ms', 'success'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for r in evaluated_results:
            writer.writerow({
                'data_type': r.get('data_type', ''),
                'complexity': r.get('complexity', ''),
                'prompt': r.get('prompt', ''),
                'agent_used': r.get('agent_used', ''),
                'expected_agent': r.get('expected_agent', ''),
                'relevance_score': r.get('relevance_score', 0),
                'context_score': r.get('context_score', 0),
                'completeness_score': r.get('completeness_score', 0),
                'overall_score': r.get('overall_score', 0),
                'uses_data': r.get('uses_data', False),
                'execution_time_ms': r.get('execution_time_ms', 0),
                'success': r.get('success', False)
            })
    
    print(f"✓ CSV summary saved to: {output_file}")
    return output_file


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python evaluation_report.py <evaluated_results.json>")
        sys.exit(1)
    
    results_file = sys.argv[1]
    
    # Load evaluated results
    with open(results_file, 'r', encoding='utf-8') as f:
        evaluated_results = json.load(f)
    
    # Generate reports
    generate_report(evaluated_results, "evaluation_report.md")
    generate_csv_summary(evaluated_results, "evaluation_summary.csv")
    
    print("\n✓ All reports generated successfully")
