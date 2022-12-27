# Smart contract utilities generator
This simple script reads an ABI file and generates a Markdown file describing the smart-contract's endpoints, as well as a interaction.sh script,
that uses erdpy to deploy, upgrade or interact with the smart-contract's endpoints and views.
## Usage
`python3 main.py /path/to/abi/file.json`

Use the `--force` (or `-f`) flag to overwrite any existing *contract_doc.md* or *interaction.sh* files.

To use the *interaction.sh* script, modify its variables as instructed in the comments, then run  
`source interaction.sh`  
You can now deploy you contract by typing  
`deploy`  
followed by your contract's constructor arguments, if any.

Once your contract deployed, update the ADDRESS variable in the script and run again  
`source interaction.sh`

You can now call you contract's endpoint by typing  
`endpoint_name argument1 argument2 ...`  
BigUint arguments are automatically multiplied by 10^18, so you can type 0.01 to actually represent 0.01 tokens for example.

Note: Payable endpoints are not yet handled by the script. For EGLD payable endpoints, you can simply add a --value argument to the call. For ESDT transfers, you'll need to use the ESDTTransfer function (see the official documentation of erdpy)
