"""
Script para mostrar las queries SQL exactas que se ejecutan
al hacer una pregunta sobre sueño
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

# Activar logging de SQL
import logging
from django.db import connection
from django.db import reset_queries

# Configurar para ver todas las queries
from django.conf import settings
settings.DEBUG = True

from apps.agents_v2.views import analyze

print("="*80)
print("SIMULANDO PREGUNTA: 'Muestra mi patrón de sueño del último mes'")
print("="*80)
print()

# Resetear contador de queries
reset_queries()

# Ejecutar el análisis
payload = {
    'query': 'Muestra mi patrón de sueño del último mes',
    'user_id': '5'  # demo-alex
}

print("📊 EJECUTANDO ANÁLISIS...")
print()

result = analyze(payload, request=None)

print("="*80)
print(f"TOTAL QUERIES EJECUTADAS: {len(connection.queries)}")
print("="*80)
print()

# Mostrar las queries más importantes
lifestyle_queries = []
document_queries = []
other_queries = []

for i, query in enumerate(connection.queries, 1):
    sql = query['sql']
    time = query['time']
    
    # Clasificar queries
    if 'lifecore_observation' in sql and 'sleep_hours' in sql:
        lifestyle_queries.append((i, sql, time))
    elif 'lifecore_document' in sql or 'lifecore_documentchunk' in sql:
        document_queries.append((i, sql, time))
    else:
        other_queries.append((i, sql, time))

# Mostrar queries de datos de sueño
print("🛌 QUERIES DE DATOS DE SUEÑO (Observations)")
print("-"*80)
for i, sql, time in lifestyle_queries[:3]:  # Primeras 3
    print(f"\n[Query #{i}] Tiempo: {time}s")
    print(sql)
    print()

if len(lifestyle_queries) > 3:
    print(f"... y {len(lifestyle_queries) - 3} queries más similares")
print()

# Mostrar queries de documentos (RAG)
print("📄 QUERIES DE DOCUMENTOS (RAG)")
print("-"*80)
for i, sql, time in document_queries[:5]:  # Primeras 5
    print(f"\n[Query #{i}] Tiempo: {time}s")
    print(sql)
    print()

if len(document_queries) > 5:
    print(f"... y {len(document_queries) - 5} queries más similares")
print()

# Resumen
print("="*80)
print("📊 RESUMEN DE QUERIES")
print("="*80)
print(f"Queries de lifestyle data: {len(lifestyle_queries)}")
print(f"Queries de documentos (RAG): {len(document_queries)}")
print(f"Otras queries: {len(other_queries)}")
print(f"TOTAL: {len(connection.queries)}")
print()

# Tiempo total
total_time = sum(float(q['time']) for q in connection.queries)
print(f"⏱️  Tiempo total en DB: {total_time:.4f}s")
print()

print("="*80)
print("✅ RESPUESTA GENERADA:")
print("="*80)
print(result.get('final_text', '')[:500])
print()
print(f"📚 Referencias encontradas: {len(result.get('references', []))}")
for ref in result.get('references', []):
    print(f"  - {ref.get('title', 'Sin título')}")

