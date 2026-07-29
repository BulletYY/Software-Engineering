# Flexible Fourier Form

This project contains an experimental implementation of the **Flexible Fourier Form (FFF)** used to model intraday periodicity and volatility in financial markets.

The implementation is based on the following paper:

> Andersen, T. G. & Bollerslev, T. (1997).  
> *Intraday Periodicity and Volatility Persistence in Financial Markets*.  
> Journal of Empirical Finance, 4(2-3).  
> DOI: `10.1016/S0927-5398(97)00004-2`

## Project Structure

```text
Software-Engineering/
├── flexible_fourier_form.py
├── main.py
├── .gitignore
└── README.md
```

- `flexible_fourier_form.py` - contains the Flexible Fourier Form implementation.
- `main.py` - contains an example of how to import and use the function.
- `.gitignore` - specifies files and directories that should not be tracked by Git.
- `README.md` - contains the project documentation.

## Main Function

```python
flexible_fourier_form(
    data,
    criteria,
    vol_estimation,
    days,
    plots,
    session_thresholds,
    N=None
)
```

## Parameters

| Parameter | Type | Description |
|---|---|---|
| `data` | `pandas.DataFrame` | Intraday financial data used in the analysis. |
| `criteria` | `str` | Model selection criterion, such as `aic` or `bic`. |
| `vol_estimation` | `str` | Volatility estimation method. Planned values include `variance`, `garch`, `egarch`, and `aparch`. |
| `days` | `list` | List of weekdays or trading days included in the analysis. |
| `plots` | `bool` | Determines whether plots should be generated. |
| `session_thresholds` | `list` | Start and end times of the analyzed trading session, for example `[900, 1650]`. |
| `N` | `int`, optional | Number of intraday observations within one trading session. |
