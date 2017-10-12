from py2neo import Graph, authenticate, Node, Relationship, Path

graph = Graph
authenticate("localhost:7474", "neo4j", "password")
graph = Graph("http://localhost:7474/Desktop/SciGraph/data/neo4j/data/")

graph.delete_all()

with open("../data/springernature-scigraph-grants.2017-02-15.nt") as grants:
    for line in grants:
        line = line.rstrip(' .\n').split(' ', 2)

        grant_node = Node("Grant", grant=line[0])
        obj_node = Node("Object", object=line[2])

        graph.merge(grant_node, "Grant", 'grant')
        graph.merge(obj_node, "Object", 'object')

        grant_pred_obj = Relationship(grant_node, line[1], obj_node)
        graph.create(grant_pred_obj)

        grant_node.push()
        obj_node.push()
