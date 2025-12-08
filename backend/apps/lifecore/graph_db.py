import os
from neo4j import GraphDatabase

class GraphDB:
    _driver = None

    @classmethod
    def get_driver(cls):
        if cls._driver is None:
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "quantia_secret_password")
            
            try:
                cls._driver = GraphDatabase.driver(uri, auth=(user, password))
                cls._driver.verify_connectivity()
                print("Connected to Neo4j successfully.")
            except Exception as e:
                print(f"Failed to connect to Neo4j: {e}")
                cls._driver = None
        
        return cls._driver

    @classmethod
    def close(cls):
        if cls._driver:
            cls._driver.close()
            cls._driver = None

    @classmethod
    def run_query(cls, query, parameters=None):
        driver = cls.get_driver()
        if not driver:
            return None
        
        with driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

