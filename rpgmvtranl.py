import argparse
import os
import time
import json

from tprtools import jsonpath

from utils.rpgmv import RPGMakerMVData

"""
requirements:
thiliapr-tools
"""

__version__ = "1.0.1"


def log(message: str, verbose: bool = False) -> None:
	message = message.replace("\n", "\\n").replace("\\", "\\\\")

	if verbose:
		print(time.strftime("[%Y-%m-%d] [%H:%M:%S]"), "[verbose]", message)
	else:
		print(time.strftime("[%Y-%m-%d] [%H:%M:%S]"), message)


def create_dir(at: str):
	if os.path.exists(at):
		if os.path.isfile(at):
			os.remove(at)
		else:
			return
	os.makedirs(at)


def extract_script(data_path: str, output_path: str, events_code: list[int], verbose: bool = False):
	# Read data files from data path
	log(f"Loading Data...")

	data_files = {}
	for filename in os.listdir(data_path):
		if not filename.endswith(".json"):
			continue

		if verbose:
			log(f"Loading {filename}", verbose=True)

		with open(os.path.join(data_path, filename), mode="r", encoding="utf-8") as f:
			data_files[filename] = json.load(f)

	log(f"Loaded data.")

	# Scan messages to translate
	log(f"Extracting Data...")

	messages: dict[str, list[str]] = {}
	for filename, data in data_files.items():
		if verbose:
			log(f"Extracting {filename}", verbose=True)

		if filename == "CommonEvents.json":
			messages[filename] = [{"path": message_path, "message": jsonpath.get(data, message_path)} for message_path in RPGMakerMVData.common_events(data, events_code)]
		elif filename == "System.json":
			messages[filename] = [{"path": message_path, "message": jsonpath.get(data, message_path)} for message_path in RPGMakerMVData.system_json(data)]
		elif isinstance(data, list):
			messages[filename] = [{"path": message_path, "message": jsonpath.get(data, message_path)} for message_path in RPGMakerMVData.items(data)]
		elif isinstance(data, dict):
			messages[filename] = [{"path": message_path, "message": jsonpath.get(data, message_path)} for message_path in RPGMakerMVData.map_events(data, events_code)]

	log(f"Extracted data.")

	# Remove empty JSONObjects in messages
	messages = {message_file: file_messages for message_file, file_messages in messages.items() if file_messages}

	if verbose:
		log(f"Scripts: {list(messages.keys())}", verbose=True)

	# Export messages to rpgmaker scripts
	log(f"Start to Export Scripts")
	for filename, message_paths in messages.items():
		if verbose:
			log(f"Exporting {filename}", verbose=True)

		with open(os.path.join(output_path, filename), encoding="utf-8", mode="w") as f:
			json.dump(message_paths, f, indent="\t", ensure_ascii=False)

	log(f"Exported scripts.")


def generate_galtransl_script(script_path: str, output_path: str, verbose: bool = False):
	# Read data files from data path
	log(f"Loading Data...")

	script_files = {}
	for filename in os.listdir(script_path):
		if not filename.endswith(".json"):
			continue

		if verbose:
			log(f"Loading {filename}", verbose=True)

		with open(os.path.join(script_path, filename), mode="r", encoding="utf-8") as f:
			script_files[filename] = json.load(f)

	log(f"Loaded data.")

	# To GalTransl Script
	scripts = {filename: [{"message": message["message"]} for message in messages] for filename, messages in script_files.items()}

	if verbose:
		log(f"Scripts: {list(scripts.keys())}", verbose=True)

	# Export scripts to GalTransl Scripts
	log(f"Start to Export Scripts.")
	for filename, context in scripts.items():
		if verbose:
			log(f"Exporting {filename}", verbose=True)

		with open(os.path.join(output_path, filename), encoding="utf-8", mode="w") as f:
			json.dump(context, f, indent="\t", ensure_ascii=False)

	log(f"Exported scripts.")


def apply_script(data_path: str, rpgmaker_script_path: str, galtransl_script_path: str, output_path: str, verbose: bool = False):
	# Read data files from data path
	log(f"Loading Data...")

	data_files, rpgmaker_scripts, galtransl_scripts = [dict() for _ in range(3)]
	for filename in os.listdir(rpgmaker_script_path):
		if not filename.endswith(".json"):
			continue

		if verbose:
			log(f"Loading {filename}", verbose=True)

		with open(os.path.join(data_path, filename), mode="r", encoding="utf-8") as f:
			data_files[filename] = json.load(f)
		with open(os.path.join(rpgmaker_script_path, filename), mode="r", encoding="utf-8") as f:
			rpgmaker_scripts[filename] = json.load(f)
		with open(os.path.join(galtransl_script_path, filename), mode="r", encoding="utf-8") as f:
			galtransl_scripts[filename] = json.load(f)

	log(f"Loaded data.")

	# Merge translation and path
	rpgmaker_translations = {
		filename: [rpgmaker_message | translation_message for rpgmaker_message, translation_message in zip(rpgmaker_messages, translation_messages)]
		for filename, rpgmaker_messages, translation_messages in zip(rpgmaker_scripts.keys(), rpgmaker_scripts.values(), galtransl_scripts.values())
	}

	# Source -> Destination
	log(f"Source -> Destination...")
	[jsonpath.assign(data, message_info["path"], message_info["message"]) for filename, data in data_files.items() for message_info in rpgmaker_translations[filename]]
	log(f"Source -> Destination is OK.")

	# Export Files
	log(f"Start to Export Scripts.")
	for filename, context in data_files.items():
		if verbose:
			log(f"Exporting {filename}", verbose=True)

		with open(os.path.join(output_path, filename), encoding="utf-8", mode="w") as f:
			json.dump(context, f, indent="\t", ensure_ascii=False)

	log(f"Exported scripts.")


def main():
	parser = argparse.ArgumentParser(description="RPGMaker MV/MZ Script Extractor")
	parser.add_argument("action", choices=["extract", "galtransl", "apply"], help="Action")
	parser.add_argument("-d", "--data", help="Game Data Path (extract, apply)")
	parser.add_argument("-s", "--rpgmaker-script", help="RPGMaker Script Path (extract, galtransl, apply)")
	parser.add_argument("-g", "--galtransl-script", help="GalTransl Script Path (galtransl, apply)")
	parser.add_argument("-t", "--translated-data", help="Translated Data Path (apply)")
	parser.add_argument("-e", "--only-needed-events", action="store_true", help="Translate only displayable events.")
	parser.add_argument("-v", "--verbose", action="store_true", default=False)
	parser.add_argument("-V", "--version", action="version", version=__version__, help="Show version")
	args = parser.parse_args()

	events_code: list[int] = [102, 401] if args.only_needed_events else [102, 108, 401]

	# Create working directory
	create_dir(args.rpgmaker_script) if args.rpgmaker_script else None
	create_dir(args.galtransl_script) if args.galtransl_script else None
	create_dir(args.translated_data) if args.translated_data else None

	# Do command
	if args.action == "extract":
		extract_script(args.data, args.rpgmaker_script, events_code, args.verbose)
	elif args.action == "galtransl":
		generate_galtransl_script(args.rpgmaker_script, args.galtransl_script, args.verbose)
	elif args.action == "apply":
		apply_script(args.data, args.rpgmaker_script, args.galtransl_script, args.translated_data, args.verbose)


if __name__ == '__main__':
	main()
