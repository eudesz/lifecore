#!/usr/bin/env python3
"""
Full Evaluation Runner
Orchestrates the complete evaluation process:
1. Load prompts
2. Execute through chat pipeline
3. Evaluate with LLM
4. Generate reports
"""
import os
import sys
from datetime import datetime

# Set up Django environment
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django
django.setup()

# Import after Django setup
from apps.evaluation.prompt_generator import get_all_prompts, print_summary as print_prompt_summary
from apps.evaluation.prompt_evaluation_runner import run_prompt_batch, save_results, save_results_markdown, print_summary as print_run_summary
from apps.evaluation.relevance_evaluator import evaluate_batch, print_evaluation_summary
from apps.evaluation.evaluation_report import generate_report, generate_csv_summary


def main():
    """Main execution flow"""
    print("\n" + "="*70)
    print("LIFECORE PROMPT EVALUATION SYSTEM")
    print("="*70)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Step 1: Load prompts
    print("="*70)
    print("STEP 1: Loading Prompts")
    print("="*70)
    
    prompts = get_all_prompts()
    print(f"\n✓ Loaded {len(prompts)} prompts")
    print_prompt_summary()
    
    # Step 2: Run prompts through chat pipeline
    print("\n" + "="*70)
    print("STEP 2: Executing Prompts through Chat Pipeline")
    print("="*70)
    
    user_id = 5  # demo-alex
    results = run_prompt_batch(user_id, prompts)
    
    # Save raw results
    results_file = "evaluation_results.json"
    save_results(results, results_file)
    save_results_markdown(results, "evaluation_results.md")
    
    # Print execution summary
    print_run_summary(results)
    
    # Step 3: Evaluate with LLM
    print("="*70)
    print("STEP 3: Evaluating Responses with LLM")
    print("="*70)
    
    evaluated_results = evaluate_batch(results)
    
    # Save evaluated results
    evaluated_file = "evaluation_results_evaluated.json"
    import json
    with open(evaluated_file, 'w', encoding='utf-8') as f:
        json.dump(evaluated_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Evaluated results saved to: {evaluated_file}")
    
    # Print evaluation summary
    print_evaluation_summary(evaluated_results)
    
    # Step 4: Generate reports
    print("="*70)
    print("STEP 4: Generating Reports")
    print("="*70 + "\n")
    
    report_file = generate_report(evaluated_results, "evaluation_report.md")
    csv_file = generate_csv_summary(evaluated_results, "evaluation_summary.csv")
    
    # Final summary
    print("\n" + "="*70)
    print("EVALUATION COMPLETE")
    print("="*70)
    
    successful = [r for r in evaluated_results if r.get('success', False)]
    if successful:
        avg_score = sum(r['overall_score'] for r in successful) / len(successful)
        
        print(f"\n📊 Final Results:")
        print(f"   Total Prompts:    {len(evaluated_results)}")
        print(f"   Successful:       {len(successful)}")
        print(f"   Average Score:    {avg_score:.2f}/10")
        print(f"\n📁 Output Files:")
        print(f"   - {results_file}")
        print(f"   - {evaluated_file}")
        print(f"   - {report_file}")
        print(f"   - {csv_file}")
        print(f"   - evaluation_results.md")
        
        # Performance assessment
        print(f"\n🎯 Performance Assessment:")
        if avg_score >= 8:
            print("   ✅ EXCELLENT - System performs very well")
        elif avg_score >= 7:
            print("   ✓ GOOD - System performs well with minor issues")
        elif avg_score >= 5:
            print("   ⚠️ FAIR - System needs improvement")
        else:
            print("   ❌ POOR - System requires significant work")
    else:
        print("\n❌ No successful executions - Critical issues detected")
        print(f"\n📁 Output Files:")
        print(f"   - {results_file}")
        print(f"   - evaluation_results.md")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Evaluation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
