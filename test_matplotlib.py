import flet as ft
from flet.matplotlib_chart import MatplotlibChart

import time
from datetime import datetime
import numpy as np

import matplotlib.pyplot as plt

def main(page: ft.page):
    
    fig, ax = plt.subplots()

    x = np.arange(0,10, 0.1)
    y = np.random.rand(len(x))
    ax.plot(x, y)

    
    t = ft.Text(size=30)
    plot = MatplotlibChart(fig, expand=True)
    page.add(t)
    page.add(plot)    
    
    while True:

        now_str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        t.value = now_str
        
        ax.clear()
        x = np.arange(0,10, 0.1)
        y = np.random.rand(len(x))
        ax.plot(x, y)
        
        plot.value = fig
        
        page.update()
        time.sleep(1)
        

ft.app(target=main)