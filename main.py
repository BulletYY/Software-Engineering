from flexible_fourier_form import flexible_fourier_form
import numpy as np
import pandas as pd

fdt =pd.read_csv("total_data_shifted.csv",sep=";")  

fdt=fdt.loc[:,['DATE','TIME','CLOSE','OPEN']].copy()

fdt['TIME'] = fdt['TIME'].astype(str).str.zfill(6).astype(int)

fdt["TIME_dt"] = pd.to_datetime(fdt["TIME"].astype(str), format="%H%M%S")
fdt["TIME_dt"] = fdt["TIME_dt"] + pd.Timedelta(minutes=5)
fdt["TIME"] = fdt["TIME_dt"].dt.strftime("%H%M%S").astype(int)

fdt['sesja'] = pd.to_datetime( fdt['TIME'].astype(str).str.zfill(6),format='%H%M%S' ).dt.time


print(fdt)

#returns = flexible_fourier_form()


