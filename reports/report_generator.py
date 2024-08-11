import json

def generate_report(check_results, issues, output_format='txt'):
    report_data = {}

    # Process each check result
    for check, result in check_results.items():
        if isinstance(result, list):
            report_data[check] = result
        else:
            report_data[check] = str(result)

    # Output report in the desired format
    if output_format == 'txt':
        with open('security_report.txt', 'w') as file:
            # Include failed checks and their remediation steps
            if issues:
                file.write("Security Configuration Checker - Remediation Report\n")
                file.write("=" * 50 + "\n\n")
                for issue, remediation in issues.items():
                    file.write(f"Issue: {issue}\n")
                    file.write(f"Remediation: {remediation['fix']}\n")
                    if remediation.get('service_restart'):
                        file.write(f"To apply changes, restart the service with:\n")
                        file.write(f"  sudo systemctl restart {remediation['service_restart']}\n")
                    file.write("\n")
                file.write("=" * 50 + "\n")

            # Include all check results (passed and failed)
            for check, result in report_data.items():
                file.write(f"{check}:\n")
                if isinstance(result, list):
                    for item in result:
                        file.write(f"  - {item}\n")
                else:
                    file.write(f"  - {result}\n")
                file.write("\n")

            file.write("End of Report\n")

    elif output_format == 'json':
        with open('security_report.json', 'w') as file:
            json.dump(report_data, file, indent=4)