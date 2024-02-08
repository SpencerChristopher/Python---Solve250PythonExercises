import os
import json
import argparse

def fetch_resource_files(extraction_path, channel):
    try:
        resource_files = []
        for root, dirs, files in os.walk(extraction_path):
            for file in files:
                if file.endswith(".json"):
                    if channel.lower() == 'global' and 'resources' in root:
                        resource_files.append(os.path.join(root, file))
                    elif f"resources_{channel.upper()}" in root:
                        resource_files.append(os.path.join(root, file))
        return resource_files
    except Exception as e:
        print(f"Error fetching resource files: {e}")
        return []

def extract_target_fields(file_path):
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            target_field = data.get('target_field', '')
            source_fields = data.get('source_field', [])
            return target_field, source_fields
    except Exception as e:
        print(f"Error extracting target fields from {file_path}: {e}")
        return None, None

def get_channel_files(extraction_path, channel):
    if channel.lower() == 'global':
        return fetch_resource_files(extraction_path, 'global')
    else:
        return fetch_resource_files(extraction_path, channel)

def generate_json_object(title, source_fields, target_field, file_name):
    json_object = {
        "title": title,
        "source_fields": source_fields,
        "target_field": target_field,
        "file_name": file_name,
    }
    return {target_field: {title: json_object}}

def find_target_field(extraction_path, target_field, channel, output_to_terminal=True):
    result = {}
    channels = channel.split(',')
    for current_channel in channels:
        resource_files = get_channel_files(extraction_path, current_channel)

        if not resource_files:
            print(f"No resource files found for channel: {current_channel}")
            continue

        for file_path in resource_files:
            current_target, source_fields = extract_target_fields(file_path)
            if current_target == target_field:
                title = os.path.splitext(os.path.basename(file_path))[0]
                result.update(generate_json_object(title, source_fields, target_field, file_path))

    if not result and output_to_terminal:
        print(f"No matching files found for target field: {target_field}")
        exit()

    if output_to_terminal:
        print(json.dumps(result, indent=4))
    else:
        try:
            with open(f'target_fields_mapping_{channel}.json', 'w') as output_json:
                json.dump(result, output_json, indent=4)
            print(f"Audit completed. Check 'target_fields_mapping_{channel}.json' for the results.")
        except Exception as e:
            print(f"Error writing to file: {e}")

def audit_target_fields(extraction_path, channel, output_to_terminal=True):
    result = {}
    channels = channel.split(',')
    for current_channel in channels:
        resource_files = get_channel_files(extraction_path, current_channel)

        if not resource_files:
            print(f"No resource files found for channel: {current_channel}")
            continue

        for file_path in resource_files:
            current_target, source_fields = extract_target_fields(file_path)
            if current_target:
                title = os.path.splitext(os.path.basename(file_path))[0]
                result.update(generate_json_object(title, source_fields, current_target, file_path))

    if not result and output_to_terminal:
        print("No matching files found.")
        exit()

    if output_to_terminal:
        print(json.dumps(result, indent=4))
    else:
        try:
            with open(f'target_fields_mapping_{channel}.json', 'w') as output_json:
                json.dump(result, output_json, indent=4)
            print(f"Audit completed. Check 'target_fields_mapping_{channel}.json' for the results.")
        except Exception as e:
            print(f"Error writing to file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Script for extracting and auditing target fields in an extraction directory.")
    parser.add_argument("--find", type=str, help="Find a target field in the extraction directory. Example: --find prod_feat1234")
    parser.add_argument("--audit", action="store_true", help="Create a file with all target fields and their associated files and source fields.")
    parser.add_argument("--channel", type=str, help="Specify the channel or channels to access. Multiple channels should be comma-separated. Example: --channel DE,ES")
    parser.add_argument("--output", choices=["terminal", "file"], default="terminal", help="Specify whether to output to terminal or file. Default: terminal")
    args = parser.parse_args()

    extraction_path = '.'  # Set to the current working directory

    target_field = args.find
    channels = args.channel.split(',') if args.channel else ['global']
    output_to_terminal = args.output.lower() == "terminal"

    found_target = False
    for channel in channels:
        try:
            result = find_target_field(extraction_path, target_field, channel, output_to_terminal)
            found_target = found_target or bool(result)
        except Exception as e:
            print(f"Error: {e}")

    if not found_target and output_to_terminal:
        print(f"No matching files found for target field: {target_field}")

    elif args.audit:
        for channel in channels:
            try:
                audit_target_fields(extraction_path, channel, output_to_terminal)
            except Exception as e:
                print(f"Error: {e}")

if __name__ == '__main__':
    main()
