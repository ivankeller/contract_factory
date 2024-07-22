import re
import logging
import fitz
from typing import List


logger = logging.getLogger('the_logger')
logger.setLevel(logging.DEBUG)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Set the level for the console handler to DEBUG

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(console_handler)

MISSING_PLACEHOLDER_VALUE = " " * 8

def extract_placeholders(input_string: str) -> List[str]:
    """Return the list of strings found between curly braces in given input string.

    Example:
    --------
    >>> extract_placeholders("This is a {simple} nice {example}.")
    ['simple', 'example']
    
    """
    return re.findall(r'\{([^}]+)\}', input_string)

def format_employee(employee: dict, format_specs: dict) -> dict:
    """Format some values of employee.
    
    Example:
    --------
    >>> employee = {'name': 'Wiliam', 'brut_day': 12.3456}
    >>> format_employee(employee=employee, format_specs={'brut_day': '.2f'})
    {'name': 'Wiliam', 'brut_day': '12.35'}

    """
    employee_out = employee.copy()
    for attribute, format_str in format_specs.items():
        if attribute in employee_out:
            employee_out[attribute] = f"{{:{format_str}}}".format(employee_out[attribute])
    return employee_out

def define_compound_placeholders(employee: dict) -> dict:
    """Add value for compound placeholders.
    
    Some placeholders in the template are composed from elemental atttributes of
    the employee data, like for example 'first_name name' wich is the concatenation
    of 'first_name' and 'name'.

    """
    employee['first_name name'] = f"{employee['first_name']} {employee['name']}"
    employee['street, number'] = f"{employee['street']}, {employee['number']}"
    return employee



def create_contract_for_employee(employee: dict, contract: fitz.Document):
    offset = 8 
    # iterate on each page of the contract template
    for page_num in range(contract.page_count):
        logger.info(f"Processing page {page_num + 1}/{contract.page_count}")
        page = contract.load_page(page_num)
        text = page.get_text()
        placeholders = extract_placeholders(text)
        # if a placeholder is missing in employees' attributes then add it with a default value
        missing_placeholders = set(placeholders) - set(employee.keys())
        if missing_placeholders:
            logger.warning(
                (f"Missing field in employee listing for placeholders {missing_placeholders}",
                f"replacing by default value: '{MISSING_PLACEHOLDER_VALUE}'")
            )
            for missing_placeholder in missing_placeholders:
                employee[missing_placeholder] = MISSING_PLACEHOLDER_VALUE
        # iterate on placeholders and replace by the corresponding employee attribute
        placeholders = placeholders[::-1]
        for placeholder in placeholders:
            logger.debug(f'searching for placeholder {{{placeholder}}}')
            search_text = f'{{{placeholder}}}'
            text_instances = page.search_for(search_text)
            replacement_text = str(employee[placeholder])
            for inst in text_instances:
                # Get font properties of the text instance
                font_info = page.get_text("dict", clip=inst)["blocks"][0]["lines"][0]["spans"][0]
                font_size = font_info["size"]
                font_name = font_info["font"]
                font_color = font_info["color"]
                page.add_redact_annot(inst, fill=(1, 1, 1))
                page.apply_redactions()
                logger.debug(f'replacing by {replacement_text}')
                x0, y0, x1, y1 = inst.irect
                x0 += offset
                y0 += offset
                try:
                    page.insert_text((x0, y0), replacement_text, fontname=font_name, fontsize=font_size, color=font_color, overlay=True)
                except Exception as e:
                    logger.warning(f"Font '{font_name}' not found. Using default font. Error: {e}")
                    page.insert_text((x0, y0), replacement_text, fontsize=font_size-1, color=font_color, overlay=True)

    
if __name__ == "__main__":
    import doctest
    doctest.testmod()