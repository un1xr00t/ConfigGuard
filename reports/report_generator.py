import json

def generate_report(check_results, output_format='json'):
    report_data = {}
    
    # Process each check result
    for check, result in check_results.items():
        if isinstance(result, list):  # If result is a list (e.g., list of services)
            report_data[check] = result
        else:  # Handle other cases if necessary
            report_data[check] = str(result)
    
    # Output report in the desired format
    if output_format == 'json':
        with open('security_report.json', 'w') as file:
            json.dump(report_data, file, indent=4)
    elif output_format == 'txt':
        with open('security_report.txt', 'w') as file:
            for check, result in report_data.items():
                file.write(f"{check}:\n")
                if isinstance(result, list):
                    for item in result:
                        file.write(f"  - {item}\n")
                else:
                    file.write(f"  - {result}\n")
                file.write("\n")

