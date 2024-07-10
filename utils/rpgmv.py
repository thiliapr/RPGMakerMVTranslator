from typing import Any
from collections.abc import Callable
from tprtools import jsonpath


class RPGMakerMVData:
	ItemTextsKeys: tuple[str] = ("name", "description", "note", "message1", "message2", "message3", "message4")
	SystemJSONKeys: tuple[str] = ("currencyUnit", "gameTitle")

	@staticmethod
	def event(event: jsonpath.JSONObject, parent_path: str, **kwargs) -> list[dict[str, Any]]:
		messages: list[dict[str, Any]] = []

		# Choices
		if event["code"] == 102:
			paths = [f"$.parameters[0][{i}]" for i in range(len(event["parameters"][0])) if event["parameters"][0][i]]
			return [{"message": jsonpath.get(event, path), "path": jsonpath.concat_path(parent_path, path)} for path in paths]
		# Text
		elif event["code"] == 401 and event["parameters"][0]:
			message: dict[str, Any] = {
				"message": event["parameters"][0],
				"path": jsonpath.concat_path(parent_path, "$.parameters[0]")
			}

			# With Name
			if message["message"].startswith("\\n<"):
				message["name"] = message["message"][3:message["message"].find(">")]
				message["message"] = message["message"][message["message"].find(">") + 1:]

			# Add message info to messages
			messages.append(message)

		# Unknown Event
		return messages

	@staticmethod
	def items(items: list, **kwargs) -> list[dict[str, Any]]:
		messages: list[dict[str, Any]] = [
			{"message": jsonpath.get(items, path), "path": path}
			for item_index in range(len(items))
			for path in (
				[f"$[{item_index}].{key}" for key in RPGMakerMVData.ItemTextsKeys if items[item_index].get(key)]
				if items[item_index] else []
			)
		]
		
		return messages

	@staticmethod
	def troops(troops: list, **kwargs) -> list[dict[str, Any]]:
		messages: list[dict[str, Any]] = RPGMakerMVData.items(troops)

		# Events
		messages += [
			message
			for troop_index in range(len(troops))
			for page_index in range(len(troops[troop_index]["pages"]) if troops[troop_index] else 0)
			for event_index in range(len(troops[troop_index]["pages"][page_index]["list"]))
			for message in RPGMakerMVData.event(troops[troop_index]["pages"][page_index]["list"][event_index], f"$[{troop_index}].pages[{page_index}].list[{event_index}]", **kwargs)
		]

		return messages

	@staticmethod
	def map_events(map_events: dict, **kwargs) -> list[dict[str, Any]]:
		messages: list[dict[str, Any]] = [
			message
			for map_event_index in range(len(map_events["events"]))
			for page_index in range(len(map_events["events"][map_event_index]["pages"]) if map_events["events"][map_event_index] else 0)
			for event_index in range(len(map_events["events"][map_event_index]["pages"][page_index]["list"]))
			for message in RPGMakerMVData.event(map_events["events"][map_event_index]["pages"][page_index]["list"][event_index], f"$.events[{map_event_index}].pages[{page_index}].list[{event_index}]", **kwargs)
		]

		# Display Name
		if map_events["displayName"]:
			messages += "$.displayName"

		return messages

	@staticmethod
	def common_events(events: list, **kwargs) -> list[dict[str, Any]]:
		messages: list[dict[str, Any]] = [
			message
			for common_event_index in range(len(events))
			for event_index in range(len(events[common_event_index]["list"]) if events[common_event_index] else 0)
			for message in RPGMakerMVData.event(events[common_event_index]["list"][event_index], f"$[{common_event_index}].list[{event_index}]")
		]

		return messages

	@staticmethod
	def system_json(system_json: dict, **kwargs) -> list[dict[str, Any]]:
		paths: list[dict[str, Any]] = [k for k in RPGMakerMVData.SystemJSONKeys]

		# Terms
		paths += [
			f"$.terms.{term_key}.{('[%s]' if isinstance(system_json['terms'][term_key], list) else '%s') % item_key}"
			for term_key in system_json["terms"]
			for item_key in (system_json["terms"][term_key] if isinstance(system_json["terms"][term_key], dict) else range(len(system_json["terms"][term_key])))
			if system_json["terms"][term_key][item_key]
		]

		return [{"message": jsonpath.get(system_json, path), "path": path} for path in paths]

	@staticmethod
	def extract_data(filename: str, data: jsonpath.JSONObject, **kwargs) -> list[dict[str, Any]]:
		extract_func: Callable[[jsonpath.JSONObject, ...], list[dict[str, Any]]]

		# Setting Extract Function
		if filename == "CommonEvents.json":
			extract_func = RPGMakerMVData.common_events
		elif filename == "System.json":
			extract_func = RPGMakerMVData.system_json
		elif filename == "Troops.json":
			extract_func = RPGMakerMVData.troops
		elif filename.startswith("Map") and filename[3:-5].isdecimal():
			extract_func = RPGMakerMVData.map_events
		elif isinstance(data, list):
			extract_func = RPGMakerMVData.items

		# Run
		return extract_func(data, **kwargs)
