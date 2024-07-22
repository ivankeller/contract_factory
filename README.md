# Contract Factory

Create the contracts for all the employees given:
- a list of employees and their description in an Excel file
- a template of the contract with place holders for the employee attributes as a PDF file

## Install for the first time

In a terminal, execute the command:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the program

### Configuration

Edit the file config.json by specifying the inputs files according to your needs:
- Excel file path for the list of employees
- PDF file path of the contract template

### Run

Activate the virtual environment if it's not activated yet:
```bash
source .venv/bin/activate
```

Execute the program: 

```bash
python make_contracts.py config.json
```

## Run the tests

In a terminal, execute the command:
```bash
python helpers.py -v
```

