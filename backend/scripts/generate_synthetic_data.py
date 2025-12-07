#!/usr/bin/env python3
import os
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parents[2] / 'sample_data'

PARAMS = {
    'glucose': {'unit': 'mg/dl', 'base': 95, 'var': 20},
    'cholesterol': {'unit': 'mg/dl', 'base': 200, 'var': 40},
    'weight': {'unit': 'kg', 'base': 78, 'var': 5},
    'blood_pressure_systolic': {'unit': 'mmHg', 'base': 130, 'var': 10},
    'blood_pressure_diastolic': {'unit': 'mmHg', 'base': 85, 'var': 6},
}


def rand_series(days: int, base: float, var: float):
    start = datetime.utcnow() - timedelta(days=days)
    out = []
    for i in range(days // 15):
        val = round(random.gauss(base, var), 1)
        out.append({
            'value': val,
            'date': (start + timedelta(days=i * 15)).isoformat()
        })
    return out


def generate_observations():
    obs = {}
    for p, cfg in PARAMS.items():
        obs[p] = rand_series(360, cfg['base'], cfg['var'])
    return obs


def write_observations(user_id: str):
    out_dir = BASE / 'observations'
    out_dir.mkdir(parents=True, exist_ok=True)
    data = {
        'user_id': user_id,
        'observations': generate_observations()
    }
    (out_dir / f'{user_id}_observations.json').write_text(
        json.dumps(data, indent=2)
    )


def write_lab_texts():
    labs_dir = BASE / 'labs'
    labs_dir.mkdir(parents=True, exist_ok=True)
    samples = [
        "Glucosa: 118 mg/dl\nPresión arterial: 135/86 mmHg\nColesterol total: 215 mg/dl\n",
        "Glucosa: 105 mg/dl\nPresión arterial: 128/82 mmHg\nColesterol total: 195 mg/dl\n",
        "Glucosa: 142 mg/dl\nPresión arterial: 138/85 mmHg\nColesterol total: 230 mg/dl\n",
    ]
    for i, txt in enumerate(samples, start=1):
        (labs_dir / f'lab_{i:02d}.txt').write_text(txt)


def main():
    BASE.mkdir(parents=True, exist_ok=True)
    write_observations('demo_user')
    write_lab_texts()
    print(f"Synthetic data written to {BASE}")


if __name__ == '__main__':
    main()
