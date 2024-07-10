import argparse
import os
import json
from datetime import datetime
from importlib import import_module

from tprtools import jsonpath

from utils.rpgmv import RPGMakerMVData

"""
requirements:
thiliapr-tools
"""

__version__ = "1.0.2"


def log(message: str, verbose: bool = False) -> None:
	message = message.replace("\n", "\\n").replace("\\", "\\\\")

	date = datetime.now()
	time_format = "[%02d:%02d:%02d.%03d]" % (date.hour, date.minute, date.second, date.microsecond / 1000)

	if verbose:
		print(time_format, "[verbose]", message)
	else:
		print(time_format, message)


def create_dir(at: str):
	if os.path.exists(at):
		if os.path.isfile(at):
			os.remove(at)
		else:
			return
	os.makedirs(at)


def extract_script(data_path: str, output_path: str, verbose: bool = False):
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

		messages[filename] = RPGMakerMVData.extract_data(filename, data)

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


def apply_script(data_path: str, rpgmaker_script_path: str, output_path: str, verbose: bool = False):
	# Read data files from data path
	log(f"Loading Data...")

	data_files, rpgmaker_scripts = dict(), dict()
	for filename in os.listdir(rpgmaker_script_path):
		if not filename.endswith(".json"):
			continue

		if verbose:
			log(f"Loading {filename}", verbose=True)

		with open(os.path.join(data_path, filename), mode="r", encoding="utf-8") as f:
			data_files[filename] = json.load(f)
		with open(os.path.join(rpgmaker_script_path, filename), mode="r", encoding="utf-8") as f:
			rpgmaker_scripts[filename] = json.load(f)

	log(f"Loaded data.")

	# Source -> Destination
	log(f"Source -> Destination...")

	for filename, data in data_files.items():
		for message in rpgmaker_scripts[filename]:
			context = f"\\n<{message['name']}>{message['message']}" if message["name"] else message["message"]
			jsonpath.assign(data, message["path"], context)

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
	parser.add_argument("action", choices=["extract", "apply"], help="Action")
	parser.add_argument("-d", "--data", help="Game Data Path (extract, apply)")
	parser.add_argument("-s", "--rpgmaker-script", help="RPGMaker Script Path (extract, apply)")
	parser.add_argument("-t", "--translated-data", help="Translated Data Path (apply)")
	parser.add_argument("-v", "--verbose", action="store_true", default=False)
	parser.add_argument("-V", "--version", action="version", version=__version__, help="Show version")
	args = parser.parse_args()

	# Create working directory
	create_dir(args.rpgmaker_script) if args.rpgmaker_script else None
	create_dir(args.translated_data) if args.translated_data else None

	# Do
	if args.action == "extract":
		extract_script(args.data, args.rpgmaker_script, args.verbose)
	elif args.action == "apply":
		apply_script(args.data, args.rpgmaker_script, args.translated_data, args.verbose)


if __name__ == '__main__':
	main()
