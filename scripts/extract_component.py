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
                if child != "\n":
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
        "test": lambda element: element.name == "a"
        # or (element.name == "div" and element.select_one("a") ),
    },
    {
        "type": "list",
        "test": lambda element: element.name == "div"
        and (element.select_one("ul") or element.select_one("ol")),
    }
    ,
    {
        "type": "input_default",
        "test": lambda element: element.name == "input" 
        and element.has_attr('type') == False,
    }
    ,
    
]


def get_condition(element):
    for condition in conditions:
        if condition["test"](element):
            return condition["type"]
    return None

import copy


def traverse_element(element, s):
    if not isinstance(element, Tag):
    # if not element.has_attr('i'):
        return
    s.add(element.get("i"))
    for child in element.children:
        traverse_element(child,s)  


def extract_action_components(root):
    

    # get list elements
    tmp_root = copy.deepcopy(root)
    list_elements = BeautifulSoup.find_all(tmp_root, lambda tag: tag.name in ["ul", "ol"])
    added_i_values = set()
    for i in list_elements:
        traverse_element(i, added_i_values)

    # get all other interactive elements
    interactive_elements = BeautifulSoup.find_all(tmp_root, lambda tag: tag.name in ["button", "input", "a", "select", "textarea"])

    # remove list elements from interactive elements
    tmp_set = set(interactive_elements)
    for i in tmp_set:
        if i.get("i") in added_i_values:
            interactive_elements.remove(i)

        
            
    components = []
    for element in interactive_elements:
        condition_type = get_condition(element)
        if condition_type:
            components.append(
                {
                    "html": str(element),
                    "type": condition_type,
                    "i": element.get("i"),
                }
            )

    for element in list_elements:
    
        components.append(
            {
                "html": str(element),
                "type": "list",
                "i": element.get("i"),
            }
        )
    
    return components

# def extract_action_components(root):
#     components = []
#     candidate_elements = query_selector_all_reverse_bfs(root, ["div", "button"])
#     added_i_values = set()

#     for i in range(len(candidate_elements)):
#         condition_type = get_condition(candidate_elements[i])
#         if condition_type:
#             current_i_value = candidate_elements[i].get("i")

#             if current_i_value in added_i_values:
#                 continue

#             descendants = candidate_elements[i].select("*")
#             if any(descendant.get("i") in added_i_values for descendant in descendants):
#                 continue

#             if current_i_value:
#                 components.append(
#                     {
#                         "html": str(candidate_elements[i]),
#                         "type": condition_type,
#                         "i": current_i_value,
#                     }
#                 )
#                 added_i_values.add(current_i_value)

#     return components
