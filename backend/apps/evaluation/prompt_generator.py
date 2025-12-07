"""
Prompt Generator for LifeCore Evaluation
Generates 5 varied prompts per data type (8 types = 40 prompts total)
"""

PROMPTS = {
    "glucose": [
        {
            "complexity": "simple",
            "prompt": "¿Cuál es mi último valor de glucosa?",
            "expected_agent": "informational"
        },
        {
            "complexity": "temporal",
            "prompt": "Muestra la evolución de mi glucosa en los últimos 30 días",
            "expected_agent": "temporal"
        },
        {
            "complexity": "comparative",
            "prompt": "Compara mi glucosa de la primera quincena vs la segunda quincena del mes pasado",
            "expected_agent": "comparative"
        },
        {
            "complexity": "statistical",
            "prompt": "¿Cuál es el promedio de mi glucosa en ayunas de los últimos 3 meses?",
            "expected_agent": "temporal"
        },
        {
            "complexity": "trend",
            "prompt": "¿Ha aumentado o disminuido mi glucosa en los últimos 6 meses?",
            "expected_agent": "temporal"
        }
    ],
    "blood_pressure": [
        {
            "complexity": "simple",
            "prompt": "¿Cuál es mi presión arterial actual?",
            "expected_agent": "informational"
        },
        {
            "complexity": "temporal",
            "prompt": "¿Cómo ha variado mi presión arterial en las últimas 2 semanas?",
            "expected_agent": "temporal"
        },
        {
            "complexity": "comparative",
            "prompt": "Compara mi presión arterial de este mes con el mes anterior",
            "expected_agent": "comparative"
        },
        {
            "complexity": "statistical",
            "prompt": "¿Cuál es mi presión arterial promedio en los últimos 60 días?",
            "expected_agent": "temporal"
        },
        {
            "complexity": "range",
            "prompt": "¿Cuántas veces mi presión sistólica ha estado por encima de 140 este mes?",
            "expected_agent": "temporal"
        }
    ],
    "weight": [
        {
            "complexity": "simple",
            "prompt": "¿Cuánto peso actualmente?",
            "expected_agent": "informational"
        },
        {
            "complexity": "temporal",
            "prompt": "¿Cómo ha evolucionado mi peso en los últimos 3 meses?",
            "expected_agent": "temporal"
        },
        {
            "complexity": "comparative",
            "prompt": "¿He ganado o perdido peso comparando el trimestre anterior con el actual?",
            "expected_agent": "comparative"
        },
        {
            "complexity": "trend",
            "prompt": "¿Cuál es la tendencia de mi peso en el último año?",
            "expected_agent": "temporal"
        },
        {
            "complexity": "change",
            "prompt": "¿Cuántos kilos he cambiado desde hace 6 meses?",
            "expected_agent": "temporal"
        }
    ],
    "physical_activity": [
        {
            "complexity": "simple",
            "prompt": "¿Cuántos pasos he dado hoy?",
            "expected_agent": "lifestyle"
        },
        {
            "complexity": "temporal",
            "prompt": "Analiza mi nivel de actividad física en el último mes",
            "expected_agent": "lifestyle"
        },
        {
            "complexity": "statistical",
            "prompt": "¿Cuál es mi promedio diario de pasos en los últimos 30 días?",
            "expected_agent": "lifestyle"
        },
        {
            "complexity": "comparative",
            "prompt": "¿He estado más o menos activo esta semana comparado con la semana pasada?",
            "expected_agent": "comparative"
        },
        {
            "complexity": "goal",
            "prompt": "¿Cuántos días he alcanzado más de 10,000 pasos este mes?",
            "expected_agent": "lifestyle"
        }
    ],
    "mood": [
        {
            "complexity": "simple",
            "prompt": "¿Cómo ha sido mi estado de ánimo últimamente?",
            "expected_agent": "lifestyle"
        },
        {
            "complexity": "temporal",
            "prompt": "Muestra mi estado de ánimo de los últimos 14 días",
            "expected_agent": "lifestyle"
        },
        {
            "complexity": "statistical",
            "prompt": "¿Cuál es mi puntuación promedio de estado de ánimo este mes?",
            "expected_agent": "lifestyle"
        },
        {
            "complexity": "trend",
            "prompt": "¿Mi estado de ánimo ha mejorado o empeorado en las últimas semanas?",
            "expected_agent": "temporal"
        },
        {
            "complexity": "pattern",
            "prompt": "¿Hay días de la semana donde mi ánimo suele ser más bajo?",
            "expected_agent": "temporal"
        }
    ],
    "sleep": [
        {
            "complexity": "simple",
            "prompt": "¿Cuántas horas dormí anoche?",
            "expected_agent": "lifestyle"
        },
        {
            "complexity": "temporal",
            "prompt": "Muestra mi patrón de sueño del último mes",
            "expected_agent": "lifestyle"
        },
        {
            "complexity": "statistical",
            "prompt": "¿Cuál es mi promedio de horas de sueño por noche?",
            "expected_agent": "lifestyle"
        },
        {
            "complexity": "comparative",
            "prompt": "¿He dormido más o menos esta semana comparado con la semana pasada?",
            "expected_agent": "comparative"
        },
        {
            "complexity": "quality",
            "prompt": "¿Cuántas noches he dormido menos de 6 horas este mes?",
            "expected_agent": "lifestyle"
        }
    ],
    "cholesterol": [
        {
            "complexity": "simple",
            "prompt": "¿Cuáles son mis niveles actuales de colesterol?",
            "expected_agent": "informational"
        },
        {
            "complexity": "detailed",
            "prompt": "Muéstrame mi último panel lipídico completo (LDL, HDL, triglicéridos)",
            "expected_agent": "informational"
        },
        {
            "complexity": "temporal",
            "prompt": "¿Cómo ha evolucionado mi colesterol LDL en el último año?",
            "expected_agent": "temporal"
        },
        {
            "complexity": "comparative",
            "prompt": "Compara mis niveles de colesterol del análisis más reciente con el anterior",
            "expected_agent": "comparative"
        },
        {
            "complexity": "trend",
            "prompt": "¿Mi colesterol HDL ha aumentado o disminuido en los últimos 6 meses?",
            "expected_agent": "temporal"
        }
    ],
    "correlations": [
        {
            "complexity": "simple_correlation",
            "prompt": "¿Hay relación entre mi nivel de actividad y mi estado de ánimo?",
            "expected_agent": "correlation"
        },
        {
            "complexity": "health_correlation",
            "prompt": "¿Mi sueño afecta mis niveles de glucosa?",
            "expected_agent": "correlation"
        },
        {
            "complexity": "lifestyle_health",
            "prompt": "¿Existe correlación entre mis pasos diarios y mi peso?",
            "expected_agent": "correlation"
        },
        {
            "complexity": "mood_health",
            "prompt": "¿Cómo se relaciona mi estado de ánimo con mi presión arterial?",
            "expected_agent": "correlation"
        },
        {
            "complexity": "multi_factor",
            "prompt": "¿Hay algún patrón entre mi sueño, actividad física y estado de ánimo?",
            "expected_agent": "correlation"
        }
    ]
}


