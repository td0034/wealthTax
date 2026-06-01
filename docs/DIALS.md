# Dial panel — v0

The viewer-as-legislator's affordances. Defaults are tuned to a stylised "current world" — rentier returns above wage growth, low taxes, no UBI, easy credit.

## Production
- **wage** — pay per labour unit. Default 1.0.
- **maker_multiplier** — value-add ratio for makers (output / inputs). Default 1.6.
- **employer_markup** — share of worker output the employer keeps. Default 0.4.
- **workers_per_maker / workers_per_employer** — hiring capacity. Default 2 / 6.

## Capital & credit
- **capital_return (r)** — passive return on rentier wealth per tick. Default 0.04.
- **rent_share_of_wage** — share of worker wage paid as rent. Default 0.35.
- **interest_rate (i)** — lender charge on debt per tick. Default 0.06.
- **spec_drift / spec_vol** — speculator mean return / volatility. Default 0.015 / 0.12.

## State
- **ubi** — flat payment to every non-state agent per tick. Default 0.
- **flat_tax_rate** — wealth tax per tick. Default 0.
- **tax_progressivity** — extra rate on wealth above threshold. Default 0.
- **wealth_tax_threshold** — wealth level above which progressive rate applies. Default 50.

## Life
- **subsistence** — cost to live per tick. Default 0.6.
- **debt_ceiling** — debt level beyond which an agent starves out. Default 25.

## Parked for v2
- inheritance_cap, reproduction, memory_bandwidth — all require births.

## What the viewer sees
- Gini coefficient (wealth inequality)
- Metabolic rate (total value transformed this tick) — the "is the economy alive" gauge
- Wealth share by type over time
- Population alive vs starved
- Total debt
