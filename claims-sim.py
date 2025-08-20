#!/usr/bin/env python3
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from pathlib import Path

def simulate_claims(
    n_years,
    lob_params,
    deductible=0,
    limit=np.inf
):
    """
    Simulates insurance claims for multiple lines of business.

    Args:
        n_years (int): The number of policy years to simulate.
        lob_params (dict): A dictionary with lines of business as keys and their
                           frequency/severity parameters as values.
                           Example:
                           {
                               'Auto': {'freq': 1.5, 'sev_mean': 8.5, 'sev_std': 1.0},
                               'Home': {'freq': 0.5, 'sev_mean': 11.0, 'sev_std': 1.5}
                           }
        deductible (float): The deductible amount per claim.
        limit (float): The policy limit per claim.

    Returns:
        pandas.DataFrame: A DataFrame containing the simulated annual aggregate losses
                          for each line of business and the total portfolio.
    """
    results = {}

    for lob, params in lob_params.items():
        # Simulate claim frequency from a Poisson distribution
        claim_counts = np.random.poisson(params['freq'], n_years)

        # Calculate the total number of claims over all years for this LOB
        total_claims = np.sum(claim_counts)

        # Simulate claim severity from a Lognormal distribution
        # Note: The parameters for lognormal are the mean and std of the underlying normal distribution
        claim_severities = np.random.lognormal(
            mean=params['sev_mean'],
            sigma=params['sev_std'],
            size=total_claims
        )

        # Apply policy terms (deductible and limit)
        gross_loss = claim_severities
        net_loss = np.maximum(0, gross_loss - deductible)
        net_loss = np.minimum(net_loss, limit)

        # Aggregate losses by year
        annual_agg_losses = []
        current_claim_index = 0
        for count in claim_counts:
            if count > 0:
                year_losses = net_loss[current_claim_index : current_claim_index + count]
                annual_agg_losses.append(np.sum(year_losses))
                current_claim_index += count
            else:
                annual_agg_losses.append(0)

        results[lob] = annual_agg_losses

    df = pd.DataFrame(results)
    df['Total'] = df.sum(axis=1)
    return df

def calculate_risk_metrics(losses):
    """
    Calculates key risk metrics from a series of losses.

    Args:
        losses (pd.Series): A pandas Series of simulated losses.

    Returns:
        dict: A dictionary containing the expected loss, VaR at 95% and 99%,
              and TVaR at 95% and 99%.
    """
    expected_loss = losses.mean()
    var_95 = losses.quantile(0.95)
    var_99 = losses.quantile(0.99)
    tvar_95 = losses[losses >= var_95].mean()
    tvar_99 = losses[losses >= var_99].mean()

    return {
        'Expected Loss': expected_loss,
        'VaR 95%': var_95,
        'VaR 99%': var_99,
        'TVaR 95%': tvar_95,
        'TVaR 99%': tvar_99,
    }

def generate_charts(simulated_losses: pd.DataFrame, metrics_df: pd.DataFrame, outdir: Path = Path("figures")):
    """
    Generate charts from the simulation outputs and save them as PNGs under `outdir`.
    Creates:
      - portfolio_loss_hist.png
      - lob_loss_boxplot.png
      - portfolio_ecdf.png
      - lob_hists_<LOB>.png (one per LOB)
    """
    outdir.mkdir(exist_ok=True)

    # 1) Histogram of total (portfolio) losses with VaR markers
    plt.figure()
    plt.hist(simulated_losses["Total"].values, bins=100, density=True, alpha=0.7)
    plt.title("Distribution of Annual Portfolio Losses")
    plt.xlabel("Loss Amount")
    plt.ylabel("Density")
    if "Total" in metrics_df.index:
        if "VaR 95%" in metrics_df.columns:
            var95 = metrics_df.loc["Total", "VaR 95%"]
            plt.axvline(var95, linestyle="--", label=f"VaR 95% = {var95:,.0f}")
        if "VaR 99%" in metrics_df.columns:
            var99 = metrics_df.loc["Total", "VaR 99%"]
            plt.axvline(var99, linestyle="--", label=f"VaR 99% = {var99:,.0f}")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outdir / "portfolio_loss_hist.png")
    plt.close()

    # 2) Boxplot of LOB losses
    lob_cols = [c for c in simulated_losses.columns if c != "Total"]
    if lob_cols:
        plt.figure()
        simulated_losses[lob_cols].boxplot()
        plt.title("Distribution of Annual Losses by Line of Business")
        plt.ylabel("Loss Amount")
        plt.tight_layout()
        plt.savefig(outdir / "lob_loss_boxplot.png")
        plt.close()

        # 2b) Histograms per LOB
        for lob in lob_cols:
            plt.figure()
            plt.hist(simulated_losses[lob].values, bins=80, density=True, alpha=0.7)
            plt.title(f"Distribution of Annual Losses — {lob}")
            plt.xlabel("Loss Amount")
            plt.ylabel("Density")
            plt.tight_layout()
            plt.savefig(outdir / f"lob_hist_{lob.replace(' ', '_').lower()}.png")
            plt.close()

    # 3) Empirical CDF of total losses
    sorted_losses = np.sort(simulated_losses["Total"].values)
    ecdf = np.arange(1, len(sorted_losses)+1) / len(sorted_losses)
    plt.figure()
    plt.plot(sorted_losses, ecdf, marker=".", linestyle="none")
    plt.title("Empirical CDF of Portfolio Losses")
    plt.xlabel("Loss Amount")
    plt.ylabel("Cumulative Probability")
    plt.tight_layout()
    plt.savefig(outdir / "portfolio_ecdf.png")
    plt.close()


if __name__ == '__main__':
    # --- Simulation Parameters ---
    N_YEARS = 10000
    LOB_PARAMETERS = {
        'Commercial Auto': {'freq': 2.5, 'sev_mean': 9.0, 'sev_std': 1.2},
        'General Liability': {'freq': 1.0, 'sev_mean': 10.5, 'sev_std': 1.8},
        'Property': {'freq': 0.8, 'sev_mean': 12.0, 'sev_std': 2.0}
    }
    # Policy Terms
    DEDUCTIBLE = 1000
    LIMIT = 500000

    # --- Run Simulation ---
    print("Running claims simulation...")
    simulated_losses = simulate_claims(
        n_years=N_YEARS,
        lob_params=LOB_PARAMETERS,
        deductible=DEDUCTIBLE,
        limit=LIMIT
    )
    print("Simulation complete.")

    # --- Calculate Risk Metrics ---
    print("Calculating risk metrics...")
    all_metrics = {}
    for column in simulated_losses.columns:
        all_metrics[column] = calculate_risk_metrics(simulated_losses[column])
    metrics_df = pd.DataFrame(all_metrics).T  # Transpose for readability

    print("\nRisk Metrics:")
    print(metrics_df.to_string(float_format="{:,.2f}".format))

    # --- Export to Excel ---
    output_filename = 'claims_simulation_results.xlsx'
    print(f"\nExporting results to {output_filename}...")
    with pd.ExcelWriter(output_filename) as writer:
        simulated_losses.to_excel(writer, sheet_name='Simulated Annual Losses', index_label='Year')
        metrics_df.to_excel(writer, sheet_name='Risk Metrics Summary')
    print("Export complete.")

    # --- Generate Charts ---
    print("\nGenerating charts...")
    generate_charts(simulated_losses, metrics_df, outdir=Path("figures"))
    print("Charts saved to /figures")
