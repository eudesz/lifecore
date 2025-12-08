import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from django.db.models import Q, Avg, Max, Min, Count
from django.db.models.functions import TruncMonth, TruncYear
from apps.lifecore.models import Observation, TimelineEvent, Document
from apps.lifecore.treatment_models import Treatment
from apps.lifecore.vectorstore_faiss import FaissVectorStore
import math
from apps.lifecore.graph_db import GraphDB

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

# --- PHASE 1 ADVANCED TOOLS ---

def analyze_lab_panels(user_id: int, panel_type: str = 'general') -> str:
    """
    Analyzes latest lab results against standard reference ranges.
    Detects anomalies (High/Low).
    """
    try:
        # Standard ranges (simplified for demo) + extended markers for complex SLE cases
        RANGES = {
            'glucose': {'min': 70, 'max': 100, 'unit': 'mg/dL'},
            'hba1c': {'min': 4.0, 'max': 5.7, 'unit': '%'},
            'cholesterol_total': {'min': 0, 'max': 200, 'unit': 'mg/dL'},
            'cholesterol_ldl': {'min': 0, 'max': 100, 'unit': 'mg/dL'},
            'cholesterol_hdl': {'min': 40, 'max': 100, 'unit': 'mg/dL'},
            'triglycerides': {'min': 0, 'max': 150, 'unit': 'mg/dL'},
            'hemoglobin': {'min': 13.5, 'max': 17.5, 'unit': 'g/dL'},
            'systolic_bp': {'min': 90, 'max': 120, 'unit': 'mmHg'},
            'diastolic_bp': {'min': 60, 'max': 80, 'unit': 'mmHg'},
            # Extended: key labs for Laura SLE case
            'lipase': {'min': 0, 'max': 160, 'unit': 'U/L'},
            'amylase': {'min': 0, 'max': 110, 'unit': 'U/L'},
            'proteinuria_24h': {'min': 0, 'max': 0.3, 'unit': 'g/24h'},
        }
        
        report = {'panel': panel_type, 'results': []}
        
        # Codes to check based on panel
        target_codes = list(RANGES.keys())
        if panel_type == 'lipid':
            target_codes = [k for k in target_codes if 'cholesterol' in k or 'triglycerides' in k]
        elif panel_type == 'metabolic':
            target_codes = ['glucose', 'hba1c', 'cholesterol_total']
        elif panel_type == 'sle_flare':
            # Custom panel to highlight lupus flare with pancreatitis + nephritis markers
            target_codes = ['lipase', 'amylase', 'proteinuria_24h']
            
        for code in target_codes:
            obs = Observation.objects.filter(user_id=user_id, code=code).order_by('-taken_at').first()
            if obs:
                ref = RANGES.get(code)
                val = float(obs.value)
                status = 'Normal'
                if val < ref['min']: status = 'Low'
                if val > ref['max']: status = 'High'
                
                report['results'].append({
                    'test': code,
                    'value': val,
                    'unit': obs.unit,
                    'date': obs.taken_at.date().isoformat(),
                    'status': status,
                    'reference_range': f"{ref['min']}-{ref['max']}"
                })
        
        if not report['results']:
            return "No recent lab results found for this panel."
            
        return json.dumps(report, default=str)
    except Exception as e:
        return f"Error analyzing labs: {str(e)}"