def get_all_prompts():
    """Returns all prompts as a flat list with metadata"""
    all_prompts = []
    for data_type, prompts in PROMPTS.items():
        for prompt_data in prompts:
            all_prompts.append({
                "data_type": data_type,
                **prompt_data
            })
    return all_prompts


def get_prompts_by_type(data_type):
    """Returns prompts for a specific data type"""
    return PROMPTS.get(data_type, [])


def get_prompts_by_complexity(complexity):
    """Returns all prompts of a specific complexity"""
    result = []
    for data_type, prompts in PROMPTS.items():
        for prompt_data in prompts:
            if prompt_data["complexity"] == complexity:
                result.append({
                    "data_type": data_type,
                    **prompt_data
                })
    return result


def print_summary():
    """Prints a summary of generated prompts"""
    total = 0
    print("=== Prompt Generation Summary ===\n")
    for data_type, prompts in PROMPTS.items():
        print(f"{data_type.upper()}: {len(prompts)} prompts")
        total += len(prompts)
    print(f"\nTOTAL: {total} prompts")


if __name__ == "__main__":
    print_summary()
    print("\n=== Sample Prompts ===")
    all_prompts = get_all_prompts()
    for i, p in enumerate(all_prompts[:3], 1):
        print(f"{i}. [{p['data_type']}] {p['prompt']}")
