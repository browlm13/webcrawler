import json
import os

# read in config/directory_structure.json
# handle reading and writing of data

DIRECTORY_STRUCTURE_FILE_PATH = "config/directory_structure.json"

def load_directory_structure():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    head = os.path.commonprefix([script_dir, DIRECTORY_STRUCTURE_FILE_PATH])
    file_path = os.path.join(head, DIRECTORY_STRUCTURE_FILE_PATH)
    with open(file_path) as json_data:
        directory_structure_dict = json.load(json_data)

    return directory_structure_dict



"""
def save(self, file_path):
    with open(file_path, 'w') as file:
        file.write(json.dumps(self.get_map()))

"""