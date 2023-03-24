import unittest
from pedigreeD3JSFormat import generate_d3_json


class TestTreeJson(unittest.TestCase):
    # Setup method to create test data
    def setUp(self):
        self.data = [
            {'animal_id': 1, 'animal_tag_id': 'A', 'father_id': 2, 'father_tag_id': 'B', 'mother_id': 3, 'mother_tag_id': 'C'},
            {'animal_id': 2, 'animal_tag_id': 'B', 'father_id': 4, 'father_tag_id': 'D', 'mother_id': 5, 'mother_tag_id': 'E'},
            {'animal_id': 3, 'animal_tag_id': 'C', 'father_id': 6, 'father_tag_id': 'F', 'mother_id': 7, 'mother_tag_id': 'G'}
        ]

    # Test if the generate_d3_json() method returns correct data type
    def test_generate_d3_json_return_format(self):
        result = generate_d3_json(self.data)
        self.assertIsInstance(result, dict)

    # Test if the root node contains correct number of children
    def test_root_node_contains_correct_number_of_children(self):
        result = generate_d3_json(self.data)
        self.assertEqual(len(result['children']), 2)

    # Test if the father and mother nodes are added properly
    def test_father_mother_nodes_added_properly(self):
        result = generate_d3_json(self.data)
        father_node = result['children'][0]
        mother_node = result['children'][1]
        self.assertEqual(father_node['name'], 'B')
        self.assertEqual(mother_node['name'], 'C')

    # Test if the daughter and son nodes are added properly
    def test_daughter_son_nodes_added_properly(self):
        result = generate_d3_json(self.data)
        father_node = result['children'][0]
        mother_node = result['children'][1]
        daughter_node = father_node['children'][0]
        son_node = mother_node['children'][0]
        self.assertEqual(daughter_node['name'], 'A')
        self.assertEqual(son_node['name'], 'B')


# Main method to run the tests
if __name__ == '__main__':
    unittest.main()
