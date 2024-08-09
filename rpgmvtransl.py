import argparse
import os
import json
from datetime import datetime

from tprtools import jsonpath

from utils.rpgmv import RPGMakerMVData

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
    log(f"Extracting Data...")

    for filename in os.listdir(data_path):
        if not filename.endswith(".json"):
            continue

        # 展示进度
        if verbose:
            log(f"Extracting {filename}", verbose=True)

        # 加载原始游戏文件
        with open(os.path.join(data_path, filename), mode="r", encoding="utf-8-sig") as f:
            data: jsonpath.JSONObject = json.load(f)

        # 提取游戏文本
        messages = [{k: v for k, v in {"message": msg["message"], "speaker": msg.get("speaker"), "additional_info": msg["path"]}.items() if v is not None} for msg in RPGMakerMVData.extract_data(filename, data)]

        # 如果什么也没有提取到，就跳过这个文件
        if not messages:
            continue

        # 导出文本
        with open(os.path.join(output_path, filename), encoding="utf-8", mode="w") as f:
            json.dump(messages, f, indent="\t", ensure_ascii=False)

    log(f"Extracted all data.")


def apply_script(data_path: str, rpgmaker_script_path: str, output_path: str, verbose: bool = False):
    log(f"Applying Data...")

    for filename in os.listdir(rpgmaker_script_path):
        if not filename.endswith(".json"):
            continue

        # 展示进度
        if verbose:
            log(f"Applying {filename}", verbose=True)

        # 加载原始游戏文件
        with open(os.path.join(data_path, filename), mode="r", encoding="utf-8-sig") as f:
            data: jsonpath.JSONObject = json.load(f)

        # 加载翻译文件
        with open(os.path.join(rpgmaker_script_path, filename), mode="r", encoding="utf-8") as f:
            rpgmaker_script: list[dict[str, str]] = json.load(f)

        # 还原游戏文件
        for message in rpgmaker_script:
            try:
                # 假设有说话的人
                destination = f"\\n<{message['speaker_translation']}>{message['translation']}"
            except KeyError:
                # 如果没有就只是译文
                destination = message["translation"]

            jsonpath.assign(data, message["additional_info"], destination)

        # 导出游戏文件
        with open(os.path.join(output_path, filename), encoding="utf-8-sig", mode="w") as f:
            json.dump(data, f, indent="\t", ensure_ascii=False)


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
