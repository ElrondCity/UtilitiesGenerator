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
        f.write("# Replace the following with your own values (You need to run the script once to get the contract address)\n")
        f.write("ADDRESS=\"erd1qqq...xxx\"\n")
        f.write("OWNER=\"erd1...xxx\"\n")
        f.write("# Place your keystore file in the same directory as this script and replace the following with the name of the file\n")
        f.write("# Optionally, you can also put your password in the .passfile in the same directory as this script (if not, you will be prompted for the password)\n")
        f.write("PRIVATE_KEY=(--keyfile=erd1...xxx.json --passfile=.passfile)\n")
        f.write("PROXY=https://devnet-api.elrond.com\n")
        f.write("CHAIN_ID=D\n")
        f.write("\n")

        tab_str = "    "

        # Deploy
        contract_name = data["buildInfo"]["contractCrate"]["name"]

        f.write("# Standard deploy command. Provide any constructor arguments as needed (e.g deploy 12 TOKEN-123456). Numbers are automatically scaled to 18 decimals. (e.g. 12 -> 12000000000000000000)\n")
        f.write("deploy() {\n")
        if (data["constructor"]["inputs"]):
                args_str = "# Arguments: \n"
                for i, input in enumerate(data["constructor"]["inputs"]):
                    args_str += "ARG_" + str(i) + "="
                    if input["type"] == "bytes" or input["type"] == "string" or input["type"] == "TokenIdentifier":
                        args_str += "str:${" + str(i) + "} "
                    elif input["type"] == "BigUint" or input["type"] == "u64" or input["type"] == "u32" or input["type"] == "u16" or input["type"] == "u8":
                        args_str += "$(echo \"scale=0; (${" + str(i) + "}*10^18)/1\" | bc -l) "
                    else:
                        args_str += "${" + str(i) + "} "
                    args_str += " # " + str(i) + ": " + input["name"] + " (" + input["type"] + ")\n"
                f.write(args_str)
        f.write("    erdpy contract build\n")
        deploy_str = "    erdpy contract deploy --bytecode output/" + contract_name + ".wasm --recall-nonce ${PRIVATE_KEY} --keyfile ${OWNER}.json --gas-limit=500000000 --proxy=${PROXY} --chain=${CHAIN_ID} --send --outfile=\"deploy.interaction.json\" "
        if (data["constructor"]["inputs"]):
            deploy_str += "\\\n" + tab_str + tab_str + "--arguments "
            for i, input in enumerate(data["constructor"]["inputs"]):
                if input["type"] == "bytes" or input["type"] == "string" or input["type"] == "TokenIdentifier":
                    deploy_str += "str:${" + str(i) + "} "
                elif input["type"] == "BigUint" or input["type"] == "u64" or input["type"] == "u32" or input["type"] == "u16" or input["type"] == "u8":
                    deploy_str += "$(echo \"scale=0; (${" + str(i) + "}*10^18)/1\" | bc -l) "
                else:
                    deploy_str += "${ARG_" + str(i) + "} "
            deploy_str += "\n"
        deploy_str += "\n"
        f.write(deploy_str)
        f.write("    echo \"Deployed contract at the address written above.\"")
        f.write("    echo \"Pleade update the ADDRESS variable in this script with the address of the deployed contract, then run 'source interaction.sh' to update the environment variables.\"\n")
        f.write("}\n\n")

        # Upgrade
        f.write("# Standard upgrade command. Provide any constructor arguments as needed (e.g upgrade 12 TOKEN-123). Numbers are automatically scaled to 18 decimals. (e.g. 12 -> 12000000000000000000)\n")
        f.write("upgrade() {\n")
        if (data["constructor"]["inputs"]):
                args_str = "# Arguments: \n"
                for i, input in enumerate(data["constructor"]["inputs"]):
                    args_str += "ARG_" + str(i) + "="
                    if input["type"] == "bytes" or input["type"] == "string" or input["type"] == "TokenIdentifier":
                        args_str += "\"str:${" + str(i + 1) + "}\" "
                    elif input["type"] == "BigUint" or input["type"] == "u64" or input["type"] == "u32" or input["type"] == "u16" or input["type"] == "u8":
                        args_str += "$(echo \"scale=0; (${" + str(i + 1) + "}*10^18)/1\" | bc -l) "
                    else:
                        args_str += "${" + str(i + 1) + "} "
                    args_str += " # " + str(i) + ": " + input["name"] + " (" + input["type"] + ")\n"
                f.write(args_str)
        upgrade_str = "    erdpy contract upgrade ${ADDRESS} --bytecode output/" + contract_name + ".wasm --recall-nonce ${PRIVATE_KEY} --gas-limit=500000000 --proxy=${PROXY} --chain=${CHAIN_ID} --send "
        if (data["constructor"]["inputs"]):
            upgrade_str += "\\\n" + tab_str + tab_str + "--arguments "
            for i, input in enumerate(data["constructor"]["inputs"]):
                upgrade_str += "${ARG_" + str(i) + "} "
            upgrade_str += "\n"
        upgrade_str += "\n"
        f.write(upgrade_str)
        f.write("}\n\n")

        # Call endpoints
        f.write("# All contract endpoints are available as functions. Provide any arguments as needed (e.g transfer 12 TOKEN-123)\n\n")
        for endpoint in data["endpoints"]:
            if endpoint["mutability"] == "readonly":
                continue
            f.write(endpoint["name"] + "() {\n")
            if (endpoint["inputs"]):
                args_str = "# Arguments: \n"
                for i, input in enumerate(endpoint["inputs"]):
                    args_str += "ARG_" + str(i) + "="
                    if input["type"] == "bytes" or input["type"] == "string" or input["type"] == "TokenIdentifier":
                        args_str += "\"str:${" + str(i + 1) + "}\" "
                    elif input["type"] == "BigUint" or input["type"] == "u64" or input["type"] == "u32" or input["type"] == "u16" or input["type"] == "u8":
                        args_str += "$(echo \"scale=0; (${" + str(i + 1) + "}*10^18)/1\" | bc -l) "
                    else:
                        args_str += "${" + str(i + 1) + "} "
                    args_str += " # " + str(i) + ": " + input["name"] + " (" + input["type"] + ")\n"
                f.write(args_str)
            call_str = "    erdpy contract call ${ADDRESS} \\\n"
            call_str += tab_str + tab_str + "--recall-nonce ${PRIVATE_KEY} --gas-limit=500000000 --proxy=${PROXY} --chain=${CHAIN_ID} --send \\\n"
            call_str += tab_str + tab_str + "--function \"" + endpoint["name"] + "\" "
            if (endpoint["inputs"]):
                call_str += "\\\n" + tab_str + tab_str + "--arguments "
                for i, input in enumerate(endpoint["inputs"]):
                    call_str += "${ARG_" + str(i) + "} "
                call_str += "\n"
            call_str += "\n"
            f.write(call_str)
            f.write("}\n\n")

        # Query endpoints
        f.write("# All contract views. Provide arguments as needed (e.g balanceOf 0x1234567890123456789012345678901234567890)\n\n")
        for endpoint in data["endpoints"]:
            if endpoint["mutability"] != "readonly":
                continue
            f.write(endpoint["name"] + "() {\n")
            if (endpoint["inputs"]):
                args_str = "# Arguments: \n"
                for i, input in enumerate(endpoint["inputs"]):
                    args_str += "ARG_" + str(i) + "="
                    if input["type"] == "bytes" or input["type"] == "string" or input["type"] == "TokenIdentifier":
                        args_str += "\"str:${" + str(i + 1) + "}\" "
                    elif input["type"] == "BigUint" or input["type"] == "u64" or input["type"] == "u32" or input["type"] == "u16" or input["type"] == "u8":
                        args_str += "$(echo \"scale=0; (${" + str(i + 1) + "}*10^18)/1\" | bc -l) "
                    else:
                        args_str += "${" + str(i) + "} "
                    args_str += " # " + str(i) + ": " + input["name"] + " (" + input["type"] + ")\n"
                f.write(args_str)
            query_str = "    erdpy contract query ${ADDRESS} \\\n"
            query_str += tab_str + tab_str + "--function \"" + endpoint["name"] + "\" \\\n"
            query_str += tab_str + tab_str + "--proxy=${PROXY} "
            if (endpoint["inputs"]):
                query_str += "\\\n" + tab_str + tab_str + " --arguments "
                for i, input in enumerate(endpoint["inputs"]):
                    query_str += "${ARG_" + str(i) + "} "
                query_str += "\n"
            query_str += "\n"
            f.write(query_str)
            f.write("}\n\n")




def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python3 main.py <path_to_json>")
        return

    force = False
    if (len(sys.argv) == 3) and (sys.argv[2] == "--force" or sys.argv[2] == "-f"):
        force = True


    # Checks if contract_doc.md or interaction.sh already exist
    if not force and (os.path.exists("contract_doc.md") or os.path.exists("interaction.sh")):
        print("contract_doc.md or interaction.sh already exist. Please rename them and run again, or use the --force flag to overwrite them.")
        return


    with open(sys.argv[1]) as f:
        data = json.load(f)

    generate_markdown(data)
    generate_interaction_script(data)

    

if __name__ == "__main__":
    main()