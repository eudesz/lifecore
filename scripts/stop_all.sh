#!/bin/bash

# Define colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${RED}Stopping all QuantIA services...${NC}"

# Kill processes on port 8000 (Backend)
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Stopping Backend (Port 8000)..."
    kill -9 $(lsof -Pi :8000 -sTCP:LISTEN -t)
    echo "Backend stopped."
else
    echo "Backend not running."
fi

# Kill processes on port 3000 (Frontend)
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Stopping Frontend (Port 3000)..."
    kill -9 $(lsof -Pi :3000 -sTCP:LISTEN -t)
    echo "Frontend stopped."
else
    echo "Frontend not running."
fi

# Stop Neo4j Container
if [ "$(docker ps -q -f name=neo4j-quantia)" ]; then
    echo "Stopping Neo4j container..."
    docker stop neo4j-quantia
    echo "Neo4j stopped."
else
    echo "Neo4j container not running."
fi

echo -e "${GREEN}All services stopped.${NC}"

