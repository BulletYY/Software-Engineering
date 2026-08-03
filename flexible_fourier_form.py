from typing import Tuple
import pandas as pd
import numpy as np
from statsmodels.formula.api import ols 
from math import pi
import matplotlib.pyplot as plt
from arch import arch_model


def flexible_fourier_form(
    data: pd.DataFrame, 
    criteria: str, 
    vol_estimation: str, 
    session_thresholds:list, 
    plots: bool =True,
    days: list= [], 
    max_lags_kernel :str='bartlett',
    N: int = None,
    verbose:bool=False)->Tuple:
    """ 
    
    This function is a placeholder for the flexible Fourier form implementation. It is intended 
    to be developed further.    
    
    implementation is based on the paper "Andersen T.G., Bollerslev T. (1997), Intraday periodicity and volatility persistence in financial markets, "Journal of Empirical Finance", vol. 4, no. 2-3." 
    
    DOI : "10.1016/S0927-5398(97)00004-2"
    
    
    """
    
    MAX_PAIRS = 13 # Hardcoded param which allows user to choose the maximum number of the sin and cos in the simulation. 
    
    
    data = data.query(f'TIME >= {session_thresholds[0]} and TIME <= {session_thresholds[1]}').copy() # wziąłem 9:00 do 16:50 dla starego kodu , Czy Wyrzucac dogrywke czy nie 

    # compute daily returns 
    data['log_return_intraday'] = ( data.groupby('DATE')['CLOSE'].transform(lambda x: np.log(x).diff()))

    data = data.dropna(subset=['log_return_intraday'])

    data['DATE'] =pd.to_datetime(data['DATE'],format='%Y%m%d')
        
    # repsonse and explanatory variables computation        

    N = 92 # ilosc 

    N_1 = (N+1) /2   

    N_2 = (N + 1) * (2*N + 1) / 6  # or (N+1)*(N+2)/6  
        
    # first open value in the day
    daily_open = data.groupby('DATE')['OPEN'].first()

    # last close value in the day
    daily_close = data.groupby('DATE')['CLOSE'].last()

    # daily returns 
    log_return_daily = np.log(daily_close) - np.log(daily_open)
    
    # choose appropriate method to estimate volatility based on the vol_estimation parameter
    
    match vol_estimation:
        case "variance":
            
            std_daily = log_return_daily.std(ddof=1)
            
            data['sigma_hat']= std_daily

        case "garch":
            
            std_daily = arch_model(log_return_daily, 
                                   vol='GARCH', 
                                   dist='t',
                                   p=1, 
                                   q=1,
                                   rescale=True
                                   ).fit(disp="off").conditional_volatility.to_dict()
            
            data["sigma_hat"] = data["DATE"].map(std_daily)
            
        case "egarch":
            
            std_daily = arch_model(log_return_daily, 
                                        vol='EGARCH', 
                                        dist='t',
                                        p=1,
                                        o=1, 
                                        q=1,
                                        rescale=True
                                        ).fit(disp="off").conditional_volatility.to_dict()
                
            data["sigma_hat"] = data["DATE"].map(std_daily)
    
        case "aparch": # and other models to be aded 
            pass
        case _:
            raise Exception("Invalid vol_estimation parameter. Choose from 'variance', 'garch', 'egarch', or 'aparch'.") 
            

    data["R_bar_n"] = data.groupby("session")["log_return_intraday"].transform("mean") # R_bar = data['log_return_intraday'].mean()   or assuming constant mean within session

    returns_centered = data['log_return_intraday'] - data["R_bar_n"]

    response = 2*np.log(np.abs(returns_centered) / (data['sigma_hat'] / np.sqrt(N) ))  # response variable 
    
    data['n'] = data.groupby('DATE').cumcount() +1 
    
    data['n^2'] = data['n'] **2
    
    data['linear'] = data['n'] / N_1 # trend liniiowy

    data['cube'] = data['n^2'] / N_2 # trend kwadratowy  
    
    data['y'] = response
    
    for p in range(1,MAX_PAIRS):
        data[f'sin_{p}'] = np.sin(2*pi*p*data['n']/N) 
        data[f'cosine_{p}'] = np.cos(2*pi*p*data['n']/N) 
                
    
    binary_df = pd.concat([
        pd.get_dummies( data["DATE"].dt.day_name(), dtype=int), data],axis=1)
    
    # choose appropriate criteria to find optimal pair of sin and cos 
    aic_list = []
    bic_list = []
    

    for p in range(1,MAX_PAIRS):
        
        expression = f"y~linear+cube+"
        
        if days:
            expression += " + ".join(days) + "+"

        
        while p >0:
            expression+= f"sin_{p}"+"+"+f"cosine_{p}+"
            p-=1

        expression =expression.rstrip("+")

        model = ols(expression,data=binary_df).fit()
        aic_list.append(model.aic)
        bic_list.append(model.bic)
        
        # to be added verbose to highlight the estimation process. (aic values bic etc)
        
    match criteria:
        case "AIC":
            optimal_pair = aic_list.index(min(aic_list))+1
            print("AIC optimal pair", optimal_pair)

        case "BIC" :  
            optimal_pair = bic_list.index(min(bic_list))+1
            print("BIC optimal pair", optimal_pair)

        case _:
            raise Exception("Invalid criteria parameter. Choose from 'AIC' or 'BIC'.") # initial idea
   
    match max_lags_kernel:
        case "bartlett":
            kernel = int( 4*(binary_df.shape[0]/100)**(2/9)  ) 
        case "other":
            pass # to be added
        case _:
            raise Exception("Invalid max_lags_kernel parameter. Choose from 'bartlett' or 'other'.") # initial idea 
    
    expression_model = f"y~linear+cube+" # sin_1+cosine_1+ 

    
    if days:
        expression_model += " + ".join(days)
        
    for pair in range(1, optimal_pair+1):
        expression_model += f"+sin_{pair}+cosine_{pair}"
    
    model2 = ols(expression_model,data=binary_df).fit( cov_type="HAC",cov_kwds={"maxlags": kernel }) # "y~linear+cube+sin_1+cosine_1+Wednesday+Monday+Thursday+Tuesday"
    
    binary_df['estimated_var'] =model2.fittedvalues

    # normalization of the estimated seasonality of variance to estimate the seasonal component.
    
    g = np.exp(binary_df['estimated_var'] / 2)

    TN = len(g)

    binary_df['s_hat'] = TN * g / g.sum()

    binary_df['s_hat'].mean()

    binary_df['deseasonalised_binary'] = binary_df['log_return_intraday'] / binary_df['s_hat']
    
    if plots:
        
        binary_df.groupby('session')['s_hat'].mean().plot()
        
        plt.show()
        
    
    
    return [model2.summary(), binary_df]