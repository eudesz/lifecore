import os
import sys
import django
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from apps.lifecore.models import TimelineEvent, Condition, Document
from apps.lifecore.treatment_models import Treatment
from django.contrib.auth.models import User
from apps.lifecore.graph_db import GraphDB

def sync_graph(user_id=8):
    print(f"Syncing Knowledge Graph for User {user_id}...")
    driver = GraphDB.get_driver()
    if not driver:
        print("Skipping sync: Neo4j driver not available.")
        return

    user = User.objects.get(id=user_id)

    with driver.session() as session:
        # 1. Reset/Clean graph for this user (Full refresh for prototype)
        session.run("MATCH (n) DETACH DELETE n") 
        print("Graph cleared.")

        # 2. Create Patient Node
        session.run("""
            CREATE (p:Patient {id: $uid, name: $name, username: $username})
        """, uid=user.id, name="Alexander Synthetic", username=user.username)
        print("Patient node created.")

        # 3. Load Conditions (Nodes)
        # We extract distinct conditions from Event links or Condition model
        conditions = Condition.objects.filter(event_links__event__user_id=user_id).distinct()
        for cond in conditions:
            session.run("""
                MATCH (p:Patient {id: $uid})
                MERGE (c:Condition {name: $name})
                MERGE (p)-[:SUFFERS_FROM]->(c)
            """, uid=user.id, name=cond.name)
        print(f"Loaded {conditions.count()} conditions.")

        # 4. Load Treatments (Nodes)
        treatments = Treatment.objects.filter(user_id=user_id)
        for tx in treatments:
            session.run("""
                MATCH (p:Patient {id: $uid})
                MERGE (m:Medication {name: $name})
                MERGE (p)-[:TAKES {start_date: $start, status: $status}]->(m)
            """, uid=user.id, name=tx.name, start=str(tx.start_date), status=tx.status)
            
            # Linking Meds to Conditions (Naive: logic based on common knowledge or manual map)
            # In a real system, this comes from a KB or LLM extraction
            if "Metformina" in tx.name:
                session.run("MATCH (m:Medication {name: $name}), (c:Condition) WHERE c.name CONTAINS 'Diabetes' MERGE (m)-[:TREATS]->(c)", name=tx.name)
            if "Lisinopril" in tx.name:
                session.run("MATCH (m:Medication {name: $name}), (c:Condition) WHERE c.name CONTAINS 'Hipertension' MERGE (m)-[:TREATS]->(c)", name=tx.name)
            if "Atorvastatina" in tx.name:
                session.run("MATCH (m:Medication {name: $name}), (c:Condition) WHERE c.name CONTAINS 'Dislipidemia' MERGE (m)-[:TREATS]->(c)", name=tx.name)

        print(f"Loaded {treatments.count()} treatments.")

        # 5. Load Timeline Events (As Event Nodes linked to Patient)
        events = TimelineEvent.objects.filter(user_id=user_id)
        for ev in events:
            # Create Event Node
            session.run("""
                MATCH (p:Patient {id: $uid})
                CREATE (e:Event {
                    id: $eid, 
                    date: $date, 
                    kind: $kind, 
                    category: $category,
                    title: $title,
                    role: $role
                })
                CREATE (p)-[:EXPERIENCED]->(e)
            """, uid=user.id, eid=ev.id, date=ev.occurred_at.isoformat(), kind=ev.kind, category=ev.category, title=ev.payload.get('title', 'Untitled'), role=(ev.data_summary or {}).get('role', 'general'))

            # Link Event to Conditions
            for cond in ev.related_conditions:
                session.run("""
                    MATCH (e:Event {id: $eid})
                    MATCH (c:Condition {name: $cname})
                    MERGE (e)-[:RELATES_TO]->(c)
                """, eid=ev.id, cname=cond)

        print(f"Loaded {events.count()} timeline events.")
        
        # 6. Load Documents (Nodes) & Simple NER
        documents = Document.objects.filter(user_id=user_id)
        for doc in documents:
            session.run("""
                MATCH (p:Patient {id: $uid})
                CREATE (d:Document {id: $did, title: $title, date: $date})
                CREATE (p)-[:HAS_RECORD]->(d)
            """, uid=user.id, did=doc.id, title=doc.title, date=doc.created_at.isoformat())
            
            # Simple keyword matching to link Docs to Concepts (instead of full LLM for now)
            content_lower = (doc.content or "").lower()
            
            # Link to Conditions mentioned
            for cond in conditions:
                if cond.name.lower() in content_lower:
                    session.run("""
                        MATCH (d:Document {id: $did})
                        MATCH (c:Condition {name: $cname})
                        MERGE (d)-[:MENTIONS]->(c)
                    """, did=doc.id, cname=cond.name)
            
            # Link to Meds mentioned
            for tx in treatments:
                if tx.name.lower() in content_lower:
                    session.run("""
                        MATCH (d:Document {id: $did})
                        MATCH (m:Medication {name: $mname})
                        MERGE (d)-[:MENTIONS]->(m)
                    """, did=doc.id, mname=tx.name)

        print(f"Loaded {documents.count()} documents.")

    print("Graph sync complete.")

if __name__ == '__main__':
    # Allow optional user_id argument: `python scripts/sync_graph.py 9`
    try:
        arg_uid = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    except Exception:
        arg_uid = 8
    sync_graph(user_id=arg_uid)

