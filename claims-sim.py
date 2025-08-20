#!/usr/bin/env python3
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from pathlib import Path

def simulate_claims(n_years, lob_params, deductible=0, limit=np.inf):
    # make annual losses for each line of business (Poisson freq, Lognormal sev)
    out = {}
    for lob, p in lob_params.items():
        counts = np.random.poisson(p['freq'], n_years)               # yearly claim counts
        sev = np.random.lognormal(p['sev_mean'], p['sev_std'], counts.sum())  # claim sizes
        net = np.clip(sev - deductible, 0, limit)                     # apply ded + limit
        # roll claims up by year
        idx, yearly = 0, []
        for c in counts:
            yearly.append(net[idx:idx+c].sum() if c else 0.0)
            idx += c
        out[lob] = yearly
    df = pd.DataFrame(out); df['Total'] = df.sum(axis=1)              # add portfolio total
    return df

def calculate_risk_metrics(s):
    # expected loss + tail risk stats
    v95, v99 = s.quantile(0.95), s.quantile(0.99)
    return {'Expected Loss': s.mean(), 'VaR 95%': v95, 'VaR 99%': v99,
            'TVaR 95%': s[s>=v95].mean(), 'TVaR 99%': s[s>=v99].mean()}

def generate_charts(df, metrics, outdir=Path("figures")):
    # save a few quick charts to /figures
    outdir.mkdir(exist_ok=True)
    # portfolio histogram with VaR markers
    plt.figure(); plt.hist(df["Total"], bins=100, density=True, alpha=.7)
    if "Total" in metrics.index:
        for col in ("VaR 95%","VaR 99%"):
            if col in metrics.columns: plt.axvline(metrics.loc["Total", col], ls="--", label=col)
    plt.title("Annual Portfolio Losses"); plt.xlabel("Loss"); plt.ylabel("Density"); plt.legend(); plt.tight_layout()
    plt.savefig(outdir/"portfolio_loss_hist.png"); plt.close()
    # boxplot + histograms per LOB
    lob_cols=[c for c in df.columns if c!="Total"]
    if lob_cols:
        plt.figure(); df[lob_cols].boxplot(); plt.title("Annual Losses by LOB"); plt.ylabel("Loss"); plt.tight_layout()
        plt.savefig(outdir/"lob_loss_boxplot.png"); plt.close()
        for lob in lob_cols:
            plt.figure(); plt.hist(df[lob], bins=80, density=True, alpha=.7)
            plt.title(f"{lob} — Annual Losses"); plt.xlabel("Loss"); plt.ylabel("Density"); plt.tight_layout()
            plt.savefig(outdir/f"lob_hist_{lob.replace(' ','_').lower()}.png"); plt.close()
    # empirical CDF for portfolio
    x=np.sort(df["Total"].values); ecdf=np.arange(1,len(x)+1)/len(x)
    plt.figure(); plt.plot(x, ecdf, marker=".", ls="none")
    plt.title("Portfolio Loss ECDF"); plt.xlabel("Loss"); plt.ylabel("Cum. Prob."); plt.tight_layout()
    plt.savefig(outdir/"portfolio_ecdf.png"); plt.close()

if __name__=="__main__":
    # sim knobs
    N_YEARS=10_000
    LOB_PARAMETERS={
        'Commercial Auto': {'freq':2.5,'sev_mean':9.0,'sev_std':1.2},
        'General Liability': {'freq':1.0,'sev_mean':10.5,'sev_std':1.8},
        'Property': {'freq':0.8,'sev_mean':12.0,'sev_std':2.0},
    }
    DEDUCTIBLE=1_000; LIMIT=500_000
    # run sim + metrics
    losses=simulate_claims(N_YEARS, LOB_PARAMETERS, DEDUCTIBLE, LIMIT)
    metrics=pd.DataFrame({c:calculate_risk_metrics(losses[c]) for c in losses.columns}).T
    print(metrics.to_string(float_format="{:,.2f}".format))
    # write outputs
    with pd.ExcelWriter("claims_simulation_results.xlsx") as w:
        losses.to_excel(w, sheet_name="Simulated Annual Losses", index_label="Year")
        metrics.to_excel(w, sheet_name="Risk Metrics Summary")
    generate_charts(losses, metrics)
