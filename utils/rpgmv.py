from tprtools import jsonpath


class RPGMakerMVData:
	@staticmethod
	def event(event: jsonpath.JSONObject, parent_path: str, events_code: list[int]) -> list[str] | None:
		if event["code"] not in events_code:
			return
		# Choices
		elif event["code"] == 102:
			return [jsonpath.concat_path(parent_path, f"$.parameters[0][{i}]") for i in range(len(event["parameters"][0])) if event["parameters"][0][i]]
		# Comment
		elif event["code"] == 108:
			return [jsonpath.concat_path(parent_path, "$.parameters[0]")] if event["parameters"][0] else []
		# Text
		elif event["code"] == 401:
			return [jsonpath.concat_path(parent_path, "$.parameters[0]")] if event["parameters"][0] else []

	@staticmethod
	def items(items: list, without_name: bool = True) -> list[str]:
		messages: list[str] = []
		for item_index in range(len(items)):
			item = items[item_index]
			if item is None:
				continue

			for key in ("description", "message1", "message2", "message3", "message4"):
				if item.get(key):
					messages.append(f"$[{item_index}].{key}")

			if not without_name and item.get("name"):
				messages.append(f"$[{item_index}].name")

		return messages

	@staticmethod
	def map_events(map_events: dict, events_code: list[int]) -> list[str]:
		messages: list[str] = []

		for map_event_index in range(len(map_events["events"])):
			map_event = map_events["events"][map_event_index]
			if map_event is None:
				continue

			for page_index in range(len(map_event["pages"])):
				page = map_event["pages"][page_index]

				for event_index in range(len(page["list"])):
					event = page["list"][event_index]

					event_messages = RPGMakerMVData.event(event, f"$.events[{map_event_index}].pages[{page_index}].list[{event_index}]", events_code)
					if event_messages:
						messages += event_messages

		return messages

	@staticmethod
	def common_events(events: list, events_code: list[int]) -> list[str]:
		messages: list[str] = []
		for common_event_index in range(len(events)):
			common_event = events[common_event_index]
			if common_event is None:
				continue

			for event_index in range(len(common_event["list"])):
				event = common_event["list"][event_index]

				message = RPGMakerMVData.event(event, f"$[{common_event_index}].list[{event_index}]", events_code)
				if message:
					messages += message

		return messages
