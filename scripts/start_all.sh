#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting QuantIA Platform Services...${NC}"

# Check for Docker (Required for Neo4j)
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed or not in PATH.${NC}"
    exit 1
fi

# 1. Start Neo4j Container
echo "Checking Neo4j container..."
if [ ! "$(docker ps -q -f name=neo4j-quantia)" ]; then
    if [ "$(docker ps -aq -f name=neo4j-quantia)" ]; then
        echo "Starting existing Neo4j container..."
        docker start neo4j-quantia
    else
        echo "Creating and starting new Neo4j container..."
        docker run -d \
            --name neo4j-quantia \
            -p 7474:7474 -p 7687:7687 \
            -e NEO4J_AUTH=neo4j/quantia_secret_password \
            neo4j:latest
    fi
else
    echo "Neo4j is already running."
fi

# Wait for Neo4j to be ready
echo "Waiting for Neo4j to be ready (this may take a few seconds)..."
until curl --silent --fail http://localhost:7474 > /dev/null; do
    printf '.'
    sleep 2
done
echo -e "\n${GREEN}Neo4j is UP!${NC}"


# 2. Start Backend (Django)
echo "Starting Backend (Django)..."
# Check if port 8000 is in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${RED}Port 8000 is already in use. Killing process...${NC}"
    kill -9 $(lsof -Pi :8000 -sTCP:LISTEN -t)
fi

cd backend
# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run migrations to be safe
echo "Running database migrations..."
python3 manage.py migrate

# Start server in background
nohup python3 manage.py runserver 0.0.0.0:8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started with PID $BACKEND_PID. Logs at backend.log"
cd ..

# 3. Start Frontend (Next.js)
echo "Starting Frontend (Next.js)..."
# Check if port 3000 is in use
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${RED}Port 3000 is already in use. Killing process...${NC}"
    kill -9 $(lsof -Pi :3000 -sTCP:LISTEN -t)
fi

cd frontend
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started with PID $FRONTEND_PID. Logs at frontend.log"
cd ..


# 4. Final Verification
echo -e "\n${GREEN}All services initiated. Verifying status...${NC}"
sleep 5

# Check Backend
if curl --silent --fail http://localhost:8000/admin/login/ > /dev/null; then
    echo -e "Backend: ${GREEN}OK${NC}"
else
    echo -e "Backend: ${RED}FAIL${NC} (Check backend.log)"
fi

# Check Frontend
if curl --silent --head http://localhost:3000 > /dev/null; then
    echo -e "Frontend: ${GREEN}OK${NC}"
else
    echo -e "Frontend: ${RED}FAIL${NC} (Check frontend.log)"
    # Note: Next.js dev server might take longer to compile, so a fail here isn't always fatal immediately
fi

# Check Neo4j
if curl --silent --fail http://localhost:7474 > /dev/null; then
    echo -e "Neo4j:   ${GREEN}OK${NC}"
else
    echo -e "Neo4j:   ${RED}FAIL${NC}"
fi

echo -e "\n${GREEN}QuantIA Platform is running!${NC}"
echo "Access Frontend: http://localhost:3000"
echo "Access Backend:  http://localhost:8000"
echo "Access Neo4j:    http://localhost:7474 (user: neo4j, pass: quantia_secret_password)"

