import pandas as pd
import numpy as np
from statsmodels.formula.api import ols 
from math import pi
import matplotlib.pyplot as plt



def flexible_fourier_form(
    data: pd.DataFrame, 
    criteria: str, 
    vol_estimation: str, 
    days: list, 
    plots: bool,
    session_thresholds:list, 
    N: int = None):
    """ 
    
    This function is a placeholder for the flexible Fourier form implementation. It is intended 
    to be developed further.    
    
    implementation is based on the paper "Andersen T.G., Bollerslev T. (1997), Intraday periodicity and volatility persistence in financial markets, "Journal of Empirical Finance", vol. 4, no. 2-3." 
    
    DOI : "10.1016/S0927-5398(97)00004-2"
    
    
    """
    
    daily_returns_log = data.query('TIME >= 90000 and TIME <= 165000')  
    
    daily_open = daily_returns_log.groupby('DATE')['OPEN'].first()

    daily_close = daily_returns_log.groupby('DATE')['CLOSE'].last()

    log_return_daily = np.log(daily_close) - np.log(daily_open)

    std_daily = log_return_daily.var(ddof=1) # nie std ale var

    data = data.query(f'TIME >= {session_thresholds[0]} and TIME <= {session_thresholds[1]}') # wziąłem 9:00 do 16:50 dla starego kodu , Czy Wyrzucac dogrywke czy nie 

    # log stopy zwrotu w obrębie dnia
    data['log_return_intraday'] = ( data.groupby('DATE')['CLOSE'].transform(lambda x: np.log(x).diff()))

    data = data.dropna(subset=['log_return_intraday'])

    data['DATE'] =pd.to_datetime(data['DATE'],format='%Y%m%d')
        
    data['dni_tygodnia'] =data['DATE'].dt.day_name()
    
    # variables computation        

    N = 92 # ilosc 

    N_1 = (N+1) /2   

    N_2 = (N + 1) * (2*N + 1) / 6  # or (N+1)*(N+2)/6  

    R_bar = data['log_return_intraday'].mean()   
        
    # here based on the vol_estimation parameter, we can choose different methods to estimate volatility , to be implemented match case statement 
    
    sigma_hat = std_daily # 13110

    data["R_bar_n"] = data.groupby("sesja")["log_return_intraday"].transform("mean")

    returns_centered = data['log_return_intraday']   - data["R_bar_n"]

    response = 2*np.log(np.abs(returns_centered) / (sigma_hat / np.sqrt(N) ))  # response variable 
    
    data['n'] = data.groupby('DATE').cumcount() +1 
    
    data['n^2'] = data['n'] **2
    
    data['linear'] = data['n'] / N_1 # trend liniiowy

    data['qube'] = data['n^2'] / N_2 # trend kwadratowy  
    
    data['y'] = response
    
    for p in range(1,11):
        data[f'sin_{p}'] = np.sin(2*pi*p*data['n']/N) 
        data[f'cosine_{p}'] = np.cos(2*pi*p*data['n']/N) 
            
    
    binary_df = pd.concat([pd.get_dummies(data['DATE'].dt.day_name(),columns=['DATE']),data],axis=1)
    
    binary_df.loc[:,['Monday','Tuesday','Wednesday','Thursday','Friday']] = binary_df.loc[:,['Monday','Tuesday','Wednesday','Thursday','Friday']].astype(int)
    
    # choose appropriate criteria to find optimal pair of sin and cos 
    aic_list = []
    bic_list = []

    for p in range(1,11):
        x=p
        expression = f"y~linear+qube+Wednesday+Monday+Thursday+Tuesday+"
        while p >0:
            expression+= f"sin_{p}"+"+"+f"cosine_{p}+"
            p-=1

        expression =expression.rstrip("+")
        print(expression)

        model = ols(expression,data=binary_df).fit()
        aic_list.append([model.aic,x])
        bic_list.append([model.bic,x])
    
    
    
    model2 = ols("y~linear+qube+sin_1+cosine_1+Wednesday+Monday+Thursday+Tuesday ",data=binary_df).fit( cov_type="HAC",cov_kwds={"maxlags": int( 4*(binary_df.shape[0]/100)**(2/9)  ) })
    
    binary_df['estimated_var'] =model2.fittedvalues

    # normalisation
    
    g = np.exp(binary_df['estimated_var'] / 2)

    TN = len(g)

    binary_df['s_hat'] = TN * g / g.sum()


    binary_df['s_hat'].mean()

    binary_df['deseasonalised_binary'] = binary_df['log_return_intraday'] / binary_df['s_hat']
    
    binary_df.groupby('sesja')['s_hat'].mean().plot()

    plt.show()
    
    return [model2.summary(), binary_df]
    
    
    """    
    match vol_estimation:
        case "variance":
            
            dzienne_zwroty_log = data.query('TIME >= 90000 and TIME <= 165000') # to be moved  
            # pierwszy OPEN w dniu
            daily_open = dzienne_zwroty_log.groupby('DATE')['OPEN'].first()

            # ostatni CLOSE w dniu
            daily_close = dzienne_zwroty_log.groupby('DATE')['CLOSE'].last()

            # dzienne log-stopy (open → close)
            log_return_daily = np.log(daily_close) - np.log(daily_open)

            # odchylenie standardowe
            std_daily = log_return_daily.var(ddof=1) # nie std ale var

                        
                        
            
            pass
        case "garch":
            pass
        case "egarch":
            pass
        case "aparch":
            pass
        case _:
            raise Exception("Invalid vol_estimation parameter. Choose from 'variance', 'garch', 'egarch', or 'aparch'.") 
            
    """ 
        
        
        
            
        


