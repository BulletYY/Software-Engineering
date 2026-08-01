# Flexible Fourier Form

An experimental Python implementation of the **Flexible Fourier Form (FFF)** for modelling intraday periodicity in financial-market volatility.

The project follows the approach described in:

> Andersen, T. G., & Bollerslev, T. (1997).  
> *Intraday Periodicity and Volatility Persistence in Financial Markets*.  
> Journal of Empirical Finance, 4(2–3), 115–158.  
> DOI: [10.1016/S0927-5398(97)00004-2](https://doi.org/10.1016/S0927-5398(97)00004-2)

> [!IMPORTANT]
> This repository is a work in progress. 

## Overview

The Flexible Fourier Form represents the deterministic intraday volatility pattern with:

- a linear trend,
- a quadratic trend,
- pairs of sine and cosine terms,
- optional weekday dummy variables.

The number of Fourier pairs is selected using the Akaike Information Criterion (`AIC`) or Bayesian Information Criterion (`BIC`). The final regression is estimated with heteroskedasticity and autocorrelation consistent (`HAC`) standard errors.

The function also calculates a normalized seasonal component and uses it to produce deseasonalized intraday returns.

## Project Structure

```text
Software-Engineering-main/
├── flexible_fourier_form.py  # Flexible Fourier Form implementation
├── main.py                   # Python entry-point script
├── launch_example.ipynb      # Complete launch example
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignore rules
└── README.md                 # Project documentation
```

## Installation

Install the project dependencies:

```bash
pip install -r requirements.txt
```

A complete launch example is available in [`launch_example.ipynb`](launch_example.ipynb).

## Input Data

The function expects a `pandas.DataFrame` containing at least the following columns:

| Column | Expected format | Description |
|---|---|---|
| `DATE` | `YYYYMMDD`, for example `20240131` | Trading date. |
| `TIME` | `HHMMSS` stored as an integer, for example `90000` | Intraday observation time. |
| `OPEN` | Numeric | Opening price for the observation. |
| `CLOSE` | Numeric | Closing price for the observation. |
| `session` | Time-like or categorical | Intraday time bucket used when calculating session means and plotting seasonality. |

Observations outside the interval supplied in `session_thresholds` are removed before estimation.

## Main Function

```python
flexible_fourier_form(
    data,
    criteria,
    vol_estimation,
    session_thresholds,
    plots=True,
    days=[],
    max_lags_kernel="bartlett",
    N=None,
    verbose=False,
)
```

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `data` | `pandas.DataFrame` | Intraday market data containing the required columns described above. |
| `criteria` | `str` | Fourier-pair selection criterion. Currently accepts uppercase `"AIC"` or `"BIC"`. |
| `vol_estimation` | `str` | Daily volatility estimator. Implemented values are `"variance"`, `"garch"`, and `"egarch"`. |
| `session_thresholds` | `list` | Two values defining the inclusive session start and end, for example `[90000, 165000]`. |
| `plots` | `bool`, optional | When `True`, plots the average estimated seasonal component by session. Default: `True`. |
| `days` | `list[str]`, optional | Weekday dummy-variable names included in the regression, for example `["Monday", "Tuesday", "Wednesday", "Thursday"]`. Default: `[]`. |
| `max_lags_kernel` | `str`, optional | Method used to determine the HAC maximum lag. Currently only `"bartlett"` is implemented. Default: `"bartlett"`. |
| `N` | `int`, optional | Intended number of intraday observations per trading day. In the current implementation this argument is overridden internally with `N = 92`. |
| `verbose` | `bool`, optional | Reserved for future diagnostic output. It is currently not used. Default: `False`. |

### Volatility Estimation Methods

| Value | Current behavior |
|---|---|
| `"variance"` | Uses one constant sample standard deviation calculated from daily open-to-close log returns. |
| `"garch"` | Fits a GARCH(1,1) model with Student's t innovations to daily log returns. |
| `"egarch"` | Fits an EGARCH(1,1,1) model with Student's t innovations to daily log returns. |
| `"aparch"` | Listed as a planned option, but not implemented yet. |

## Returned Values

The function currently returns a two-element list that can be unpacked as follows:

```python
model_summary, result = flexible_fourier_form(...)
```

| Value | Description |
|---|---|
| `model_summary` | A `statsmodels` summary object for the final OLS model estimated with HAC covariance. |
| `result` | A DataFrame containing the transformed input data, regressors, fitted values, seasonal estimates, and deseasonalized returns. |

Important columns added to `result` include:

| Column | Description |
|---|---|
| `log_return_intraday` | Within-day logarithmic return calculated from `CLOSE`. |
| `sigma_hat` | Estimated daily volatility mapped to each intraday observation. |
| `y` | Log-transformed response variable used in the FFF regression. |
| `linear` | Normalized linear intraday trend. |
| `cube` | Name currently used in the code for the normalized quadratic trend. |
| `sin_k`, `cosine_k` | Fourier regressors for harmonic pair `k`. |
| `estimated_var` | Fitted value from the final regression. |
| `s_hat` | Normalized estimated intraday seasonal component. |
| `deseasonalised_binary` | Intraday return divided by the estimated seasonal component. |

## Estimation Workflow

1. Filter observations to the selected trading session.
2. Calculate within-day log returns from closing prices.
3. Calculate daily open-to-close log returns.
4. Estimate daily volatility using the selected method.
5. Construct the response variable, polynomial trends, weekday dummies, and Fourier terms.
6. Fit candidate models containing between 1 and 12 Fourier pairs.
7. Select the preferred number of pairs using `AIC` or `BIC`.
8. Refit the selected model with HAC standard errors.
9. Normalize the fitted periodic component to obtain `s_hat`.
10. Calculate deseasonalized intraday returns.

## Reference

Andersen, T. G., & Bollerslev, T. (1997). Intraday periodicity and volatility persistence in financial markets. *Journal of Empirical Finance, 4*(2–3), 115–158. https://doi.org/10.1016/S0927-5398(97)00004-2
