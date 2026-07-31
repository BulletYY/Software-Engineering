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
    plots: bool,
    session_thresholds:list, 
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
    
    MAX_PAIRS = 13 # param to be changed to allow user to choose the number of pairs of sin and cos to be used in the model
    
    
    data = data.query(f'TIME >= {session_thresholds[0]} and TIME <= {session_thresholds[1]}').copy() # wziąłem 9:00 do 16:50 dla starego kodu , Czy Wyrzucac dogrywke czy nie 

    # log stopy zwrotu w obrębie dnia
    data['log_return_intraday'] = ( data.groupby('DATE')['CLOSE'].transform(lambda x: np.log(x).diff()))

    data = data.dropna(subset=['log_return_intraday'])

    data['DATE'] =pd.to_datetime(data['DATE'],format='%Y%m%d')
        
    # variables computation        

    N = 92 # ilosc 

    N_1 = (N+1) /2   

    N_2 = (N + 1) * (2*N + 1) / 6  # or (N+1)*(N+2)/6  
        
    # here based on the vol_estimation parameter, we can choose different methods to estimate volatility , to be implemented match case statement 
    
     # add an parameter here to allow user to provide his data
    
    dzienne_zwroty_log = data.query('TIME >= 90000 and TIME <= 165000') # to be removed  
    # pierwszy OPEN w dniu
    daily_open = dzienne_zwroty_log.groupby('DATE')['OPEN'].first()

    # ostatni CLOSE w dniu
    daily_close = dzienne_zwroty_log.groupby('DATE')['CLOSE'].last()

    # dzienne log-stopy (open → close)
    log_return_daily = np.log(daily_close) - np.log(daily_open)

    
    match vol_estimation:
        case "variance":
            # odchylenie standardowe
            std_daily = log_return_daily.var(ddof=1) # nie std ale var
            
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
            

    data["R_bar_n"] = data.groupby("sesja")["log_return_intraday"].transform("mean") # R_bar = data['log_return_intraday'].mean()   or assuming constant mean within session

    returns_centered = data['log_return_intraday'] - data["R_bar_n"]

    response = 2*np.log(np.abs(returns_centered) / (data['sigma_hat'] / np.sqrt(N) ))  # response variable 
    
    data['n'] = data.groupby('DATE').cumcount() +1 
    
    data['n^2'] = data['n'] **2
    
    data['linear'] = data['n'] / N_1 # trend liniiowy

    data['qube'] = data['n^2'] / N_2 # trend kwadratowy  
    
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
        expression = f"y~linear+qube+Wednesday+Monday+Thursday+Tuesday+"
        while p >0:
            expression+= f"sin_{p}"+"+"+f"cosine_{p}+"
            p-=1

        expression =expression.rstrip("+")

        model = ols(expression,data=binary_df).fit()
        aic_list.append(model.aic)
        bic_list.append(model.bic)
        
    print("\n")
    print("---"*60)
    print("AIC list:", aic_list.index(min(aic_list))+1)
    print("BIC list:", bic_list.index(min(bic_list))+1)
    print("---"*60)
    print("\n")
    
    
    if criteria == "AIC":
        optimal_pair = aic_list.index(min(aic_list))+1 
    elif criteria == "BIC":
        optimal_pair = bic_list.index(min(bic_list))+1
    else :
        raise Exception("Invalid criteria parameter. Choose from 'AIC' or 'BIC'.") # initial idea
    
   
    # HERE SHOULD BE ADDED THE LOOP WHICH CREATES SIN AND COS  
    
    match max_lags_kernel:
        case "bartlett":
            kernel = int( 4*(binary_df.shape[0]/100)**(2/9)  ) 
        case "other":
            pass # to be added
        case _:
            raise Exception("Invalid max_lags_kernel parameter. Choose from 'bartlett' or 'other'.") # initial idea 
    
    expression_model = f"y~linear+qube+sin_1+cosine_1+" 

    
    if not days:
        expression_model_2 = expression_model+f"{days[0]}+{days[1]}+{days[2]}+{days[3]}"
    
    
    model2 = ols("y~linear+qube+sin_1+cosine_1+Wednesday+Monday+Thursday+Tuesday",data=binary_df).fit( cov_type="HAC",cov_kwds={"maxlags": kernel })
    
    binary_df['estimated_var'] =model2.fittedvalues

    # normalization of the estimated seasonality of variance to get the seasonal component
    
    g = np.exp(binary_df['estimated_var'] / 2)

    TN = len(g)

    binary_df['s_hat'] = TN * g / g.sum()

    binary_df['s_hat'].mean()

    binary_df['deseasonalised_binary'] = binary_df['log_return_intraday'] / binary_df['s_hat']
    
    binary_df.groupby('sesja')['s_hat'].mean().plot()
    
    plt.show()
    
    
    return [model2.summary(), binary_df]
        
        
        
            
        


