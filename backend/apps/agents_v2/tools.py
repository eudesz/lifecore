import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from django.db.models import Q, Avg, Max, Min, Count
from django.db.models.functions import TruncMonth, TruncYear
from apps.lifecore.models import Observation, TimelineEvent, Document
from apps.lifecore.treatment_models import Treatment
from apps.lifecore.vectorstore_faiss import FaissVectorStore
import math

# --- EXISTING TOOLS ---

def get_biometric_data(user_id: int, metric: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
    """
    Retrieves biometric data (weight, glucose, bp, steps) for a given date range.
    Useful for trends, charts, averages, min/max analysis.
    """
    try:
        qs = Observation.objects.filter(user_id=user_id)
        
        # Metric mapping
        if metric.lower() in ['weight', 'peso']:
            qs = qs.filter(code='weight')
        elif metric.lower() in ['glucose', 'glucosa', 'sugar']:
            qs = qs.filter(code='glucose')
        elif metric.lower() in ['bp', 'blood pressure', 'presion', 'presion arterial']:
            qs = qs.filter(code__in=['systolic_bp', 'diastolic_bp'])
        elif metric.lower() in ['steps', 'pasos', 'caminata']:
            qs = qs.filter(code='steps')
        else:
            qs = qs.filter(code__icontains=metric)

        if start_date:
            qs = qs.filter(taken_at__gte=start_date)
        if end_date:
            qs = qs.filter(taken_at__lte=end_date)

        data = list(qs.order_by('taken_at').values('taken_at', 'code', 'value', 'unit'))
        
        if not data:
            return "No biometric data found for the specified criteria."

        if len(data) > 100:
            step = len(data) // 100
            data = data[::step]

        return json.dumps(data, default=str)
    except Exception as e:
        return f"Error retrieving biometrics: {str(e)}"

def get_clinical_events(user_id: int, category: Optional[str] = None) -> str:
    """
    Retrieves clinical timeline events like diagnoses, treatments, surgeries.
    Useful for correlating dates of medical history.
    """
    try:
        qs = TimelineEvent.objects.filter(user_id=user_id)
        
        if category:
            if 'medic' in category.lower() or 'trat' in category.lower() or 'drug' in category.lower():
                qs = qs.filter(kind__in=['treatment_start', 'treatment_end', 'medication'])
            elif 'diag' in category.lower():
                qs = qs.filter(kind='diagnosis')
            elif 'surg' in category.lower() or 'ciru' in category.lower() or 'oper' in category.lower():
                qs = qs.filter(category='procedure')
        
        events = list(qs.order_by('occurred_at').values('occurred_at', 'kind', 'category', 'payload', 'data_summary'))
        
        if not events:
            return "No clinical events found."
            
        return json.dumps(events, default=str)
    except Exception as e:
        return f"Error retrieving events: {str(e)}"

def search_medical_documents(user_id: int, query: str, year: Optional[int] = None) -> str:
    """
    Performs semantic search on medical documents (notes, reports, PDFs).
    Useful for finding qualitative details, doctor opinions, symptoms descriptions.
    """
    try:
        store = FaissVectorStore(user_id=user_id)
        results = store.search(query, top_k=5)
        
        if not results:
            return "No relevant information found in documents."
            
        formatted_results = []
        for res in results:
            content = res.get('snippet', '')
            source = res.get('source', 'Unknown')
            title = res.get('title', 'Untitled')
            formatted_results.append(f"Document: {title}\nSource: {source}\nContent: {content}")
            
        return "\n---\n".join(formatted_results)
    except Exception as e:
        return f"Error searching documents: {str(e)}"

def get_medical_summary_data(user_id: int, time_range: str = '1y', category: Optional[str] = None, condition: Optional[str] = None) -> str:
    """
    Aggregates a comprehensive summary of medical data for a specific range or condition.
    Ideal for broad questions like "Resumen de los últimos 5 años" or "Historia de mi diabetes".
    """
    try:
        summary = {}
        now = datetime.now()
        start_date = None
        
        if time_range == '1y':
            start_date = now - timedelta(days=365)
        elif time_range == '2y':
            start_date = now - timedelta(days=365*2)
        elif time_range == '3y':
            start_date = now - timedelta(days=365*3)
        elif time_range == '5y':
            start_date = now - timedelta(days=365*5)
        elif time_range.isdigit() and len(time_range) == 4: 
            year = int(time_range)
            start_date = datetime(year, 1, 1)
        
        events_qs = TimelineEvent.objects.filter(user_id=user_id)
        if start_date:
            events_qs = events_qs.filter(occurred_at__gte=start_date)
        
        if category:
            if 'consult' in category.lower():
                events_qs = events_qs.filter(category='consultation')
            elif 'lab' in category.lower():
                events_qs = events_qs.filter(category='lab')
            elif 'treat' in category.lower():
                events_qs = events_qs.filter(category='treatment')
        
        if condition:
            events_qs = events_qs.filter(Q(payload__icontains=condition) | Q(kind__icontains=condition))

        summary['events_count'] = events_qs.count()
        summary['key_events'] = list(events_qs.order_by('-occurred_at')[:15].values('occurred_at', 'kind', 'payload'))

        obs_qs = Observation.objects.filter(user_id=user_id)
        if start_date:
            obs_qs = obs_qs.filter(taken_at__gte=start_date)
        
        stats = {}
        for code in ['glucose', 'weight', 'systolic_bp']:
            agg = obs_qs.filter(code=code).aggregate(
                avg=Avg('value'), 
                min=Min('value'), 
                max=Max('value')
            )
            if agg['avg']:
                stats[code] = {k: round(v, 1) for k, v in agg.items()}
        
        summary['vitals_summary'] = stats

        if not category or 'treat' in category:
            treatments = Treatment.objects.filter(user_id=user_id)
            if start_date:
                treatments = treatments.filter(start_date__gte=start_date)
            summary['treatments'] = list(treatments.values('name', 'status', 'start_date'))

        return json.dumps(summary, default=str)

    except Exception as e:
        return f"Error generating summary: {str(e)}"

# --- NEW ADVANCED TOOLS ---

def compare_health_periods(user_id: int, metric: str, year1: int, year2: int) -> str:
    """
    Compares a health metric between two specific years (e.g., weight in 2020 vs 2024).
    Returns averages and percentage change.
    """
    try:
        def get_avg(year):
            start = datetime(year, 1, 1)
            end = datetime(year, 12, 31, 23, 59, 59)
            qs = Observation.objects.filter(user_id=user_id, taken_at__range=(start, end))
            if metric == 'weight': qs = qs.filter(code='weight')
            elif metric == 'glucose': qs = qs.filter(code='glucose')
            elif 'pressure' in metric or 'bp' in metric: qs = qs.filter(code='systolic_bp')
            
            return qs.aggregate(Avg('value'))['value__avg']

        avg1 = get_avg(year1)
        avg2 = get_avg(year2)

        if avg1 is None or avg2 is None:
            return f"Insufficient data for comparison. {year1}: {avg1}, {year2}: {avg2}"

        diff = avg2 - avg1
        pct = (diff / avg1) * 100
        trend = "increased" if diff > 0 else "decreased"

        return json.dumps({
            "metric": metric,
            f"average_{year1}": round(avg1, 2),
            f"average_{year2}": round(avg2, 2),
            "absolute_change": round(diff, 2),
            "percent_change": round(pct, 1),
            "trend": trend
        })
    except Exception as e:
        return f"Error comparing periods: {str(e)}"

def analyze_correlation(user_id: int, metric_a: str, metric_b: str) -> str:
    """
    Analyzes potential correlation between two metrics (e.g. 'steps' and 'weight') over the last year.
    Uses monthly aggregations to find patterns.
    """
    try:
        start_date = datetime.now() - timedelta(days=365)
        
        def get_monthly_data(code_slug):
            qs = Observation.objects.filter(
                user_id=user_id, 
                taken_at__gte=start_date,
                code__icontains=code_slug
            ).annotate(month=TruncMonth('taken_at')).values('month').annotate(avg=Avg('value')).order_by('month')
            return {entry['month'].strftime('%Y-%m'): entry['avg'] for entry in qs}

        data_a = get_monthly_data(metric_a)
        data_b = get_monthly_data(metric_b)
        
        common_months = sorted(list(set(data_a.keys()) & set(data_b.keys())))
        
        if len(common_months) < 3:
            return "Not enough overlapping data points to calculate correlation."

        # Simple trend description
        series_a = [data_a[m] for m in common_months]
        series_b = [data_b[m] for m in common_months]
        
        # Naive correlation direction check
        trend_a = series_a[-1] - series_a[0]
        trend_b = series_b[-1] - series_b[0]
        
        relationship = "divergent"
        if (trend_a > 0 and trend_b > 0) or (trend_a < 0 and trend_b < 0):
            relationship = "parallel"
            
        return json.dumps({
            "analysis_period": "Last 12 months",
            "data_points": len(common_months),
            "metric_a_trend": "up" if trend_a > 0 else "down",
            "metric_b_trend": "up" if trend_b > 0 else "down",
            "observed_relationship": relationship,
            "details": "Correlation is based on monthly averages."
        })
    except Exception as e:
        return f"Error analyzing correlation: {str(e)}"

def analyze_treatment_impact(user_id: int, treatment_query: str, target_metric: str) -> str:
    """
    Analyzes how a metric changed before and after starting a specific treatment.
    """
    try:
        # 1. Find treatment start date
        treatment = Treatment.objects.filter(user_id=user_id, name__icontains=treatment_query).order_by('start_date').first()
        if not treatment:
            return f"Treatment '{treatment_query}' not found."
            
        start_date = treatment.start_date
        # Make naive datetime timezone aware if needed, assuming UTC for simplicity here
        if start_date.tzinfo is None:
            # In real app, use django.utils.timezone
            pass

        # 2. Get avg metric 3 months BEFORE
        before_start = start_date - timedelta(days=90)
        qs_before = Observation.objects.filter(
            user_id=user_id, 
            code__icontains=target_metric,
            taken_at__range=(before_start, start_date)
        ).aggregate(Avg('value'))
        
        # 3. Get avg metric 3 months AFTER
        after_end = start_date + timedelta(days=90)
        qs_after = Observation.objects.filter(
            user_id=user_id, 
            code__icontains=target_metric,
            taken_at__range=(start_date, after_end)
        ).aggregate(Avg('value'))
        
        val_before = qs_before.get('value__avg')
        val_after = qs_after.get('value__avg')
        
        if val_before is None or val_after is None:
            return f"Insufficient biometric data around the treatment start date ({start_date.date()})."
            
        diff = val_after - val_before
        
        return json.dumps({
            "treatment": treatment.name,
            "start_date": str(start_date.date()),
            "metric": target_metric,
            "avg_3_months_before": round(val_before, 2),
            "avg_3_months_after": round(val_after, 2),
            "change": round(diff, 2),
            "conclusion": "Improved" if (target_metric in ['glucose','weight','bp'] and diff < 0) else "Changed"
        })
    except Exception as e:
        return f"Error analyzing impact: {str(e)}"

def calculate_health_score(user_id: int, score_type: str) -> str:
    """
    Calculates health scores like BMI or simplified cardiovascular risk.
    """
    try:
        if score_type.lower() == 'bmi':
            weight = Observation.objects.filter(user_id=user_id, code='weight').order_by('-taken_at').first()
            height = Observation.objects.filter(user_id=user_id, code='height').order_by('-taken_at').first()
            
            if not weight or not height:
                return "Need recent weight and height data."
                
            h_m = float(height.value) / 100 if float(height.value) > 3 else float(height.value) # normalize cm to m
            w_kg = float(weight.value)
            bmi = w_kg / (h_m * h_m)
            
            category = "Normal"
            if bmi >= 25: category = "Overweight"
            if bmi >= 30: category = "Obese"
            
            return json.dumps({"score": "BMI", "value": round(bmi, 1), "category": category})
            
        return "Score type not supported yet."
    except Exception as e:
        return f"Error calculating score: {str(e)}"

# Registry of tools for OpenAI
AVAILABLE_TOOLS = {
    "get_biometric_data": get_biometric_data,
    "get_clinical_events": get_clinical_events,
    "search_medical_documents": search_medical_documents,
    "get_medical_summary_data": get_medical_summary_data,
    "compare_health_periods": compare_health_periods,
    "analyze_correlation": analyze_correlation,
    "analyze_treatment_impact": analyze_treatment_impact,
    "calculate_health_score": calculate_health_score,
}

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_biometric_data",
            "description": "Get structured biometric data (vital signs, lab values) for a specific metric over a time range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric": {"type": "string", "description": "Metric name (e.g., 'weight', 'glucose', 'bp')."},
                    "start_date": {"type": "string", "description": "YYYY-MM-DD format."},
                    "end_date": {"type": "string", "description": "YYYY-MM-DD format."}
                },
                "required": ["metric"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_clinical_events",
            "description": "Get historical clinical events (diagnoses, surgeries).",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Filter: 'diagnosis', 'surgery', 'treatment'."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_medical_documents",
            "description": "Search unstructured medical notes/reports (RAG). Use for qualitative questions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query."},
                    "year": {"type": "integer", "description": "Optional year filter."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_medical_summary_data",
            "description": "Generates a comprehensive summary of events, vitals, and treatments for a range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "time_range": {"type": "string", "description": "'1y', '5y', 'all' or specific year '2023'."},
                    "category": {"type": "string", "description": "'consultation', 'lab', 'treatment'."},
                    "condition": {"type": "string", "description": "Filter by disease (e.g. 'diabetes')."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_health_periods",
            "description": "Compares a specific metric between two different years (e.g. weight in 2020 vs 2023).",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric": {"type": "string", "description": "The metric code (e.g. 'weight', 'glucose')."},
                    "year1": {"type": "integer", "description": "First year."},
                    "year2": {"type": "integer", "description": "Second year."}
                },
                "required": ["metric", "year1", "year2"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_correlation",
            "description": "Analyzes correlation trends between two metrics (e.g. 'Do my steps affect my weight?').",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric_a": {"type": "string", "description": "First metric."},
                    "metric_b": {"type": "string", "description": "Second metric."}
                },
                "required": ["metric_a", "metric_b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_treatment_impact",
            "description": "Analyzes how a biometric metric changed before and after starting a treatment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "treatment_query": {"type": "string", "description": "Name of medication or treatment."},
                    "target_metric": {"type": "string", "description": "Metric to evaluate (e.g. 'cholesterol')."}
                },
                "required": ["treatment_query", "target_metric"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_health_score",
            "description": "Calculates standard health scores (BMI, etc) from available data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "score_type": {"type": "string", "description": "Type of score: 'bmi'."}
                },
                "required": ["score_type"]
            }
        }
    }
]
