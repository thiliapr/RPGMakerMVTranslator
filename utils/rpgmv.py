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
                "path": jsonpath.concat_path(parent_path, "$.parameters[0]"),
                "message": event["parameters"][0]
            }

            # With Name
            context: str = message["message"]
            if context.strip().startswith("\\n<"):
                message["speaker"] = context[context.find("<") + 1:context.find(">")]
                message["message"] = context[context.find(">") + 1:]

            # Add message info to messages
            messages.append(message)

        # Unknown Event
        return messages

    @staticmethod
    def items(items: list, **kwargs) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = [
            {"path": path, "message": jsonpath.get(items, path)}
            for item_index, item in enumerate(items)
            for path in (
                [f"$[{item_index}].{key}" for key in RPGMakerMVData.ItemTextsKeys if item.get(key)]
                if item else []
            )
        ]

        return messages

    @staticmethod
    def troops(troops: list, **kwargs) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = RPGMakerMVData.items(troops)

        # Events
        messages += [
            message
            for troop_index, troop in enumerate(troops)
            for page_index, page in (enumerate(troop["pages"]) if troop else tuple())
            for event_index, event in enumerate(page["list"])
            for message in RPGMakerMVData.event(event, f"$[{troop_index}].pages[{page_index}].list[{event_index}]", **kwargs)
        ]

        return messages

    @staticmethod
    def map_events(map_events: dict, **kwargs) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = [
            message
            for map_event_index, map_event in enumerate(map_events["events"])
            for page_index, page in (enumerate(map_event["pages"]) if map_event else tuple())
            for event_index, event in enumerate(page["list"])
            for message in RPGMakerMVData.event(event, f"$.events[{map_event_index}].pages[{page_index}].list[{event_index}]", **kwargs)
        ]

        # Display Name
        if map_events["displayName"]:
            messages.append({"path": "$.displayName", "message": map_events["displayName"]})

        return messages

    @staticmethod
    def common_events(events: list, **kwargs) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = [
            message
            for common_event_index, common_event in enumerate(events)
            for event_index, event in (enumerate(common_event["list"]) if common_event else tuple())
            for message in RPGMakerMVData.event(event, f"$[{common_event_index}].list[{event_index}]")
        ]

        return messages

    @staticmethod
    def system_json(system_json: dict, **kwargs) -> list[dict[str, Any]]:
        paths: list[str] = [f"$.{k}" for k in RPGMakerMVData.SystemJSONKeys]

        # Terms
        paths += [
            f"$.terms.messages.{msg_key}"
            for msg_key, msg in system_json["terms"]["messages"].items()
            if msg
        ]

        return [{"path": path, "message": jsonpath.get(system_json, path)} for path in paths]

    @staticmethod
    def extract_data(filename: str, data: jsonpath.JSONObject, **kwargs) -> list[dict[str, Any]]:
        """
        {"message" ..., "path": ..., "speaker": ...}
        """

        extract_func: Callable[[jsonpath.JSONObject, ...], list[dict[str, Any]]]

        # Setting Extract Function
        if filename == "CommonEvents.json":
            extract_func = RPGMakerMVData.common_events
        elif filename == "Animations.json":
            return []
        elif filename == "System.json":
            extract_func = RPGMakerMVData.system_json
        elif filename == "Troops.json":
            extract_func = RPGMakerMVData.troops
        elif filename.startswith("Map") and filename[3:-5].isdecimal():
            extract_func = RPGMakerMVData.map_events
        elif isinstance(data, list):
            extract_func = RPGMakerMVData.items
        else:
            return []

        # Run
        return extract_func(data, **kwargs)
