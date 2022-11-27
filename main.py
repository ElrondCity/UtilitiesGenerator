'''
This script reads the ABI file given as input and generates a Markdown file with the ABI documentation, and a interaction.sh script to interact with the contract.

The ABI file is expected to be in JSON format. The Markdown file is generated in the same directory as the script.

Example usage:
    python3 main.py /path/to/abi/file.json

'''

import json
import os
import sys

def generate_markdown(data):
    # Create the markdown file
    with open("contract_doc.md", "w") as f:
        f.write("# " + data["name"])
        f.write('\n')
        if ("docs" in data):
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

        # Then write the public and not readonly endpoints
        f.write(" ### Public ")
        f.write('\n')
        for endpoint in data["endpoints"]:
            if ("onlyOwner" not in endpoint or not endpoint["onlyOwner"]) and endpoint["mutability"] != "readonly":
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

def generate_interaction_script(data):
    # Create the interaction script
    with open("interaction.sh", "w") as f:
        f.write("# Replace the following with your own values\n")
        f.write("ADDRESS=\"\erd1qqq...xxx\"\n")
        f.write("OWNER=\"\erd1...xxx\"\n")
        f.write("# Place your keystore file in the same directory as this script and replace the following with the name of the file\n")
        f.write("# Optionally, you can also put your password in the .passfile in the same directory as this script (if not, you will be prompted for the password)\n")
        f.write("PRIVATE_KEY=\"(--keyfile=erd1...xxx.json --passfile=.passfile)\"\n")
        f.write("PROXY=https://devnet-api.elrond.com\n")
        f.write("CHAIN_ID=D\n")
        f.write("\n")

        # Deploy
        contract_name = data["buildInfo"]["contractCrate"]["name"]

        f.write("# Standard deploy command. Provide any constructor arguments as needed (e.g deploy 12 TOKEN-123456). Numbers are automatically scaled to 18 decimals. (e.g. 12 -> 12000000000000000000)\n")
        f.write("deploy() {\n")
        f.write("    erdpy contract build\n")
        deploy_str = "    erdpy contract deploy --bytecode=\"../output/" + contract_name + ".wasm\" --recall-nonce ${PRIVATE_KEY} --gas-limit=500000000 --proxy=${PROXY} --chain=${CHAIN_ID} --send --outfile=\"deploy.interaction.json\""
        if (data["constructor"]["inputs"]):
            deploy_str += " --arguments "
            for i, input in enumerate(data["constructor"]["inputs"]):
                if input["type"] == "bytes" or input["type"] == "string" or input["type"] == "TokenIdentifier":
                    deploy_str += "str:${" + str(i) + "} "
                elif input["type"] == "BigUint" or input["type"] == "u64" or input["type"] == "u32" or input["type"] == "u16" or input["type"] == "u8":
                    deploy_str += "$(echo \"scale=0; (${" + str(i) + "}*10^18)/1\" | bc -l) "
                else:
                    deploy_str += "${" + str(i) + "} "
            deploy_str += "\n"
        f.write(deploy_str)
        f.write("    echo \"Deployed contract at address: $(cat deploy.interaction.json | jq -r '.emitted_tx.contract_address')\"\n")
        f.write("    echo \"Pleade update the ADDRESS variable in this script with the address of the deployed contract, then run 'source interaction.sh' to update the environment variables.\"\n")
        f.write("}\n\n")

        # Upgrade
        f.write("# Standard upgrade command. Provide any constructor arguments as needed (e.g upgrade 12 TOKEN-123). Numbers are automatically scaled to 18 decimals. (e.g. 12 -> 12000000000000000000)\n")
        f.write("upgrade() {\n")
        upgrade_str = "    erdpy contract upgrade ${ADDRESS} --bytecode output/" + contract_name + ".wasm --recall-nonce ${PRIVATE_KEY} --gas-limit=500000000 --proxy=${PROXY} --chain=${CHAIN_ID} --send"
        if (data["constructor"]["inputs"]):
            upgrade_str += " --arguments "
            for i, input in enumerate(data["constructor"]["inputs"]):
                if input["type"] == "bytes" or input["type"] == "string" or input["type"] == "TokenIdentifier":
                    upgrade_str += "str:${" + str(i) + "} "
                elif input["type"] == "BigUint" or input["type"] == "u64" or input["type"] == "u32" or input["type"] == "u16" or input["type"] == "u8":
                    upgrade_str += "$(echo \"scale=0; (${" + str(i) + "}*10^18)/1\" | bc -l) "
                else:
                    upgrade_str += "${" + str(i) + "} "
            upgrade_str += "\n"
        f.write(upgrade_str)
        f.write("}\n\n")

        tab_str = "    "

        # Call endpoints
        for endpoint in data["endpoints"]:
            if endpoint["mutability"] == "readonly":
                continue
            f.write("# " + endpoint["name"] + " endpoint call command. Provide any arguments as needed\n")
            f.write(endpoint["name"] + "() {\n")
            call_str = "    erdpy contract call ${ADDRESS} \\\n"
            call_str += tab_str + tab_str + "--function \"" + endpoint["name"] + "\" \\\n"
            call_str += tab_str + tab_str + "--recall-nonce ${PRIVATE_KEY} --gas-limit=500000000 --proxy=${PROXY} --chain=${CHAIN_ID} --send \\\n"
            if (endpoint["inputs"]):
                call_str += tab_str + tab_str + " --arguments "
                for i, input in enumerate(endpoint["inputs"]):
                    if input["type"] == "bytes" or input["type"] == "string" or input["type"] == "TokenIdentifier":
                        call_str += "str:${" + str(i) + "} "
                    elif input["type"] == "BigUint" or input["type"] == "u64" or input["type"] == "u32" or input["type"] == "u16" or input["type"] == "u8":
                        call_str += "$(echo \"scale=0; (${" + str(i) + "}*10^18)/1\" | bc -l) "
                    else:
                        call_str += "${" + str(i) + "} "
                call_str += "\n"
            f.write(call_str)
            f.write("}\n\n")




def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <path_to_json>")
        return

    with open(sys.argv[1]) as f:
        data = json.load(f)

    generate_markdown(data)
    generate_interaction_script(data)

    

if __name__ == "__main__":
    main()