def calculate_risk_scores(user_id: int, risk_model: str) -> str:
    """
    Calculates simplified clinical risk scores (Framingham, FINDRISC).
    """
    try:
        risk_model = risk_model.lower()
        
        # Common data needed
        age = 45 # Default/Placeholder if DOB missing. In real app, fetch from User profile.
        # Attempt to find DOB from events? (Assuming ~1975 birth from previous context)
        birth_event = TimelineEvent.objects.filter(user_id=user_id, kind='medical_history', payload__description__icontains='Nacimiento').first()
        if birth_event:
            age = (datetime.now().date() - birth_event.occurred_at.date()).days // 365
            
        bmi_raw = calculate_health_score(user_id, 'bmi')
        bmi = 25  # default
        try:
            # calculate_health_score returns JSON string on success or plain text on error
            if isinstance(bmi_raw, str) and bmi_raw.strip().startswith('{'):
                bmi_data = json.loads(bmi_raw)
                if isinstance(bmi_data, dict):
                    bmi = bmi_data.get('value', 25)
        except Exception:
            # Fallback to default BMI if parsing fails
            bmi = 25
        
        if 'cardio' in risk_model or 'framingham' in risk_model:
            # Simplified 10-year Risk Logic (Non-clinical valid, just for demo structure)
            # Factors: Age, Gender (Male), Smoker (No), Diabetic (Yes/No), BP, Chol
            
            # Fetch BP & Chol
            sbp_obs = Observation.objects.filter(user_id=user_id, code='systolic_bp').order_by('-taken_at').first()
            sbp = float(sbp_obs.value) if sbp_obs else 120
            
            chol_obs = Observation.objects.filter(user_id=user_id, code='cholesterol_total').order_by('-taken_at').first()
            chol = float(chol_obs.value) if chol_obs else 180
            
            # Base points
            points = 0
            if age > 40: points += 2
            if chol > 200: points += 2
            if sbp > 130: points += 2
            if bmi > 30: points += 1
            
            # Check diabetes history
            is_diabetic = TimelineEvent.objects.filter(user_id=user_id, related_conditions__contains='diabetes').exists()
            if is_diabetic: points += 4
            
            risk_pct = min(30, points * 2) # Dummy calc
            level = "Low"
            if risk_pct >= 10: level = "Moderate"
            if risk_pct >= 20: level = "High"
            
            return json.dumps({
                "model": "Framingham (Simplified)",
                "risk_score_10y": f"{risk_pct}%",
                "risk_level": level,
                "factors": {
                    "age": age,
                    "systolic_bp": sbp,
                    "cholesterol": chol,
                    "diabetes": is_diabetic
                }
            })
            
        elif 'diabetes' in risk_model or 'findrisc' in risk_model:
            # FINDRISC simplified
            score = 0
            if age > 45: score += 2
            if bmi > 25: score += 1
            if bmi > 30: score += 3
            
            # History of high glucose?
            high_gluc = Observation.objects.filter(user_id=user_id, code='glucose', value__gt=100).exists()
            if high_gluc: score += 5
            
            risk_txt = "Low risk"
            if score > 7: risk_txt = "Slightly elevated"
            if score > 12: risk_txt = "Moderate to High"
            if score > 15: risk_txt = "High risk (1 in 3)"
            
            return json.dumps({
                "model": "FINDRISC (Simplified)",
                "score": score,
                "risk_description": risk_txt
            })
            
        return "Risk model not supported."
    except Exception as e:
        return f"Error calculating risk: {str(e)}"

def check_drug_interactions(user_id: int, new_drug: str) -> str:
    """
    Checks potential interactions between current active treatments and a new drug.
    Uses a local knowledge base of common interactions.
    """
    try:
        # 1. Get active treatments
        active_treatments = Treatment.objects.filter(user_id=user_id, status='active').values_list('name', flat=True)
        active_list = list(active_treatments)
        
        if not active_list:
            return f"No active treatments found. '{new_drug}' has no known context interactions."
            
        # 2. Local KB (Simplified)
        # Format: "drug_a": ["incompatible_1", "incompatible_2"]
        INTERACTIONS = {
            "warfarina": ["aspirina", "ibuprofeno", "naproxeno", "ajo"],
            "metformina": ["alcohol", "contrastes yodados"],
            "sildenafil": ["nitratos", "nitroglicerina"],
            "atorvastatina": ["gemfibrozilo", "ciclosporina"],
            "ibuprofeno": ["warfarina", "litio", "metotrexato"],
            "aspirina": ["warfarina", "ibuprofeno"]
        }
        
        alerts = []
        new_drug_clean = new_drug.lower()
        
        for current in active_list:
            current_clean = current.lower()
            
            # Check new vs current
            if current_clean in INTERACTIONS:
                bad_mixes = INTERACTIONS[current_clean]
                for bad in bad_mixes:
                    if bad in new_drug_clean:
                        alerts.append(f"⚠️ MAJOR: {current} + {new_drug} (Risk of bleeding/toxicity)")
            
            # Check current vs new (reverse)
            if new_drug_clean in INTERACTIONS:
                bad_mixes = INTERACTIONS[new_drug_clean]
                for bad in bad_mixes:
                    if bad in current_clean:
                        alerts.append(f"⚠️ MAJOR: {new_drug} + {current}")

        if not alerts:
            return json.dumps({
                "status": "Safe", 
                "message": f"No critical interactions found for {new_drug} with current meds ({', '.join(active_list)})."
            })
            
        return json.dumps({
            "status": "Warning",
            "alerts": list(set(alerts)),
            "current_meds": active_list
        })

    except Exception as e:
        return f"Error checking interactions: {str(e)}"

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

