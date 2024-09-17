import re
import sys
from typing import List, Dict, Tuple

def read_thunderbird_filters(file_path: str) -> str:
    """Read the contents of a Thunderbird filter file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: File '{file_path}' not found.")
    except IOError as e:
        raise IOError(f"Error reading file '{file_path}': {e}")

def parse_thunderbird_filters(thunderbird_filters: str) -> List[Dict[str, str]]:
    """Parse Thunderbird filters into a list of dictionaries."""
    filters = []
    current_filter = {}
    for line in thunderbird_filters.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('name='):
            if current_filter and 'name' in current_filter and 'condition' in current_filter:
                filters.append(current_filter)
            current_filter = {}
        if '=' in line:
            key, value = line.split('=', 1)
            value = value.strip('"')
            if key == 'action':
                if 'actions' not in current_filter:
                    current_filter['actions'] = []
                current_filter['actions'].append(value)
            elif key == 'name':
                current_filter['name'] = value
            else:
                current_filter[key] = value

    # Check that the current filter has a name and condition before appending
    if current_filter and 'name' in current_filter and 'condition' in current_filter:
        filters.append(current_filter)
        
    return filters


def clean_header(header: str) -> str:
    """Remove unnecessary escaping from the header."""
    # Only unescape inner quotes if they are double-escaped
    return header.replace('\\"', '"').strip('"')

def convert_condition(condition: str) -> Tuple[str, List[str]]:
    """Convert a Thunderbird condition to Sieve format."""
    
    condition = condition.strip()
    if condition.startswith('OR '):
        operator = 'anyof'
        condition = condition[3:]
    elif condition.startswith('AND '):
        operator = 'allof'
        condition = condition[4:]
    else:
        operator = 'anyof'

    # Regex to match the parts, including escaped quotes
    parts = re.findall(r'\(([^,]+),\s*([^,]+),\s*(.+?)\)', condition)

    sieve_conditions = []
    for header, operation, value in parts:
        # Clean header and value
        header = clean_header(header)
        value = clean_header(value)
        
        if header == "to or cc":
            sieve_conditions.append(f'header :contains "to" "{value}"')
            sieve_conditions.append(f'header :contains "cc" "{value}"')
        elif operation == 'contains':
            sieve_conditions.append(f'header :contains "{header}" "{value}"')
        elif operation == "doesn't contain":
            sieve_conditions.append(f'not header :contains "{header}" "{value}"')

    return operator, sieve_conditions


def convert_to_sieve(thunderbird_filter: Dict[str, str]) -> str:
    """Convert a single Thunderbird filter to a Sieve rule."""
    name = thunderbird_filter.get('name', 'Unnamed Filter')
    condition = thunderbird_filter.get('condition', '')
    actions = []

    if 'actionValue' in thunderbird_filter:
        full_path = thunderbird_filter['actionValue']
        folder_match = re.search(r'INBOX/(.+)$', full_path)
        if folder_match:
            folder = folder_match.group(1)
            actions.append(f'\tfileinto "INBOX/{folder}";')

    if 'actions' in thunderbird_filter:
        if "Mark read" in thunderbird_filter['actions']:
            actions.append('\tsetflag "\\\\Seen";')
        if "Stop execution" in thunderbird_filter['actions']:
            actions.append('\tstop;')

    operator, sieve_conditions = convert_condition(condition)

    sieve_rule = f"# rule:[{name}]\n"
    sieve_rule += f"if {operator} (\n    "
    sieve_rule += ",\n    ".join(sieve_conditions)
    sieve_rule += "\n)\n{\n" + "\n".join(actions) + "\n}"

    return sieve_rule

def thunderbird_to_sieve(thunderbird_filters: str) -> str:
    """Convert Thunderbird filters to Sieve rules."""
    filters = parse_thunderbird_filters(thunderbird_filters)
    sieve_rules = []
    for filter in filters:
        rule = convert_to_sieve(filter)
        sieve_rules.append(rule)
    return 'require ["fileinto", "imap4flags"];\n\n' + "\n\n".join(sieve_rules)

def main():
    """Main function to handle command-line arguments and file operations."""
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python script.py path/to/msgFilterRules.dat [output_file.sieve]")
        sys.exit(1)

    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2] if len(sys.argv) == 3 else "roundcube.sieve"

    try:
        thunderbird_filters = read_thunderbird_filters(input_file_path)
        sieve_rules = thunderbird_to_sieve(thunderbird_filters)

        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(sieve_rules)

        print(f"Sieve rules have been successfully written to {output_file_path}")
        print(f"Total rules converted: {sieve_rules.count('# rule:')}")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
