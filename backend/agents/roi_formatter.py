import json
import pandas as pd
import re
from agents.roi_calculator import run_roi_calculations_from_json

def format_lease_site_details(lease_data):
    html = ""
    for site, data in lease_data.items():
        storage_gb = data.get("total_GB", 0)
        app_count = data.get("number_of_applications", 0)
        one_time_moving_fee = round(storage_gb * 0.01 + 1000 + 500 * app_count, 2)

        html += f"""
        <h4>{site}:</h4>
        <ul>
            <li><strong>Monthly Rent:</strong> ${data.get('Monthly Rent', 'N/A')}</li>
            <li><strong>Termination Fee:</strong> {data.get('termination_fee_clause', 'N/A')}</li>
            <li><strong>Under Occupancy Clause:</strong> {data.get('under_occupancy', 'N/A')}</li>
            <li><strong>Monthly Storage Cost:</strong> ${round(storage_gb * 0.021, 2)}</li>
            <li><strong>One-Time Moving Fee:</strong> ${one_time_moving_fee}</li>
            <li><strong>On-Premise Cost:</strong> Calculated in ROI table below</li>
        </ul>
        <hr>
        """
    return html


def format_roi_summary_table(roi_df):
    table_html = "<h4>Summary Table</h4><table class='table table-bordered'><thead><tr>"
    table_html += ''.join(f"<th>{col}</th>" for col in roi_df.columns)
    table_html += "</tr></thead><tbody>"
    for _, row in roi_df.iterrows():
        table_html += "<tr>" + ''.join(f"<td>{val}</td>" for val in row) + "</tr>"
    table_html += "</tbody></table>"
    return table_html

def get_html_output(lease_json_path):
    with open(lease_json_path, "r") as f:
        raw = json.load(f)

    # Extract and clean embedded JSON
    response_str = raw.get("response", "")
    cleaned_str = re.sub(r"^```json|```$", "", response_str.strip(), flags=re.MULTILINE)
    lease_data = json.loads(cleaned_str)

    # Run ROI calculations
    roi_df = run_roi_calculations_from_json(lease_data)

    # Format HTML
    lease_html = format_lease_site_details(lease_data)
    roi_html = format_roi_summary_table(roi_df)

    return lease_html + roi_html
