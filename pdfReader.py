from utils.bbva_bank import get_bbva_bank_statement


function_map = {
    "BBVA": {
        "bankStatement": get_bbva_bank_statement
    }
}


def getResponse(request):
    func = function_map.get(request["issuer"], {}).get(request["policyType"], None)

    if func is not None:
        # If the function is found, call it and save its output
        output = func(request['url'])
        return output
    else:
        # If the function is not found, return an error message
        return "Function not found for the given issuer and policyType"

