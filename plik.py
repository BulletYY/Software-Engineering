import numpy as np
import pandas as pd
import seaborn as sns
from statsmodels.formula.api import ols 



def flexible_fourier_form(data: pd.DataFrame, N: int, criteria: str, vol_estimation: str, days: list, plots: bool,session_thresholds:list):
    """ This function is a placeholder for the flexible Fourier form implementation. It is intended 
    to be developed further.    
    
    """
    
    data = data.query('TIME >= 90000 and TIME <= 165000') # wziąłem 9:05 do 16:50 dla starego kodu , Czy Wyrzucac dogrywke czy nie 

    # log stopy zwrotu w obrębie dnia
    data['log_return_intraday'] = (
        data.groupby('DATE')['CLOSE']
        .transform(lambda x: np.log(x).diff()) 
    )

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
    
    model2 = ols("y~linear+qube+sinus_1+cosinus_1+Wednesday+Monday+Thursday+Tuesday   ",data=binary_df).fit( cov_type="HAC",cov_kwds={"maxlags": int( 4*(binary_df.shape[0]/100)**(2/9)  ) })
        
        
    
    pass




