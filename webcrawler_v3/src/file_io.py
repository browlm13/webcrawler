import json
import os

# read in config/directory_structure.json
# handle reading and writing of data

DIRECTORY_STRUCTURE_FILE_PATH = "config/directory_structure.json"   #from root

def load_directory_structure():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    head = os.path.commonprefix([script_dir, DIRECTORY_STRUCTURE_FILE_PATH])
    file_path = os.path.join(head, DIRECTORY_STRUCTURE_FILE_PATH)
    with open(file_path) as json_data:
        directory_structure_dict = json.load(json_data)

    return directory_structure_dict

def save(type, data, parameters_list):
    directory_structure_dict = load_directory_structure()
    print(directory_structure_dict['path_templates'][type])
    print(parameters_list)
    file_path = directory_structure_dict['path_templates'][type] % tuple(parameters_list)
    directory_path = os.path.split(file_path)[0]

    # if directory does not exist, create it
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # write response summary file
    with open(file_path, 'w') as file:
        file.write(json.dumps(data))