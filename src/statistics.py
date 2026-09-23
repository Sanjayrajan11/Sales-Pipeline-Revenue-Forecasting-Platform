"""Associations in simulated observational data, with uncertainty and effect sizes."""

import numpy as np
import pandas as pd
from scipy import stats


def statistical_analysis(o: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Wilson intervals and a lead-source proportion test; no causal claims."""
    resolved = o[o.deal_status.isin(["Closed Won", "Closed Lost"])].copy()
    resolved["won"] = resolved.deal_status.eq("Closed Won").astype(int)
    rows = []
    z = 1.96
    for source, g in resolved.groupby("lead_source"):
        n, p = len(g), g.won.mean()
        center = (p + z * z / (2 * n)) / (1 + z * z / n)
        half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
        rows.append(
            {
                "lead_source": source,
                "resolved_deals": n,
                "wins": g.won.sum(),
                "win_rate": p,
                "ci_lower": center - half,
                "ci_upper": center + half,
            }
        )
    table = pd.crosstab(resolved.lead_source, resolved.won)
    if min(table.shape) >= 2:
        chi, pvalue, _, expected = stats.chi2_contingency(table)
        effect = np.sqrt(
            chi / (table.to_numpy().sum() * min(table.shape[0] - 1, table.shape[1] - 1))
        )
        test = f"Chi-square={chi:.3f}; p={pvalue:.6g}; Cramér V={effect:.4f}; minimum expected cell={expected.min():.2f}."
    else:
        test = "Insufficient resolved source/outcome groups to perform the test."
    corr = resolved[["engagement_score", "won"]].corr(method="spearman").iloc[0, 1]
    text = (
        "# Statistical analysis\n\nQuestion: do resolved-deal win proportions differ across lead sources?\n\n"
        "H0: proportions are equal. H1: at least one differs. Pearson chi-square tests the contingency table. "
        "Wilson 95% intervals describe individual proportions, not simultaneous comparisons.\n\n"
        + test
        + f"\n\nEngagement/win Spearman association: {corr:.4f}.\n\n"
        "Interpretation: compare effect size and commercial value, not only significance in a large dataset. "
        "The generator intentionally creates source and engagement associations. Accounts and representatives repeat, "
        "so independent-observation assumptions are imperfect; p-values are illustrative, not real-world evidence. "
        "Resolved-only comparisons may suffer maturity and selection bias. These results do not establish causation. "
        "Validate with account-clustered uncertainty and prospective experiments before changing real sales policy.\n"
    )
    return pd.DataFrame(rows), text
