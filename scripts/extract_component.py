from bs4 import BeautifulSoup
from bs4.element import Tag


def query_selector_all_reverse_bfs(root, selector):
    queue = [{"element": root, "level": 0}]
    grouped_by_level = []
    result = []

    while queue:
        queue_item = queue.pop(0)
        element, level = queue_item["element"], queue_item["level"]

        if len(grouped_by_level) <= level:
            grouped_by_level.append([])
        grouped_by_level[level].append(element)

        if isinstance(element, Tag):
            for child in element.children:
                queue.append({"element": child, "level": level + 1})

    grouped_by_level.reverse()
    for level in grouped_by_level:
        for element in level:
            if element.name in selector:
                result.append(element)

    return result


conditions = [
    {
        "type": "input_radio",
        "test": lambda element: len(element.select('input[type="radio"]')) >= 2,
    },
    {
        "type": "button",
        "test": lambda element: element.name == "button"
        and element.get("type") == "button",
    },
    {
        "type": "input_button",
        "test": lambda element: element.name == "div"
        and element.select_one('input[type="button"]')
        and element.select_one("label"),
    },
    {
        "type": "link",
        "test": lambda element: element.name == "a",
    },
    {
        "type": "list",
        "test": lambda element: element.name == "div"
        and (element.select_one("ul") or element.select_one("ol")),
    },
]


def get_condition(element):
    for condition in conditions:
        if condition["test"](element):
            return condition["type"]
    return None


def extract_action_components(root):
    components = []
    candidate_elements = query_selector_all_reverse_bfs(root, ["div", "button"])
    added_i_values = set()

    for i in range(len(candidate_elements)):
        condition_type = get_condition(candidate_elements[i])
        if condition_type:
            current_i_value = candidate_elements[i].get("i")

            if current_i_value in added_i_values:
                continue

            descendants = candidate_elements[i].select("*")
            if any(descendant.get("i") in added_i_values for descendant in descendants):
                continue

            if current_i_value:
                components.append(
                    {
                        "html": str(candidate_elements[i]),
                        "type": condition_type,
                        "i": current_i_value,
                    }
                )
                added_i_values.add(current_i_value)

    return components
