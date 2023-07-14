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
        "type": "button",
        "test": lambda element: element.name == "button"
        #and element.get("type") == "button",
    },

    {
        "type": "link",
        "test": lambda element: element.name == "a"
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
    {
        "type": "input_radio",
        "test": lambda element: element.name == "input" and element.get("type") == "radio",
    },
    {
        "type": "input_button",
        "test": lambda element: element.name == "input" and element.get("type") == "button",
    },
    {
        "type": "input_checkbox",
        "test": lambda element: element.name == "input" and element.get("type") == "checkbox",
    },
    {
        "type": "input_text",
        "test": lambda element: element.name == "input" and element.get("type") == "text",
    },
    {
        "type": "input_range",
        "test": lambda element: element.name == "input" and element.get("type") == "range",
    },
    {
        "type": "paragraph",
        "test": lambda element: element.name == "p",
    },
    {
        "type": "Unknown",
        "test": lambda element: 1==1, # For merged components, we don't know what it is, so just use Unknown
    }
    
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


threshold = 10
# Used for merged components. Set the threshold above.
def traverse_element2(element, s, action_components:set):
    if not isinstance(element, Tag):
        return
    tmp_leave_node_set = set()
    traverse_element(element,tmp_leave_node_set)
    inter_set = tmp_leave_node_set.intersection(action_components)
    if len(inter_set) == 0:
        return
    if len(inter_set) <= threshold:
        s.append(element)
        return 
    
    for child in element.children:
        traverse_element2(child,s, action_components)  

def extract_action_components(root):
    

    # get list elements
    tmp_root = copy.deepcopy(root)
    list_elements = BeautifulSoup.find_all(tmp_root, lambda tag: tag.name in ["ul", "ol"])
    added_i_values = set()
    for i in list_elements:
        traverse_element(i, added_i_values)

    # get table elements
    table_elements = BeautifulSoup.find_all(tmp_root, lambda tag: tag.name in ["table"])
    for i in table_elements:
        traverse_element(i, added_i_values)

    # get fieldset elements
    fieldset_elements = BeautifulSoup.find_all(tmp_root, lambda tag: tag.name in ["fieldset"])
    for i in fieldset_elements:
        traverse_element(i, added_i_values)
    
    # find all paragraph elements with interactive elements
    paragraph_elements = BeautifulSoup.find_all(tmp_root, lambda tag: tag.name in ["p"])
    paragraph_with_active_elements = []
    for i in paragraph_elements:
        tmp_len_rec = len(added_i_values)
        traverse_element(i, added_i_values)
        if len(added_i_values) > tmp_len_rec:
            paragraph_with_active_elements.append(i)
    
    # get all other interactive elements
    interactive_elements = BeautifulSoup.find_all(tmp_root, lambda tag: tag.name in ["button", "input", "a", "select", "textarea"])
    with open("interactive_elements.txt", "w") as f:
        for i in interactive_elements:
            f.write(str(i.get("i")) + " ")


    # remove duplicated elements from interactive elements
    tmp_set = set(interactive_elements)
    for i in tmp_set:
        if i.get("i") in added_i_values:
            interactive_elements.remove(i)

    interactive_elements += list_elements
    interactive_elements += table_elements
    interactive_elements += fieldset_elements
    interactive_elements += paragraph_with_active_elements


    # merge components
    # For each element containing less than {threshold} action compenents, we try to merge them.

    merged_components = []
    action_components_i_attr = set([i.get("i") for i in interactive_elements])
    traverse_element2(tmp_root, merged_components, action_components_i_attr)
            
    components = []

    for element in merged_components:
        condition_type = get_condition(element)
        if condition_type:
            components.append(
                {
                    "html": str(element),
                    "type": condition_type,
                    "i": element.get("i"),
                }
            )



    return components

