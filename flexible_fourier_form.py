import numpy as np
import pandas as pd
import seaborn as sns
from statsmodels.formula.api import ols 



fdt =pd.read_csv("total_data_shifted.csv",sep=";") 



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
    
    data = data.query(f'TIME >= {session_thresholds[0]} and TIME <= {session_thresholds[1]}') # wziąłem 9:00 do 16:50 dla starego kodu , Czy Wyrzucac dogrywke czy nie 

    # log stopy zwrotu w obrębie dnia
    data['log_return_intraday'] = ( data.groupby('DATE')['CLOSE'].transform(lambda x: np.log(x).diff()))

    data = data.dropna(subset=['log_return_intraday'])
    data['abs_zwroty'] = np.abs(data['log_return_intraday'])

    #print("number of days:", data['DATE'].nunique())
    #print("number of rows:", len(data))
    #print(data.groupby('DATE').size().value_counts().sort_index())
        
    data['DATE'] =pd.to_datetime(data['DATE'],format='%Y%m%d')
        
    
    data['dni_tygodnia'] =data['DATE'].dt.day_name()
        
    #
    N = 92 # ilosc 

    N_1 = (N+1) /2  # bezposrednio z ksiazki prof gurg i wojtow

    N_2 = (N + 1) * (2*N + 1) / 6  #(N+1)*(N+2)/6 # bezposrednio z ksiazki prof gurg i wojtow

    R_bar = data['log_return_intraday'].mean() ## R_bar = data['log_return_intraday'].mean() stare 
        
    returns = data['log_return_intraday'] ## stare returns = data['log_return_intraday']

    # here based on the vol_estimation parameter, we can choose different methods to estimate volatility , to be implemented match case statement 
    
    
    match vol_estimation:
        case "variance":
            pass
        case "garch":
            pass
        case "egarch":
            pass
        case "aparch":
            pass
        case _:
            raise Exception("Invalid vol_estimation parameter. Choose from 'variance', 'garch', 'egarch', or 'aparch'.") 
        
     
     
    
    sigma_hat = std_daily # 13110


    data["R_bar_n"] = data.groupby("sesja")["log_return_intraday"].transform("mean")

    returns_centered = returns - data["R_bar_n"]




    response = 2*np.log(np.abs(returns_centered) / (sigma_hat / np.sqrt(N) ))  # oblcizenie zmiennej objasnianej y // returns -R_bar 

    
        
    aic_list = []
    bic_list = []

    # while i dodawac dp espression += dopóki p ==0 i odejmowac z kazdym while 
    for p in range(1,11):
        x=p
        expression = f"y~linear+qube+Friday+Monday+Thursday+Tuesday+"
        while p >0:
            expression+= f"sinus_{p}"+"+"+f"cosinus_{p}+"
            p-=1

        expression =expression.rstrip("+")
        print(expression)

        model = ols(expression,data=data).fit()
        aic_list.append([model.aic,x])
        bic_list.append([model.bic,x])
    
    model2 = ols("y~linear+qube+sinus_1+cosinus_1+Wednesday+Monday+Thursday+Tuesday   ",data=data).fit( cov_type="HAC",cov_kwds={"maxlags": int( 4*(data.shape[0]/100)**(2/9)  ) })
    
    
    
        
        


