import datetime
import json
import os
import time

import htmlmin
from bs4 import BeautifulSoup
from html_parser import simplify_html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

url = "https://www.greyhound.com/"

options = Options()
options.headless = False
options.add_argument("--window-size=390,844")
options.add_argument(
    "user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
)

webdriver_service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=webdriver_service, options=options)

driver.get(url)


# action


time.sleep(3)
button = driver.find_element(By.XPATH, '//*[@id="dateInput-from"]')
button.click()


time.sleep(3)

hidden_element_ids = []
id_counter = 0

# driver.implicitly_wait(10)

elements = driver.find_elements(By.XPATH, "//*")
for el in elements:
    driver.execute_script(f"arguments[0].setAttribute('i', '{id_counter}')", el)
    width_in_pixels = el.size["width"]
    is_hidden = (
        el.value_of_css_property("display") == "none"
        or el.value_of_css_property("visibility") == "hidden"
        # or width_in_pixels <= 5 # do not use this when debugging OTZ
    )

    if is_hidden:
        hidden_element_ids.append(str(id_counter))
    id_counter += 1

html = driver.page_source
simplified_html, components = simplify_html(html, hidden_element_ids)

minified_html = htmlmin.minify(
    str(simplified_html),
    remove_comments=True,
    remove_empty_space=True,
    reduce_empty_attributes=True,
)

beautified_html = BeautifulSoup(minified_html, "html.parser").prettify()

now = datetime.datetime.now()
time_str = now.strftime("%y%m%d_%H%M%S")

current_dir = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(current_dir, f"../output/output_{time_str}")
os.makedirs(output_dir, exist_ok=True)

output_html_file_name = f"body_{time_str}.html"
output_html_file = os.path.join(output_dir, output_html_file_name)

with open(output_html_file, "w") as html_file:
    html_file.write(beautified_html)

for component in components:
    beautified_component_html = BeautifulSoup(
        component["html"], "html.parser"
    ).prettify()
    output_component_file_name = f"component_{component['i']}_{component['type']}.html"
    output_component_file = os.path.join(output_dir, output_component_file_name)
    with open(output_component_file, "w") as component_file:
        component_file.write(beautified_component_html)

input("Press Enter to quit...")
