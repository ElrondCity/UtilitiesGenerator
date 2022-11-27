'''
This script reads the ABI file given as input and generates a Markdown file with the ABI documentation.

The ABI file is expected to be in JSON format. The Markdown file is generated in the same directory as the ABI file.

Example usage:
    python3 main.py /path/to/abi/file.json

'''

import json
import os
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_doc.py <path_to_json>")
        return

    with open(sys.argv[1]) as f:
        data = json.load(f)

    # Create the markdown file
    with open("contract_doc.md", "w") as f:
        f.write("# " + data["name"])
        f.write('\n')
        f.write("#### " + data["docs"][0])
        f.write('\n\n')

        # Write the endpoints
        f.write(" ## Endpoints ")
        f.write('\n')
        # Start with onlyOwner endpoints
        f.write(" ### onlyOwner ")
        f.write('\n')
        for endpoint in data["endpoints"]:
            if "onlyOwner" in endpoint and endpoint["onlyOwner"]:
                endpoint_str = "- **" + endpoint["name"] + "**("
                for i, input in enumerate(endpoint["inputs"]):
                    endpoint_str += input["name"] + ": `" + input["type"] + "`"
                    if i != len(endpoint["inputs"]) - 1:
                        endpoint_str += ", "
                endpoint_str += ")"
                f.write(endpoint_str)
                f.write('\n')

        f.write('\n')

        # Then write the public endpoints
        f.write(" ### Public ")
        f.write('\n')
        for endpoint in data["endpoints"]:
            if "onlyOwner" not in endpoint or not endpoint["onlyOwner"]:
                endpoint_str = "- **" + endpoint["name"] + "**("
                for i, input in enumerate(endpoint["inputs"]):
                    endpoint_str += input["name"] + ": `" + input["type"] + "`"
                    if i != len(endpoint["inputs"]) - 1:
                        endpoint_str += ", "
                endpoint_str += ")"
                f.write(endpoint_str)
                f.write('\n')

        f.write('\n')

        # Then write the readonly endpoints
        f.write(" ### Readonly ")
        f.write('\n')
        for endpoint in data["endpoints"]:
            if endpoint["mutability"] == "readonly":
                endpoint_str = "- **" + endpoint["name"] + "**("
                for i, input in enumerate(endpoint["inputs"]):
                    endpoint_str += input["name"] + ": `" + input["type"] + "`"
                    if i != len(endpoint["inputs"]) - 1:
                        endpoint_str += ", "
                endpoint_str += ")"
                if len(endpoint["outputs"]) > 0:
                    endpoint_str += " -> `"
                    for i, output in enumerate(endpoint["outputs"]):
                        endpoint_str += output["type"]
                        if i != len(endpoint["outputs"]) - 1:
                            endpoint_str += ", "
                    endpoint_str += "`"
                f.write(endpoint_str)
                f.write('\n')

if __name__ == "__main__":
    main()