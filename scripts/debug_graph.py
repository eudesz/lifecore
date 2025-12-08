import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from apps.lifecore.graph_db import GraphDB

def check_graph(user_id=8):
    print(f"Checking Neo4j for User ID: {user_id}")
    driver = GraphDB.get_driver()
    if not driver:
        print("No driver!")
        return

    with driver.session() as session:
        # 1. Count nodes
        res = session.run("MATCH (n) RETURN count(n) as count").single()
        print(f"Total nodes in DB: {res['count']}")

        # 2. Check Patient
        res = session.run("MATCH (p:Patient {id: $uid}) RETURN p", uid=user_id).single()
        if res:
            print(f"Found Patient node: {res['p']}")
        else:
            print(f"Patient node with id={user_id} NOT FOUND.")
            # List all patients to see what happened
            all_p = session.run("MATCH (p:Patient) RETURN p.id, p.name")
            print("Existing Patients:", [r.data() for r in all_p])

        # 3. Check relationships
        res = session.run("MATCH (p:Patient {id: $uid})-[r]-(n) RETURN count(r) as rels", uid=user_id).single()
        print(f"Relationships for User {user_id}: {res['rels']}")

if __name__ == '__main__':
    check_graph()

