from collections.abc import Callable
from tprtools import jsonpath


class RPGMakerMVData:
	ItemTextsKeys: tuple[str] = ("name", "description", "note", "message1", "message2", "message3", "message4")

	@staticmethod
	def event(event: jsonpath.JSONObject, parent_path: str, events_code: list[int], **kwargs) -> list[str]:
		if event["code"] not in events_code:
			return []

		# Choices
		if event["code"] == 102:
			return [jsonpath.concat_path(parent_path, f"$.parameters[0][{i}]") for i in range(len(event["parameters"][0])) if event["parameters"][0][i]]
		# Comment
		elif event["code"] == 108:
			return [jsonpath.concat_path(parent_path, "$.parameters[0]")] if event["parameters"][0] else []
		# Text
		elif event["code"] == 401:
			return [jsonpath.concat_path(parent_path, "$.parameters[0]")] if event["parameters"][0] else []

	@staticmethod
	def items(items: list, **kwargs) -> list[str]:
		messages: list[str] = [
			message_path
			for item_index in range(len(items))
			for message_path in (
				[f"$[{item_index}].{key}" for key in RPGMakerMVData.ItemTextsKeys if items[item_index].get(key)]
				if items[item_index] else []
			)
		]
		
		return messages

	@staticmethod
	def troops(troops: list, events_code: list[int], **kwargs) -> list[str]:
		messages: list[str] = RPGMakerMVData.items(troops)

		# Events
		messages += [
			message_path
			for troop_index in range(len(troops))
			for page_index in range(len(troops[troop_index]["pages"]) if troops[troop_index] else 0)
			for event_index in range(len(troops[troop_index]["pages"][page_index]["list"]))
			for message_path in RPGMakerMVData.event(troops[troop_index]["pages"][page_index]["list"][event_index], f"$[{troop_index}].pages[{page_index}].list[{event_index}]", events_code)
		]

		return messages

	@staticmethod
	def map_events(map_events: dict, events_code: list[int], **kwargs) -> list[str]:
		messages: list[str] = [
			message_path
			for map_event_index in range(len(map_events["events"]))
			for page_index in range(len(map_events["events"][map_event_index]["pages"]) if map_events["events"][map_event_index] else 0)
			for event_index in range(len(map_events["events"][map_event_index]["pages"][page_index]["list"]))
			for message_path in RPGMakerMVData.event(map_events["events"][map_event_index]["pages"][page_index]["list"][event_index], f"$.events[{map_event_index}].pages[{page_index}].list[{event_index}]", events_code)
		]

		# Display Name
		if map_events["displayName"]:
			messages += "$.displayName"

		return messages

	@staticmethod
	def common_events(events: list, events_code: list[int], **kwargs) -> list[str]:
		messages: list[str] = [
			message_path
			for common_event_index in range(len(events))
			for event_index in range(len(events[common_event_index]["list"]) if events[common_event_index] else 0)
			for message_path in RPGMakerMVData.event(events[common_event_index]["list"][event_index], f"$[{common_event_index}].list[{event_index}]", events_code)
		]

		return messages

	@staticmethod
	def system_json(system_json: dict, **kwargs) -> list[str]:
		messages: list[str] = []

		# Outside
		messages.append("$.currencyUnit")
		messages.append("$.gameTitle")

		# Terms
		messages += [
			f"$.terms.{term_key}.{('[%s]' if isinstance(system_json['terms'][term_key], list) else '%s') % item_key}"
			for term_key in system_json["terms"]
			for item_key in (system_json["terms"][term_key] if isinstance(system_json["terms"][term_key], dict) else range(len(system_json["terms"][term_key])))
			if system_json["terms"][term_key][item_key]
		]

		return messages

	@staticmethod
	def extract_data(filename: str, data: jsonpath.JSONObject, **kwargs) -> list[str]:
		extract_func: Callable[[jsonpath.JSONObject, ...], list[str]]

		# Setting Extract Function
		if filename == "CommonEvents.json":
			extract_func = RPGMakerMVData.common_events
		elif filename == "System.json":
			extract_func = RPGMakerMVData.system_json
		elif filename == "Troops.json":
			extract_func = RPGMakerMVData.troops
		elif filename.startswith("Map") and filename[3:-5].isdigit():
			extract_func = RPGMakerMVData.map_events
		elif isinstance(data, list):
			extract_func = RPGMakerMVData.items

		# Run
		return extract_func(data, **kwargs)