# --- PHASE 2: LIFESTYLE & WEARABLES TOOLS ---

def analyze_sleep_quality(user_id: int, period: str = '7d') -> str:
    """
    Analyzes sleep patterns (hours, quality) over a period.
    """
    try:
        days = 7
        if period == '30d': days = 30
        elif period == '90d': days = 90
        
        start_date = datetime.now() - timedelta(days=days)
        
        qs = Observation.objects.filter(
            user_id=user_id, 
            code__in=['sleep_hours', 'sleep_score', 'rem_sleep'],
            taken_at__gte=start_date
        ).order_by('taken_at')
        
        if not qs.exists():
            return "No sleep data found for this period."
            
        # Agrupar por código
        data = {}
        for obs in qs:
            data.setdefault(obs.code, []).append(obs.value)
            
        report = {"period": f"Last {days} days"}
        
        if 'sleep_hours' in data:
            vals = data['sleep_hours']
            avg = sum(vals) / len(vals)
            report['avg_hours'] = round(avg, 1)
            report['consistency'] = "Good" if (max(vals) - min(vals)) < 2 else "Variable"
            
        if 'sleep_score' in data:
            vals = data['sleep_score']
            report['avg_sleep_score'] = round(sum(vals) / len(vals), 0)
            
        return json.dumps(report)
    except Exception as e:
        return f"Error analyzing sleep: {str(e)}"

def analyze_wearable_metrics(user_id: int) -> str:
    """
    Analyzes advanced wearable metrics like HRV, VO2 Max, Resting Heart Rate.
    """
    try:
        # Fetch latest values for key metrics
        metrics = ['vo2_max', 'hrv', 'resting_hr']
        results = {}
        
        for m in metrics:
            obs = Observation.objects.filter(user_id=user_id, code=m).order_by('-taken_at').first()
            if obs:
                results[m] = {
                    "value": obs.value,
                    "date": obs.taken_at.date().isoformat(),
                    "status": "Normal" # Placeholder for range logic
                }
                
        if not results:
            return "No advanced wearable metrics (HRV, VO2 Max) found."
            
        return json.dumps(results)
    except Exception as e:
        return f"Error analyzing wearables: {str(e)}"

def analyze_nutritional_logs(user_id: int, days: int = 7) -> str:
    """
    Analyzes nutritional information from logs or documents.
    Currently searches for diet-related documents as a proxy.
    """
    try:
        # In a real app, this would query a NutritionLog model.
        # Here we use RAG to find diet summaries.
        docs = search_medical_documents(user_id, "diet nutrition calories food log")
        if "No relevant information" in docs:
            return "No detailed nutritional logs found. Please upload a diet diary."
            
        return f"Nutritional Context found in documents:\n{docs[:500]}..."
    except Exception as e:
        return f"Error analyzing nutrition: {str(e)}"


