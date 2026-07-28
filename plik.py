




def flexible_fourier_form(data,N,criteria,vol_estimation,days):
    """ This function is a placeholder for the flexible Fourier form implementation. It is intended 
    to be developed further.    
    
    """
        
    #
    N = 92 # ilosc 

    N_1 = (N+1) /2  # bezposrednio z ksiazki prof gurg i wojtow

    N_2 = (N + 1) * (2*N + 1) / 6  #(N+1)*(N+2)/6 # bezposrednio z ksiazki prof gurg i wojtow

    R_bar = fdt['log_return_intraday'].mean() ## R_bar = fdt['log_return_intraday'].mean() stare 
        
    returns = fdt['log_return_intraday'] ## stare returns = fdt['log_return_intraday']

    sigma_hat = std_daily # 13110


    fdt["R_bar_n"] = fdt.groupby("sesja")["log_return_intraday"].transform("mean")

    returns_centered = returns - fdt["R_bar_n"]




    response = 2*np.log(np.abs(returns_centered) / (sigma_hat / np.sqrt(N) ))  # oblcizenie zmiennej objasnianej y // returns -R_bar 

    
    
    pass




