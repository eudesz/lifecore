import json
import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any

class TimeSeriesGenerator:
    def __init__(self, start_date: datetime, end_date: datetime):
        self.start_date = start_date
        self.end_date = end_date
        self.days = (end_date - start_date).days

    def generate_linear_trend(self, start_val: float, end_val: float, noise_std: float = 1.0) -> List[Dict[str, Any]]:
        """Generates a daily time series with a linear trend + noise."""
        values = np.linspace(start_val, end_val, self.days)
        noise = np.random.normal(0, noise_std, self.days)
        series = values + noise
        
        data = []
        for i, val in enumerate(series):
            date = self.start_date + timedelta(days=i)
            data.append({
                'date': date.isoformat(),
                'value': round(float(val), 2),
                'timestamp': date.timestamp()
            })
        return data

    def generate_seasonal_trend(self, base_val: float, amplitude: float, period_days: int = 365, noise_std: float = 1.0) -> List[Dict[str, Any]]:
        """Generates a daily time series with seasonality."""
        x = np.arange(self.days)
        seasonality = amplitude * np.sin(2 * np.pi * x / period_days)
        noise = np.random.normal(0, noise_std, self.days)
        series = base_val + seasonality + noise
        
        data = []
        for i, val in enumerate(series):
            date = self.start_date + timedelta(days=i)
            data.append({
                'date': date.isoformat(),
                'value': round(float(val), 2),
                'timestamp': date.timestamp()
            })
        return data

    def generate_biometrics(self) -> Dict[str, List[Dict[str, Any]]]:
        # Phase 1: 1975-2005 (0-30 years) - Healthy
        # Phase 2: 2005-2015 (30-40 years) - Pre-condition (Weight gain, BP rise)
        # Phase 3: 2015-2025 (40-50 years) - Condition (Diabetes T2, Hypert)
        
        # We'll approximate this by constructing piece-wise trends or just a full 50-year curve 
        # But per the plan, we mostly need detailed data for later years, but let's do full range broadly.
        
        # Weight: 
        # 0-20y: Growth (3kg -> 75kg)
        # 20-30y: Stable (75kg -> 78kg)
        # 30-45y: Gain (78kg -> 95kg)
        # 45-50y: Managed/Stable (95kg -> 92kg)
        
        # Let's simplify and generate daily data for the whole period but maybe sample it later for observations
        
        # To make it realistic efficiently, let's focus on the generation logic
        
        results = {}
        
        # WEARABLES (Steps) - Higher in youth, sedentary middle age, improvement after diagnosis
        # 1990-2005 (15-30y): Active (8000-12000 steps)
        # 2005-2017 (30-42y): Sedentary (4000-6000 steps)
        # 2017-2025 (42-50y): Improvement attempts (6000-8000 steps)
        
        steps_data = []
        current_date = self.start_date
        while current_date <= self.end_date:
            year = current_date.year
            age = year - 1975
            
            if age < 15:
                 base = 10000 # Kids move a lot
            elif 15 <= age < 30:
                base = 9000
            elif 30 <= age < 42:
                base = 4500 # Sedentary office job
            else:
                base = 6500 # Trying to walk more
            
            val = max(0, int(np.random.normal(base, 1500)))
            steps_data.append({
                'date': current_date.isoformat(),
                'value': val
            })
            current_date += timedelta(days=1)
            
        results['steps'] = steps_data

        # GLUCOSE (Fasting) - Generated as episodic measurements usually, but here maybe daily trend
        # We will generate a trend line to sample from for Lab reports
        # 0-35y: Normal (85-95)
        # 35-42y: Pre-diabetic rising (95 -> 125)
        # 42y+: Diabetic (125 -> 160 without meds, but controlled -> 110-130)
        
        return results

    def generate_vitals_history(self):
        """Generates detailed vitals for the whole life"""
        data = {
            'weight': [],
            'glucose': [],
            'systolic_bp': [],
            'diastolic_bp': []
        }
        
        curr = self.start_date
        while curr <= self.end_date:
            age = curr.year - 1975
            noise = random.uniform(-1, 1)
            
            # WEIGHT
            if age < 20:
                w = 3 + (72/20) * age # Linear growth roughly
            elif 20 <= age < 30:
                w = 75 + (age-20)*0.3 # Slow gain
            elif 30 <= age < 45:
                w = 78 + (age-30)*1.2 # Faster gain
            else:
                w = 96 - (age-45)*0.5 # Losing some weight due to meds/diet
            
            data['weight'].append({
                'date': curr.isoformat(),
                'value': round(w + noise, 1),
                'unit': 'kg'
            })
            
            # GLUCOSE (Fasting trend)
            if age < 35:
                g = 85
            elif 35 <= age < 42:
                g = 85 + (age-35)*5 # 85 -> 120
            else:
                # Controlled with volatility
                g = 120 + random.uniform(-15, 30)
            
            data['glucose'].append({
                'date': curr.isoformat(),
                'value': round(g + noise*2, 0),
                'unit': 'mg/dl'
            })
            
            # BP
            if age < 30:
                s, d = 110, 70
            elif 30 <= age < 40:
                s = 110 + (age-30)*2 # -> 130
                d = 70 + (age-30)*1.5 # -> 85
            else:
                s = 135 + random.uniform(-5, 15)
                d = 85 + random.uniform(-5, 10)
                
            data['systolic_bp'].append({'date': curr.isoformat(), 'value': int(s), 'unit': 'mmHg'})
            data['diastolic_bp'].append({'date': curr.isoformat(), 'value': int(d), 'unit': 'mmHg'})

            curr += timedelta(days=7) # Weekly resolution for vitals is enough for history
            
        return data

if __name__ == "__main__":
    gen = TimeSeriesGenerator(datetime(1975, 1, 1), datetime(2025, 12, 31))
    vitals = gen.generate_vitals_history()
    steps = gen.generate_biometrics()
    
    # Save to JSON
    with open('sample_data/full_history/biometrics/vitals.json', 'w') as f:
        json.dump(vitals, f, indent=2)
        
    with open('sample_data/full_history/biometrics/wearables.json', 'w') as f:
        json.dump(steps, f, indent=2)

