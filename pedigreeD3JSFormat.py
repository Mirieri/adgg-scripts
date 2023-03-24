from pyramid.config import Configurator
from pyramid.response import Response
from jinja2 import Environment, FileSystemLoader
import mysql.connector
import json
from wsgiref.simple_server import make_server


def generate_d3_json(data):
    # Create the root node
    root = {"name": "Animal ID: " + str(data[0]['animal_id']),
            "children": []}

    # Create a dictionary to store nodes by ID for easy access
    nodes = {}
    for d in data:
        nodes[d['animal_id']] = {
            "name": d['animal_tag_id'],
            "children": []
        }

    # Add father and mother nodes as children of the root node
    for d in data:
        if d['father_id'] in nodes and d['mother_id'] in nodes:
            father_node = nodes[d['father_id']]
            mother_node = nodes[d['mother_id']]
            # Check if father and mother nodes already have parent nodes
            if 'parent' not in father_node and 'parent' not in mother_node:
                father_node['parent'] = "Father"
                mother_node['parent'] = "Mother"
                root['children'].append(father_node)
                root['children'].append(mother_node)

    # Add daughter and son nodes as children of their respective parents
    for d in data:
        if d['father_id'] in nodes and d['mother_id'] in nodes and d['animal_id'] != d['father_id'] and d['animal_id'] != d['mother_id']:
            animal_node = nodes[d['animal_id']]
            # Check if animal node already has a parent node
            if 'parent' not in animal_node:
                gender = "Daughter" if d['animal_tag_id'].startswith("F") else "Son"
                animal_node['parent'] = gender
                father_node = nodes[d['father_id']]
                mother_node = nodes[d['mother_id']]
                father_node['children'].append(animal_node) if gender == "Son" else None
                mother_node['children'].append(animal_node) if gender == "Daughter" else None

    return root


def tree_json(request):
    # Connect to the database
    cnx = mysql.connector.connect(user='root', password='', host='localhost', database='adgg')
    cursor = cnx.cursor(dictionary=True)

    # Execute the SQL query and get the result
    query = "SELECT " \
            "   id AS animal_id, " \
            "   tag_id AS animal_tag_id, " \
            "   sire_id AS father_id, " \
            "   sire_tag_id AS father_tag_id, " \
            "   dam_id AS mother_id," \
            "   dam_tag_id AS mother_tag_id " \
            "FROM core_animal " \
            "WHERE sire_id IS NOT NULL AND dam_id IS NOT NULL AND " \
            "sire_id = (SELECT sire_id FROM (SELECT sire_id, COUNT(id) num_offspring FROM core_animal " \
            "WHERE sire_id IS NOT NULL AND dam_id IS NOT NULL GROUP BY sire_id ORDER BY COUNT(id) DESC LIMIT 1 ) t)"
    cursor.execute(query)
    result = cursor.fetchall()

    # Generate the JSON data for the tree
    tree_data = generate_d3_json(result)

    # Convert the tree data to JSON
    tree_json = json.dumps(tree_data)

    # Close the database connection
    cursor.close()
    cnx.close()

    # Render the HTML template with the tree data
    env = Environment(loader=FileSystemLoader('View'))
    template = env.get_template('template.html')

    return Response(template.render(tree_data=tree_json))


if __name__ == '__main__':
    config = Configurator()

    config.add_route('tree_json', '/tree.json')
    config.add_view(tree_json, route_name='tree_json')

    app = config.make_wsgi_app()

    try:
        server = make_server('0.0.0.0', 8080, app)
        print("Starting server at http://0.0.0.0:8080")
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
