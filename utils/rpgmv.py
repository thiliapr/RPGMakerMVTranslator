from tprtools import jsonpath


class RPGMakerMVData:
	ItemTextsKeys: tuple[str] = ("name", "description", "note", "message1", "message2", "message3", "message4")
	SystemJSONItemsKeys: tuple[str] = ("armorTypes", "elements", "equipTypes", "skillTypes", "weaponTypes")

	@staticmethod
	def event(event: jsonpath.JSONObject, parent_path: str, events_code: list[int]) -> list[str] | None:
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
	def items(items: list) -> list[str]:
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
	def map_events(map_events: dict, events_code: list[int]) -> list[str]:
		messages: list[str] = [
			message_path
			for map_event_index in range(len(map_events["events"]))
			for page_index in range(len(map_events["events"][map_event_index]["pages"] if map_events["events"][map_event_index] else []))
			for event_index in range(len(map_events["events"][map_event_index]["pages"][page_index]["list"]))
			for message_path in RPGMakerMVData.event(map_events["events"][map_event_index]["pages"][page_index]["list"][event_index], f"$.events[{map_event_index}].pages[{page_index}].list[{event_index}]", events_code)
		]

		return messages

	@staticmethod
	def common_events(events: list, events_code: list[int]) -> list[str]:
		messages: list[str] = [
			message_path
			for common_event_index in range(len(events))
			for event_index in range(len(events[common_event_index]["list"] if events[common_event_index] else []))
			for message_path in RPGMakerMVData.event(events[common_event_index]["list"][event_index], f"$[{common_event_index}].list[{event_index}]", events_code)
		]

		return messages

	@staticmethod
	def system_json(system_json: dict) -> list[str]:
		messages: list[str] = []

		# Outside
		messages.append("$.currencyUnit")
		messages.append("$.gameTitle")

		# Add items to messages
		messages += [
			f"$.{items_key}[{item_index}]"
			for items_key in RPGMakerMVData.SystemJSONItemsKeys
			for item_index in range(len(system_json[items_key]))
			if system_json[items_key][item_index]
		]

		# Terms
		messages += [
			f"$.terms.{term_key}.{('[%s]' if isinstance(system_json['terms'][term_key], list) else '%s') % item_key}"
			for term_key in system_json["terms"]
			for item_key in (system_json["terms"][term_key] if isinstance(system_json["terms"][term_key], dict) else range(len(system_json["terms"][term_key])))
			if system_json["terms"][term_key][item_key]
		]

		return messages
