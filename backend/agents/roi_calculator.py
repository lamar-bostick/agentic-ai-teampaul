import json
import math
import pandas as pd

# === Constants ===
SERVER_POWER_KW = {
    "DL380": 0.45,
    "R740": 0.50,
    "R750": 0.50,
    "SR650": 0.40
}
SERVER_COST = {
    "DL380": 120,
    "R740": 140,
    "R750": 140,
    "SR650": 100,
    "Other": 120
}
STORAGE_COST_PER_GB = 0.021
TRANSFER_COST_PER_GB = 0.01
# EGRESS_COST_PER_GB = 0.01  # Removed from usage
VPN_MONTHLY = 100
SUPPORT_MONTHLY = 300
CLOUDOPS_MONTHLY = 1000
LABOR_BASE = 1000
LABOR_PER_APP = 500
LABOR_MONTHLY = 1000

MANUAL_STORAGE = {
    "VA": 754800,
    "AZ": 368400,
    "CO": 379200
}

def adjusted_storage(site, default_gb):
    if site in MANUAL_STORAGE:
        return MANUAL_STORAGE[site]
    return default_gb * 1.3

def extra_network_cost(mbps):
    gb_month = mbps * 0.3 * 60 * 60 * 24 * 30 / 8 / 1024
    return gb_month * 0.01

def calculate_power_cost(dl380, r740_750, sr650, rate):
    total_kw = (
        dl380 * SERVER_POWER_KW["DL380"] +
        r740_750 * SERVER_POWER_KW["R740"] +
        sr650 * SERVER_POWER_KW["SR650"]
    )
    monthly_kwh = total_kw * 24 * 30.44
    return monthly_kwh * rate

def process_site(site_key, data):
    app_count = data.get("number_of_applications", 0)
    dl380 = data.get("DL380_count", 0)
    r740_750 = data.get("R740_R750_count", 0)
    sr650 = data.get("SR650_count", 0)
    raw_gb = data.get("total_GB", 0)
    storage_gb = adjusted_storage(site_key, raw_gb)
    lease_cost = data.get("Monthly Rent", 0)
    bandwidth = data.get("sum_of_bandwidth", 0)
    power_rate = data.get("power_rate", 0.08)

    # Cloud Costs
    compute = dl380 * SERVER_COST["DL380"] + r740_750 * SERVER_COST["R740"] + sr650 * SERVER_COST["SR650"]
    storage = storage_gb * STORAGE_COST_PER_GB
    transfer = storage_gb * TRANSFER_COST_PER_GB
    egress = 0  # Egress removed
    extra_net = extra_network_cost(bandwidth)
    vpn = VPN_MONTHLY
    support = SUPPORT_MONTHLY
    cloudops = CLOUDOPS_MONTHLY
    labor = LABOR_BASE + LABOR_PER_APP * app_count

    cloud_monthly = compute + storage + egress + vpn + support + cloudops + extra_net
    cloud_yearly = 12 * cloud_monthly
    one_time = transfer + labor
    investment = cloud_yearly + one_time

    power = calculate_power_cost(dl380, r740_750, sr650, power_rate)
    onprem_monthly = lease_cost + power + LABOR_MONTHLY
    onprem_yearly = 12 * onprem_monthly

    savings = onprem_yearly - cloud_yearly
    roi = (savings - one_time) / one_time if one_time > 0 else float("inf")
    payback = investment / savings if savings > 0 else float("inf")

    # Debug output
    print(f"\n--- DEBUG: {site_key} ---")
    print(f"Applications: {app_count}, DL380: {dl380}, R740/R750: {r740_750}, SR650: {sr650}")
    print(f"Storage (GB, adjusted): {storage_gb}")
    print(f"Bandwidth (Mbps): {bandwidth}")
    print(f"Lease Monthly Rent: {lease_cost}")
    print(f"Power Rate: {power_rate}, Power Monthly: {power:.2f}")
    print(f"On-Prem Monthly = Rent({lease_cost}) + Power({power:.2f}) + Labor({LABOR_MONTHLY}) = {onprem_monthly:.2f}")
    print(f"On-Prem Yearly: {onprem_yearly}")
    print(f"Cloud Monthly Breakdown: Compute={compute:.2f}, Storage={storage:.2f}, VPN={vpn}, Support={support}, CloudOps={cloudops}, ExtraNet={extra_net:.2f}")
    print(f"Cloud Monthly Total: {cloud_monthly:.2f}")
    print(f"Cloud Yearly: {cloud_yearly}")
    print(f"One-Time Cost = Transfer({transfer:.2f}) + Labor({labor}) = {one_time:.2f}")
    print(f"Investment: {investment}, Savings: {savings}")
    print(f"ROI: {roi}, Payback: {payback}\n")

    return {
        "Site": site_key,
        "OnPrem_Yearly": round(onprem_yearly),
        "Cloud_Yearly": round(cloud_yearly),
        "OneTime_Cost": round(one_time),
        "Investment": round(investment),
        "Savings": round(savings),
        "ROI": f"{roi * 100:.1f}%",
        "Payback_Years": f"{payback:.1f}" if math.isfinite(payback) else "N/A"
    }

def run_roi_calculations_from_json(lease_data):
    results = []
    for site_key, site_data in lease_data.items():
        results.append(process_site(site_key, site_data))
    return pd.DataFrame(results)
