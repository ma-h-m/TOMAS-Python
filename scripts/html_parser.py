from bs4 import BeautifulSoup, NavigableString
from extract_component import extract_action_components


def remove_attributes(element, attributes_to_keep, exclude_tags):
    if element.name not in exclude_tags:
        attrs = dict(element.attrs)
        for attr in attrs:
            if attr not in attributes_to_keep:
                del element.attrs[attr]

    for child in element.children:
        if child.name:
            remove_attributes(child, attributes_to_keep, exclude_tags)


def remove_specific_tags(soup, tag_names):
    for tag_name in tag_names:
        for tag in soup.find_all(tag_name):
            tag.decompose()


def contains_specific_tag(element, tags):
    return any(element.find(tag) for tag in tags)


def is_empty_element(element, include_tags):
    has_non_i_specific_attributes = any(attr != "i" for attr in element.attrs.keys())

    return (
        not contains_specific_tag(element, include_tags)
        and not element.get_text(strip=True)
        and not has_non_i_specific_attributes
    )


def remove_empty_elements(element, include_tags):
    children = [child for child in element.children if child.name is not None]
    for child in children:
        if is_empty_element(child, include_tags):
            child.decompose()
        else:
            remove_empty_elements(child, include_tags)


def simplify_nested_structure(element, target_tags, avoid_tags):
    current_element = element
    while (
        current_element.name in target_tags
        and len(current_element.contents) == 1
        and not contains_specific_tag(current_element, avoid_tags)
    ):
        child = current_element.contents[0]
        if isinstance(child, NavigableString) or len(child.contents) != 1:
            break
        child.extract()
        current_element.append(child.contents[0])

    for child in current_element.contents:
        if not isinstance(child, NavigableString):
            simplify_nested_structure(child, target_tags, avoid_tags)


def simplify_html(html, hidden_element_ids):
    soup = BeautifulSoup(html, "html.parser")
    for hidden_id in hidden_element_ids:
        hidden_element = soup.find(attrs={"i": hidden_id})
        if hidden_element:
            hidden_element.decompose()
    body = soup.body
    remove_specific_tags(body, ["script", "style", "svg", "path", "link", "meta"])
    remove_attributes(body, ["i", "href"], ["input", "button", "label"])
    remove_attributes(
        body,
        [
            "i",
            "href",
            "type",
            "aria-label",
            "role",
            "checked",
            "value",
            "aria-expanded",
            "aria-controls",
        ],
        [],
    )

    remove_empty_elements(body, ["input", "button", "label", "a"])
    simplify_nested_structure(body, ["div", "span"], ["button", "input", "a", "select", "textarea"])
    components = extract_action_components(body)
    return str(body), components
