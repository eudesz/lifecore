# Operaciones de Servidores - QuantIA

Esta guía detalla cómo gestionar los servicios de la plataforma (Frontend, Backend, Base de Datos Gráfica).

## Scripts Automáticos

Hemos creado scripts para facilitar el inicio y parada de todo el entorno.

### Iniciar Todo (`start_all.sh`)
Levanta Neo4j (Docker), Backend (Django) y Frontend (Next.js) y verifica que estén respondiendo.

```bash
./scripts/start_all.sh
```

**Qué hace:**
1. Verifica si Docker está instalado.
2. Inicia el contenedor `neo4j-quantia`. Si no existe, lo crea.
3. Espera a que Neo4j esté listo (Healthcheck en puerto 7474).
4. Mata procesos previos en puerto 8000 si existen.
5. Corre migraciones de Django.
6. Inicia Backend en background (`nohup`).
7. Mata procesos previos en puerto 3000 si existen.
8. Inicia Frontend en background (`nohup`).
9. Verifica status de los 3 servicios y reporta OK/FAIL.

### Apagar Todo (`stop_all.sh`)
Detiene todos los procesos relacionados con la app de forma segura.

```bash
./scripts/stop_all.sh
```

**Qué hace:**
1. Busca y mata el proceso en puerto 8000 (Backend).
2. Busca y mata el proceso en puerto 3000 (Frontend).
3. Detiene el contenedor de Docker `neo4j-quantia`.

---

## Gestión Manual (Por si fallan los scripts)

### 1. Neo4j (Graph Database)
Requiere Docker.

*   **Iniciar:**
    ```bash
    docker start neo4j-quantia
    # O si no existe:
    docker run -d --name neo4j-quantia -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/quantia_secret_password neo4j:latest
    ```
*   **Parar:**
    ```bash
    docker stop neo4j-quantia
    ```
*   **Verificar:** Accede a `http://localhost:7474`.

### 2. Backend (Django)
*   **Ruta:** `cd backend`
*   **Iniciar:**
    ```bash
    python3 manage.py runserver
    ```
*   **Puerto:** 8000

### 3. Frontend (Next.js)
*   **Ruta:** `cd frontend`
*   **Iniciar:**
    ```bash
    npm run dev
    ```
*   **Puerto:** 3000

## Solución de Problemas Comunes

*   **Error: Port already in use**: Ejecuta `./scripts/stop_all.sh` para limpiar procesos huerfanos.
*   **Error: Neo4j connection refused**: Asegúrate de que Docker esté corriendo (`docker ps`).
*   **Logs**:
    *   Backend: Ver archivo `backend.log` en la raíz.
    *   Frontend: Ver archivo `frontend.log` en la raíz.

