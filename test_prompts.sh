#!/usr/bin/env bash
# Script para probar los 10 prompts del documento PROMPTS-TEST.md
# Usa la API directamente para verificar las respuestas

set -euo pipefail

API_URL="http://127.0.0.1:8000/api/agents/v2/analyze"
API_KEY="dev-secret-key"
USER_ID=5

echo "======================================"
echo "QuantIA - Test de Prompts por API"
echo "======================================"
echo ""

# Array de prompts a probar
declare -a PROMPTS=(
  "1|¿Cuáles fueron mis últimas consultas de 2024? Dame un resumen breve."
  "2|¿Qué tratamientos activos tuve entre 2011 y 2018? Incluye inicios y ajustes."
  "3|¿Cómo evolucionó mi glucosa entre 2019 y 2024? Promedio y tendencia."
  "4|¿Hay relación entre mis pasos diarios y mi peso en 2023? Resume hallazgos."
  "5|Muéstrame los diagnósticos de Diabetes de 2010 a 2025 (top 5 con fecha)."
  "6|Compara mi presión arterial: 2020 vs 2024 (promedios y variación)."
  "7|¿Cómo fue mi adherencia a tratamientos para Diabetes entre 2016 y 2018?"
  "8|Resumen trimestral 2024: consultas y cambios de tratamiento más relevantes."
  "9|Busca documentos de 2014 a 2016 que contengan \"insulina basal\" (título y fecha)."
  "10|En el contexto filtrado actual, dame un \"Resumen del contexto\" y 3 insights clave."
)

# Función para probar un prompt
test_prompt() {
  local num=$1
  local prompt=$2
  
  echo "======================================"
  echo "PROMPT $num"
  echo "======================================"
  echo "Pregunta: $prompt"
  echo ""
  echo "Enviando request..."
  
  # Crear payload JSON
  local payload=$(cat <<EOF
{
  "user_id": $USER_ID,
  "query": "$prompt",
  "context": {
    "date_from": "2000-01-01",
    "date_to": "2025-12-31",
    "categories": [],
    "conditions": []
  }
}
EOF
)
  
  # Hacer request y capturar respuesta
  local response=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $API_KEY" \
    -d "$payload")
  
  # Verificar si hay error
  if echo "$response" | grep -q '"error"'; then
    echo "❌ ERROR:"
    echo "$response" | jq -r '.error // .detail // .'
  else
    echo "✅ RESPUESTA RECIBIDA"
    echo ""
    echo "Categoría detectada: $(echo "$response" | jq -r '.category // "N/A"')"
    echo ""
    echo "Respuesta:"
    echo "$response" | jq -r '.response // .answer // .'
    echo ""
    echo "Referencias: $(echo "$response" | jq -r '.references | length // 0')"
  fi
  
  echo ""
  echo ""
}

# Probar cada prompt
for item in "${PROMPTS[@]}"; do
  IFS='|' read -r num prompt <<< "$item"
  test_prompt "$num" "$prompt"
  sleep 2  # Dar tiempo entre requests
done

echo "======================================"
echo "TEST COMPLETADO"
echo "======================================"


