"""""

run.py

Brief: this file will run the whole project. 

Note: all configuration and preferences should be set in the config.py file.

Ronald Rihoo

"""""

from prepare import process_map
from log import load_learned_names_list, manage_directory, produce_logs

# run the main loop and then save all of the existing logs
def run():
	manage_directory('', 'OSM_Auditor')
	load_learned_names_list()

	data = process_map(neat_format = True)              # 'True': pretty/neat print format

	produce_logs(dev = True)                            # 'True': produces extra logs for development/grading ease

	return

if __name__ == "__main__":
    run()