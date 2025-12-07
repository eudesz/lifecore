"""
Relevance Evaluator
Uses LLM (GPT-4) to evaluate response relevance and context appropriateness
"""
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EVALUATION_PROMPT_TEMPLATE = """You are evaluating a medical chatbot response for relevance and context appropriateness.

**Question:** {prompt}

**Response:** {response}

**References Used:** {references_count} documents

**Criteria to Evaluate:**
1. **Relevance (0-10)**: Does the response directly address the question asked?
2. **Context (0-10)**: Is the response contextually appropriate and coherent?
3. **Completeness (0-10)**: Does the answer provide sufficient information?
4. **Data Usage**: Does the response reference actual patient data (numbers, dates, trends)?

**Scoring Guide:**
- 9-10: Excellent - Perfect relevance and context
- 7-8: Good - Minor issues but generally appropriate
- 5-6: Fair - Some relevance but missing key points
- 3-4: Poor - Partially relevant or off-topic
- 0-2: Very Poor - Irrelevant or incoherent

Respond ONLY with valid JSON in this exact format:
{{
  "relevance_score": <number 0-10>,
  "context_score": <number 0-10>,
  "completeness_score": <number 0-10>,
  "uses_data": <true or false>,
  "overall_score": <average of the three scores>,
  "explanation": "<brief 1-2 sentence explanation>",
  "strengths": ["<strength1>", "<strength2>"],
  "weaknesses": ["<weakness1>"] or []
}}"""


def evaluate_relevance(prompt, response, references):
    """
    Evaluate response relevance using GPT-4
    
    Args:
        prompt: The user's question
        response: The chatbot's response
        references: List of references used
        
    Returns:
        Dictionary with evaluation scores and feedback
    """
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    evaluation_prompt = EVALUATION_PROMPT_TEMPLATE.format(
        prompt=prompt,
        response=response[:1000],  # Limit response length
        references_count=len(references) if references else 0
    )
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "You are an expert evaluator of medical chatbot responses. Provide objective, detailed assessments."
            }, {
                "role": "user",
                "content": evaluation_prompt
            }],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        evaluation = json.loads(completion.choices[0].message.content)
        
        # Ensure all required fields are present
        required_fields = [
            "relevance_score", "context_score", "completeness_score",
            "uses_data", "overall_score", "explanation", "strengths", "weaknesses"
        ]
        
        for field in required_fields:
            if field not in evaluation:
                if field.endswith("_score") or field == "overall_score":
                    evaluation[field] = 0
                elif field == "uses_data":
                    evaluation[field] = False
                elif field in ["strengths", "weaknesses"]:
                    evaluation[field] = []
                else:
                    evaluation[field] = "N/A"
        
        return evaluation
        
    except Exception as e:
        print(f"  ✗ Evaluation error: {str(e)}")
        return {
            "relevance_score": 0,
            "context_score": 0,
            "completeness_score": 0,
            "uses_data": False,
            "overall_score": 0,
            "explanation": f"Evaluation failed: {str(e)}",
            "strengths": [],
            "weaknesses": ["Evaluation error"]
        }


def evaluate_batch(results):
    """
    Evaluate a batch of results
    
    Args:
        results: List of result dictionaries
        
    Returns:
        List of results with evaluation data added
    """
    evaluated_results = []
    total = len(results)
    
    print(f"\n=== Evaluating {total} responses ===\n")
    
    for i, result in enumerate(results, 1):
        if not result.get('success', False):
            print(f"[{i}/{total}] Skipping failed prompt")
            evaluation = {
                "relevance_score": 0,
                "context_score": 0,
                "completeness_score": 0,
                "uses_data": False,
                "overall_score": 0,
                "explanation": "Prompt execution failed",
                "strengths": [],
                "weaknesses": ["Execution error"]
            }
        else:
            print(f"[{i}/{total}] Evaluating: {result['data_type']} ({result['complexity']})")
            evaluation = evaluate_relevance(
                result['prompt'],
                result['response'],
                result['references']
            )
            print(f"  Score: {evaluation['overall_score']:.1f}/10 | Data: {evaluation['uses_data']}")
        
        # Merge evaluation into result
        evaluated_result = {**result, **evaluation}
        evaluated_results.append(evaluated_result)
    
    print("\n✓ Evaluation complete\n")
    return evaluated_results


def print_evaluation_summary(evaluated_results):
    """Print summary of evaluation scores"""
    print("\n" + "="*60)
    print("EVALUATION SCORES SUMMARY")
    print("="*60)
    
    successful = [r for r in evaluated_results if r.get('success', False)]
    
    if not successful:
        print("\nNo successful results to evaluate")
        return
    
    # Overall averages
    avg_relevance = sum(r['relevance_score'] for r in successful) / len(successful)
    avg_context = sum(r['context_score'] for r in successful) / len(successful)
    avg_completeness = sum(r['completeness_score'] for r in successful) / len(successful)
    avg_overall = sum(r['overall_score'] for r in successful) / len(successful)
    data_usage = sum(1 for r in successful if r['uses_data']) / len(successful) * 100
    
    print(f"\n📊 Overall Scores (avg):")
    print(f"  Relevance:    {avg_relevance:.2f}/10")
    print(f"  Context:      {avg_context:.2f}/10")
    print(f"  Completeness: {avg_completeness:.2f}/10")
    print(f"  Overall:      {avg_overall:.2f}/10")
    print(f"  Data Usage:   {data_usage:.1f}%")
    
    # Score distribution
    print(f"\n📈 Score Distribution:")
    excellent = sum(1 for r in successful if r['overall_score'] >= 9)
    good = sum(1 for r in successful if 7 <= r['overall_score'] < 9)
    fair = sum(1 for r in successful if 5 <= r['overall_score'] < 7)
    poor = sum(1 for r in successful if r['overall_score'] < 5)
    
    print(f"  Excellent (9-10): {excellent} ({excellent/len(successful)*100:.1f}%)")
    print(f"  Good (7-8):       {good} ({good/len(successful)*100:.1f}%)")
    print(f"  Fair (5-6):       {fair} ({fair/len(successful)*100:.1f}%)")
    print(f"  Poor (0-4):       {poor} ({poor/len(successful)*100:.1f}%)")
    
    # By data type
    print(f"\n📋 By Data Type:")
    by_type = {}
    for r in successful:
        if r['data_type'] not in by_type:
            by_type[r['data_type']] = []
        by_type[r['data_type']].append(r)
    
    for data_type, type_results in sorted(by_type.items()):
        avg_score = sum(r['overall_score'] for r in type_results) / len(type_results)
        print(f"  {data_type}: {avg_score:.2f}/10")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python relevance_evaluator.py <results_file.json>")
        sys.exit(1)
    
    results_file = sys.argv[1]
    
    # Load results
    with open(results_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # Evaluate
    evaluated_results = evaluate_batch(results)
    
    # Save evaluated results
    output_file = results_file.replace('.json', '_evaluated.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(evaluated_results, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Evaluated results saved to: {output_file}")
    
    # Print summary
    print_evaluation_summary(evaluated_results)