def graph_explain_relationship(user_id: int, entities: List[str]) -> str:
    """
    Uses Neo4j to explore how a set of clinical concepts (entities) are connected
    around the current patient. Returns a textual explanation of key paths.
    """
    try:
        driver = GraphDB.get_driver()
        if not driver:
            return "Graph engine (Neo4j) is not available."

        # Normalize entities (lowercase, strip)
        clean_entities = [e.strip().lower() for e in entities if e and e.strip()]
        if not clean_entities:
            return "No valid entities provided to explore in the knowledge graph."

        with driver.session() as session:
            # 1. Find candidate nodes matching each entity near the patient
            match_query = """
            MATCH (p:Patient {id: $uid})-[*1..2]-(n)
            WHERE ANY(term IN $terms WHERE
                toLower(coalesce(n.name, '')) CONTAINS term OR
                toLower(coalesce(n.title, '')) CONTAINS term
            )
            RETURN DISTINCT labels(n) AS labels, id(n) AS nid, properties(n) AS props
            LIMIT 50
            """
            candidates = session.run(match_query, uid=user_id, terms=clean_entities)
            nodes = []
            for rec in candidates:
                labels = rec["labels"]
                props = rec["props"]
                label_txt = props.get("name") or props.get("title") or "/".join(labels)
                nodes.append({"labels": labels, "name": label_txt})

            if not nodes:
                return "No graph nodes were found near the patient for the specified entities."

            # 2. Describe high-level connections between all matched nodes
            # (Patient-centric: how many conditions, meds, documents are involved)
            summary = {
                "Condition": 0,
                "Medication": 0,
                "Document": 0,
                "Event": 0,
            }
            for n in nodes:
                lbls = n["labels"]
                if "Condition" in lbls:
                    summary["Condition"] += 1
                if "Medication" in lbls:
                    summary["Medication"] += 1
                if "Document" in lbls:
                    summary["Document"] += 1
                if "Event" in lbls:
                    summary["Event"] += 1

            # 3. Basic textual explanation
            parts = []
            parts.append(
                f"Encontré {len(nodes)} nodos en el grafo relacionados con los términos: "
                + ", ".join(entities)
                + "."
            )
            if summary["Condition"]:
                parts.append(f"- Condiciones implicadas: {summary['Condition']}.")
            if summary["Medication"]:
                parts.append(f"- Medicamentos implicados: {summary['Medication']}.")
            if summary["Document"]:
                parts.append(f"- Documentos clínicos relacionados: {summary['Document']}.")
            if summary["Event"]:
                parts.append(f"- Eventos de la línea de tiempo asociados: {summary['Event']}.")

            # 4. Provide a small sample of node names for context
            sample_names = [n["name"] for n in nodes[:6]]
            if sample_names:
                parts.append("Ejemplos de nodos relevantes en tu grafo:")
                for name in sample_names:
                    parts.append(f"  • {name}")

            return "\n".join(parts)
    except Exception as e:
        return f"Error exploring knowledge graph: {str(e)}"


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
    "analyze_lab_panels": analyze_lab_panels,
    "calculate_risk_scores": calculate_risk_scores,
    "check_drug_interactions": check_drug_interactions,
    # Phase 2
    "analyze_sleep_quality": analyze_sleep_quality,
    "analyze_wearable_metrics": analyze_wearable_metrics,
    "analyze_nutritional_logs": analyze_nutritional_logs,
    "graph_explain_relationship": graph_explain_relationship,
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
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_lab_panels",
            "description": "Analyzes latest lab results (Lipid, Metabolic) against standard ranges and detects anomalies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "panel_type": {"type": "string", "description": "'lipid', 'metabolic', 'general'."}
                },
                "required": ["panel_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_risk_scores",
            "description": "Calculates clinical risk scores like Framingham (Cardio) or FINDRISC (Diabetes).",
            "parameters": {
                "type": "object",
                "properties": {
                    "risk_model": {"type": "string", "description": "'cardio' (Framingham) or 'diabetes' (FINDRISC)."}
                },
                "required": ["risk_model"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_drug_interactions",
            "description": "Checks for potential interactions between current meds and a new drug.",
            "parameters": {
                "type": "object",
                "properties": {
                    "new_drug": {"type": "string", "description": "Name of the new drug to check."}
                },
                "required": ["new_drug"]
            }
        }
    },
    # Phase 2 Tools
    {
        "type": "function",
        "function": {
            "name": "analyze_sleep_quality",
            "description": "Analyzes sleep patterns and quality over a period.",
            "parameters": {
                "type": "object",
                "properties": {
                    "period": {"type": "string", "description": "'7d', '30d', '90d'."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_wearable_metrics",
            "description": "Analyzes advanced metrics like HRV, VO2 Max from wearables.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_nutritional_logs",
            "description": "Analyzes nutritional habits from logs or documents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "Number of days to analyze."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "graph_explain_relationship",
            "description": "Explains how a set of entities (diagnoses, symptoms, labs, meds) are connected in the patient-specific knowledge graph (Neo4j).",
            "parameters": {
                "type": "object",
                "properties": {
                    "entities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of key concepts to relate, e.g. ['lupus', 'pancreatitis', 'proteinuria', 'trombosis']."
                    }
                },
                "required": ["entities"]
            }
        }
    }
]
