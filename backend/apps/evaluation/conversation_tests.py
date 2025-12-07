import json
import uuid
from typing import List, Dict
import requests


BACKEND = 'http://localhost:8000'
API_KEY = 'dev-secret-key'


def run_session(user_id: str, prompts: List[str]) -> List[Dict]:
    conv_id = str(uuid.uuid4())
    results = []
    for p in prompts:
        payload = {'query': p, 'user_id': user_id, 'conversation_id': conv_id}
        r = requests.post(f'{BACKEND}/api/agents/v2/analyze', data=json.dumps(payload), headers={'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'})
        r.raise_for_status()
        results.append(r.json())
    return results


def patient_script() -> List[str]:
    return [
        '¿Cuál fue mi último valor de glucosa?',
        '¿Cómo evolucionó en los últimos 90 días?',
        'Compáralo con mi colesterol LDL.',
        '¿Hay correlación entre mi peso y la glucosa?',
        '¿Puedes resumir mis mejores y peores semanas recientes?',
        '¿Qué hábitos de sueño podrían estar influyendo?'
    ]


def doctor_script() -> List[str]:
    return [
        'Resumen ejecutivo 12 meses con hitos terapéuticos.',
        'Correlaciones relevantes entre glucosa, peso y PA.',
        'Respuesta tras iniciar metformina.',
        'Cita documentos relevantes de laboratorio.'
    ]


def main():
    user_id = 'demo-alex'
    pat_res = run_session(user_id, patient_script())
    doc_res = run_session(user_id, doctor_script())
    print('Paciente:')
    for i, r in enumerate(pat_res):
        print(i + 1, r.get('final_text', '')[:160].replace('\n', ' '))
    print('\nMédico:')
    for i, r in enumerate(doc_res):
        print(i + 1, r.get('final_text', '')[:160].replace('\n', ' '))


if __name__ == '__main__':
    main()


