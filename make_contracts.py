
import io
import os
import json
import sys
import pandas as pd
import fitz  # PyMuPDF
import datetime as dt
import helpers
import logging
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


logger = logging.getLogger('the_logger')
logger.setLevel(logging.DEBUG)

def main(config_path):

    # read configuration
    with open(config_path, 'r') as f:
        config = json.load(f)
    output_dir = config['output directory path']
    excel_file_path = config['EXCEL employees data path']
    template_path = config['PDF contract template path']
    format_employee_specs = config['format employee specs']

    # Load the employees data from Excel file into a DataFrame
    df_employees = pd.read_excel(excel_file_path)

    # iterate on each employee
    for index, employee_row in df_employees.iterrows():
        # we need to re-read the template at each iteration
        # todo: find a method allowing reading only once
        contract_template = fitz.open(template_path)
        logger.info(f"Processing employee {index + 1}/{len(df_employees)}")
        employee = employee_row.to_dict()
        # use today date as contract date
        today = dt.datetime.now()
        employee['date'] = today.strftime("%Y-%m-%d")
        # format placeholers' values
        employee = helpers.format_employee(employee, format_employee_specs)
        employee = helpers.define_compound_placeholders(employee)
        # replace placeholders in the contract by the employee attributes
        helpers.create_contract_for_employee(employee, contract_template)
        # Save the result
        contract_filename = f"contract_{index + 1}_{employee['name']}.pdf"
        output_path = os.path.join(output_dir, contract_filename)
        contract_template.save(output_path)
        logger.info(f"saved to {output_path}")


if __name__ == "__main__":
    config_path = sys.argv[1]
    main(config_path)