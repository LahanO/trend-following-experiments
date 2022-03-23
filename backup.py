import pandas as pd
import numpy as np
import os
from pathlib import Path
from pdb import set_trace
import operator
import asyncio
import traceback
import time
from datetime import datetime
import matplotlib.pyplot as plt
from ast import literal_eval
from collections import OrderedDict
from collections import Counter
import itertools
import pickle
import math
import copy
import gc

async def get_performance_log_file_names():
    #get a list of files in Trades_log directory
    file_names = os.listdir(os.path.abspath(os.getcwd())+ '/performance_log/')
    file_names = [filename for filename in file_names if filename.endswith('.csv')]
    exchanges = list(set([item.split('-')[0] for item in file_names]))
    return file_names

def get_optimization_log_file_names():
    #get a list of files in Trades_log directory
    file_names = os.listdir(os.path.abspath(os.getcwd())+ '/Optimization/')
    file_names = [filename for filename in file_names if filename.endswith('.pkl')]
    exchanges = list(set([item.split('-')[0] for item in file_names]))
    return file_names

def convert_trade_log_csv_to_df(file_name):
    file_name = Path(os.path.abspath(os.getcwd())+ '/performance_log/' + file_name)
    #if file exists, convert to df, else print error
    if file_name.is_file():
        trade_log_df = pd.read_csv(file_name)
    else:
        print('Func convert_trade_log_csv_to_df: \n', file_name,'does not exist')
    return trade_log_df
 
async def simulate_trades(performance_log_df, duration, order_life,
                          exchange, symbol, variable_dict, config_no):
    #initialize tracking variables
    earnings = 0
    Tearnings = 0
    profit = 0
    loss = 0
    pr = 0
    Volume = 0
    ts = 0
    bs = 0
    ss = 0
    tc = 0
    initialize = None
    initialized = None
    conserved = None
    trade = None
    trade_count = 0
    successful_trade_count = 0
    successful_buy = 0
    successful_sell = 0
    buy = 0
    sell = 0
    long_layer_grad_list = []
    mid_layer_grad_list = []
    short_layer_grad_list = []
    long_low_grad = 0
    long_high_grad = 0
    mid_low_grad = 0
    mid_high_grad = 0
    init_mid_high_grad = 0
    low_low_grad = 0
    low_high_grad = 0
    
    #filter out the duration from the dataframe
    now = time.time()
    since = now -int(24*60*60*duration[0])
    to = now - int(24*60*60*duration[1])
    performance_log_df['Timestamp'] = pd.to_numeric(performance_log_df['Timestamp'])
    now = (now/10**len(str(int(now))))*10**(len(str(int(performance_log_df['Timestamp'][0]))))
    since = (since/10**len(str(int(since))))*10**(len(str(int(performance_log_df['Timestamp'][0]))))
    to = (to/10**len(str(int(to))))*10**(len(str(int(performance_log_df['Timestamp'][0]))))

    performance_log_df = performance_log_df[(performance_log_df['Timestamp'] > since)].reset_index()
    performance_log_df = performance_log_df[(performance_log_df['Timestamp'] < to)].reset_index()
    
    if len(performance_log_df['low']) > 0:
        init_price = performance_log_df['open'][0]
##    set_trace()
    #loop through rows of dataframe
    for row in range(int((len(performance_log_df.index)))):
        '''UNDERLINING PHILOSOPHY, IS TO BRUTE FORCE PROFIT FROM THE MARKET: MAKE PROFIT IF IT CAN BE MADE
           SAFELY, AVOID LOSSES WITH NO DETRIMENT TO PROFITS'''
##        value_step_0 = performance_log_df.loc[row, 'value state']
        price_step_0 = performance_log_df.loc[row, 'open']
##        price_step_0 = performance_log_df.loc[row, 'low'] + (performance_log_df.loc[row, 'high'] -
##                                                             performance_log_df.loc[row, 'low'])/4
        vol = 150/price_step_0
        #HISTORY LOG
##        if row >= 10:
##            value_step_10 = performance_log_df.loc[row-10, 'value state']
##            price_step_10 = performance_log_df.loc[row-10, 'open']
####            price_step_10 = performance_log_df.loc[row-10, 'low'] + (performance_log_df.loc[row-10, 'high'] -
####                                                                     performance_log_df.loc[row-10, 'low'])/4
##            if row >= 11:
##                price_change_step_10 = performance_log_df.loc[row-11, 'open']
####                price_change_step_10 = performance_log_df.loc[row-11, 'low'] + (performance_log_df.loc[row-11, 'high'] -
####                                                                                performance_log_df.loc[row-11, 'low'])/4
##            else:
##                price_change_step_10 = 0
##        else:
##            value_step_10 = performance_log_df.loc[row, 'value state']
##            price_step_10 = performance_log_df.loc[row, 'open']
####            price_step_10 = performance_log_df.loc[row, 'low'] + (performance_log_df.loc[row, 'high'] -
####                                                                  performance_log_df.loc[row, 'low'])/4
##            price_change_step_10 = 0
##        if row >= 9:
##            value_step_9 = performance_log_df.loc[row-9, 'value state']
##            price_step_9 = performance_log_df.loc[row-9, 'open']
####            price_step_9 = performance_log_df.loc[row-9, 'low'] + (performance_log_df.loc[row-9, 'high'] -
####                                                                   performance_log_df.loc[row-9, 'low'])/4
##            price_change_step_9 = price_step_9 - price_step_10
##        else:
##            value_step_9 = performance_log_df.loc[row, 'value state']
##            price_step_9 = performance_log_df.loc[row, 'open']
####            price_step_9 = performance_log_df.loc[row, 'low'] + (performance_log_df.loc[row, 'high'] -
####                                                                 performance_log_df.loc[row, 'low'])/4
##            price_change_step_9 = 0
##        if row >= 8:
##            value_step_8 = performance_log_df.loc[row-8, 'value state']
##            price_step_8 = performance_log_df.loc[row-8, 'open']
####            price_step_8 = performance_log_df.loc[row-8, 'low'] + (performance_log_df.loc[row-8, 'high'] -
####                                                                   performance_log_df.loc[row-8, 'low'])/4
##            price_change_step_8 = price_step_8 - price_step_9
##        else:
##            value_step_8 = performance_log_df.loc[row, 'value state']
##            price_step_8 = performance_log_df.loc[row, 'open']
####            price_step_8 = performance_log_df.loc[row, 'low'] + (performance_log_df.loc[row, 'high'] -
####                                                                 performance_log_df.loc[row, 'low'])/4
##            price_change_step_8 = 0
##        if row >= 7:
##            value_step_7 = performance_log_df.loc[row-7, 'value state']
##            price_step_7 = performance_log_df.loc[row-7, 'open']
####            price_step_7 = performance_log_df.loc[row-7, 'low'] + (performance_log_df.loc[row-7, 'high'] -
####                                                                   performance_log_df.loc[row-7, 'low'])/4
##            price_change_step_7 = price_step_7 - price_step_8
##        else:
##            value_step_7 = performance_log_df.loc[row, 'value state']
##            price_step_7 = performance_log_df.loc[row, 'open']
####            price_step_7 = performance_log_df.loc[row, 'low'] + (performance_log_df.loc[row, 'high'] -
####                                                                 performance_log_df.loc[row, 'low'])/4
##            price_change_step_7 = 0
##        if row >= 6:
##            value_step_6 = performance_log_df.loc[row-6, 'value state']
##            price_step_6 = performance_log_df.loc[row-2, 'open']
####            price_step_6 = performance_log_df.loc[row-2, 'low'] + (performance_log_df.loc[row-6, 'high'] -
####                                                                   performance_log_df.loc[row-6, 'low'])/4
##            price_change_step_6 = price_step_6 - price_step_7
##        else:
##            value_step_6 = performance_log_df.loc[row, 'value state']
##            price_step_6 = performance_log_df.loc[row, 'open']
####            price_step_6 = performance_log_df.loc[row, 'low'] + (performance_log_df.loc[row, 'high'] -
####                                                                 performance_log_df.loc[row, 'low'])/4
##            price_change_step_6 = 0
        if row >= 5:
            price_step_5 = performance_log_df.loc[row-5, 'open']
        else:
            price_step_5 = performance_log_df.loc[row, 'open']
        if row >= 4:
            price_step_4 = performance_log_df.loc[row-4, 'open']
        else:
            price_step_4 = performance_log_df.loc[row, 'open'] 
        if row >= 3:
            price_step_3 = performance_log_df.loc[row-3, 'open']
        else:
            price_step_3 = performance_log_df.loc[row, 'open']
        if row >= 2:
            price_step_2 = performance_log_df.loc[row-2, 'open']
        else:
            price_step_2 = performance_log_df.loc[row, 'open']
        if row >= 1:
            price_step_1 = performance_log_df.loc[row-1, 'open']
        else:
            price_step_1 = performance_log_df.loc[row, 'open']
            

        
##        value_history = [value_step_0, value_step_1, value_step_2, value_step_3, value_step_4, value_step_5,
##                         value_step_6, value_step_7, value_step_8, value_step_9, value_step_10]
##        price_history = [price_step_0, price_step_1, price_step_2, price_step_3, price_step_4, price_step_5 ,
##                         price_step_6, price_step_7, price_step_8, price_step_9, price_step_10]
        price_history = [price_step_0, price_step_1, price_step_2, price_step_3, price_step_4, price_step_5]
##        
##        price_change_history = [price_change_step_0, price_change_step_1, price_change_step_2, price_change_step_3,
##                                price_change_step_4, price_change_step_5 , price_change_step_6, price_change_step_7,
##                                price_change_step_8, price_change_step_9, price_change_step_10]
        #LAYER STAGE
##        init_layer_grad = np.mean(np.gradient([init_price, price_step_0]))
##        long_layer_list = [value_step_9, value_step_8, value_step_7, value_step_6,
##                           value_step_5, value_step_4, value_step_3, value_step_2, value_step_1,
##                           valuestep_0]
##        long_layer_grad = np.mean(np.gradient([value_step_9, value_step_0]))
##        mid_layer_grad = np.mean(np.gradient([value_step_7, value_step_0]))
##        short_layer_grad = np.mean(np.gradient([value_step_1, value_step_0]))
        
##        long_layer_grad = np.mean(np.gradient([price_step_5, price_step_0]))
##        mid_layer_grad = np.mean(np.gradient([price_step_3, price_step_0]))
##        short_layer_grad = np.mean(np.gradient([price_step_1, price_step_0]))
        
        long_layer_grad = np.degrees(np.arctan((price_step_0-price_step_5)/30))
        mid_layer_grad = np.degrees(np.arctan((price_step_0-price_step_3)/20))
        short_layer_grad = np.degrees(np.arctan((price_step_0-price_step_2)/15))
        
        long_layer_grad_list.append(long_layer_grad)
        mid_layer_grad_list.append(mid_layer_grad)
        short_layer_grad_list.append(short_layer_grad)
        
        #FILTER STAGE
##        '''OPTION 1'''
##        if all(item >= 0 for item in value_history[0:1]):
##            initialize = True
##        else:
##            initialize = False

        #OPTION 2
        '''LAYERED WITH SIGNALING'''
##        if value_step_0 >= 0:
##            initialize = True
##        else:
##            initialize = False
##        len([item for item in value_history[:9] if item >= 0])/len(value_history[:9]) >= 0.6
        '''
        if there have been a lot of reds ad the reds are slowing, buy,
        if there have been a lot of greens and the greens are slowing, sell.
        '''
        long_low_grad = -45
        long_high_grad = 45
        
        mid_low_grad = -45
        mid_high_grad = 45
            
        low_low_grad = -45
        low_high_grad = 45
        
##        long_low_grad = np.min([item for item in long_layer_grad_list if item <= 0][-2:])
##        long_high_grad = np.max([item for item in long_layer_grad_list if item >= 0][-2:])
##        
##        mid_low_grad = np.min([item for item in mid_layer_grad_list if item <= 0][-2:])
##        mid_high_grad = np.max([item for item in mid_layer_grad_list if item >= 0][-2:])
##            
##        low_low_grad = np.min([item for item in short_layer_grad_list if item <= 0][-2:])
##        low_high_grad = np.max([item for item in short_layer_grad_list if item >= 0][-2:])
       
##        if long_layer_grad > long_high_grad:
##            set_trace()
##        variable_dict = OrderedDict([('initialize_8_10_mid_low_low_low', False), ('initialize_8_10_mid_low_low_low0', False),
##                                     ('initialize_8_10_mid_low_0low_high', False), ('initialize_8_10_mid_low_low_high', False),
##                                     
##                                     ('initialize_8_10_mid_low0_low_low', False), ('initialize_8_10_mid_low0_low_low05', False),
##                                     ('initialize_8_10_mid_low0_0low_high6', False), ('initialize_8_10_mid_low0_low_high', False),
##
##                                     ('initialize_8_10_0mid_high_low_low', False), ('initialize_8_10_0mid_high_low_low09', True),
##                                     ('initialize_8_10_0mid_high_0low_high10', True), ('initialize_8_10_0mid_high_low_high', False),
##
##                                     ('initialize_8_10_mid_high_low_low', False), ('initialize_8_10_mid_high_low_low0', False),
##                                     ('initialize_8_10_mid_high_0low_high', True), ('initialize_8_10_mid_high_low_high', True),
##
##
##                                     ('initialize_05_07_mid_low_low_low', True), ('initialize_05_07_mid_low_low_low0', True),
##                                     ('initialize_05_07_mid_low_0low_high', True), ('initialize_05_07_mid_low_low_high', True),
##
##                                     ('initialize_05_07_mid_low0_low_low', True), ('initialize_05_07_mid_low0_low_low021', False),
##                                     ('initialize_05_07_mid_low0_0low_high22', False), ('initialize_05_07_mid_low0_low_high23', False),
##
##                                     ('initialize_05_07_0mid_high_low_low', True), ('initialize_05_07_0mid_high_low_low025', False),
##                                     ('initialize_05_07_0mid_high_0low_high26', False), ('initialize_05_07_0mid_high_low_high', False),
##
##                                     ('initialize_05_07_mid_high_low_low', True), ('initialize_05_07_mid_high_low_low0', True),
##                                     ('initialize_05_07_mid_high_0low_high', True), ('initialize_05_07_mid_high_low_high', True),
##
##
##                                     ('initialize_3_4_mid_low_low_low32', False), ('initialize_3_4_mid_low_low_low033', False),
##                                     ('initialize_3_4_mid_low_0low_high', True), ('initialize_3_4_mid_low_low_high', True),
##                                     
##                                     ('initialize_3_4_mid_low0_low_low36', False), ('initialize_3_4_mid_low0_low_low037', False),
##                                     ('initialize_3_4_mid_low0_0low_high38', False), ('initialize_3_4_mid_low0_low_high', True),
##                                     
##                                     ('initialize_3_4_0mid_high_low_low', True), ('initialize_3_4_0mid_high_low_low041', False),
##                                     ('initialize_3_4_0mid_high_0low_high42', False), ('initialize_3_4_0mid_high_low_high43', False),
##                                     
##                                     ('initialize_3_4_mid_high_low_low', True), ('initialize_3_4_mid_high_low_low0', True),
##                                     ('initialize_3_4_mid_high_0low_high46', False), ('initialize_3_4_mid_high_low_high', True)])
##0.8 <= len([item for item in value_history[:10] if item >= 0])/len(value_history[:10]) <= 1
    
        
##long_high_grad <= long_layer_grad:
##('initialize_8_10_0mid_high_low_low0', False), ('initialize_8_10_0mid_high_0low_high', False),
##('initialize_8_10_mid_high_0low_high', False), ('initialize_8_10_mid_high_low_high', False)
##        if long_high_grad <= long_layer_grad:
##            if mid_layer_grad <= mid_low_grad:
##                initialize = False
##            if mid_low_grad <= mid_layer_grad <= 0:
##                initialize = True
##            if 0 <= mid_layer_grad <= mid_high_grad:
##                initialize = True
##            if mid_high_grad <= mid_layer_grad:
##                initialize = False
##        elif 0 <= long_layer_grad <= long_high_grad:
##            if mid_layer_grad <= mid_low_grad:
##                initialize = False
##            if mid_low_grad <= mid_layer_grad <= 0:
##                initialize = True
##            if 0 <= mid_layer_grad <= mid_high_grad:
##                initialize = True
##            if mid_high_grad <= mid_layer_grad:
##                initialize = True
##        elif long_low_grad <= long_layer_grad <= 0:
##            if mid_layer_grad <= mid_low_grad:
##                initialize = False
##            if mid_low_grad <= mid_layer_grad <= 0:
##                initialize = False
##            if 0 <= mid_layer_grad <= mid_high_grad:
##                initialize = False
##            if mid_high_grad <= mid_layer_grad:
##                initialize = True
##        elif long_layer_grad <= long_low_grad:
##            if mid_layer_grad <= mid_low_grad:
##                initialize = False
##            if mid_low_grad <= mid_layer_grad <= 0:
##                initialize = False
##            if 0 <= mid_layer_grad <= mid_high_grad:
##                initialize = False
##            if mid_high_grad <= mid_layer_grad:
##                initialize = False
##        else:
##            initialize = False
##
##        if long_high_grad <= long_layer_grad:
##            if mid_layer_grad <= mid_low_grad:
##                if short_layer_grad <= low_low_grad:
##                    initialize = False
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = False
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = False
##                elif low_high_grad <= short_layer_grad:
##                    initialize = False
##            if mid_low_grad <= mid_layer_grad <= 0:
##                if short_layer_grad <= low_low_grad:
##                    initialize = False
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[0]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[1]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = False
##            if 0 <= mid_layer_grad <= mid_high_grad:
##                if short_layer_grad <= low_low_grad:
##                    initialize = False
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[2]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[3]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = False
##            if mid_high_grad <= mid_layer_grad:
##                if short_layer_grad <= low_low_grad:
##                    initialize = False
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = False
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = False
##                elif low_high_grad <= short_layer_grad:
##                    initialize = False
##        elif 0 <= long_layer_grad <= long_high_grad:
##            if mid_layer_grad <= mid_low_grad:
##                if short_layer_grad <= low_low_grad:
##                    initialize = False
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = False
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = False
##                elif low_high_grad <= short_layer_grad:
##                    initialize = False
##            if mid_low_grad <= mid_layer_grad <= 0:
##                if short_layer_grad <= low_low_grad:
##                    initialize = False
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[4]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[5]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[6]]
##            if 0 <= mid_layer_grad <= mid_high_grad:
##                if short_layer_grad <= low_low_grad:
##                    initialize = False
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[7]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[8]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = False
##            if mid_high_grad <= mid_layer_grad:
##                if short_layer_grad <= low_low_grad:
##                    initialize = False
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = False
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = False
##                elif low_high_grad <= short_layer_grad:
##                    initialize = False
##        elif long_low_grad <= long_layer_grad <= 0:
##            if mid_layer_grad <= mid_low_grad:
##                if short_layer_grad <= low_low_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[9]]
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[10]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = False
##                elif low_high_grad <= short_layer_grad:
##                    initialize = False
##            if mid_low_grad <= mid_layer_grad <= 0:
##                if short_layer_grad <= low_low_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[11]]
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[12]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[13]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = False
##            if 0 <= mid_layer_grad <= mid_high_grad:
##                if short_layer_grad <= low_low_grad:
##                    initialize = False
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[14]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[15]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[16]]
##            if mid_high_grad <= mid_layer_grad:
##                if short_layer_grad <= low_low_grad:
##                    initialize = False
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = False
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[17]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = False
##        if 0 <= len([item for item in value_history[:10] if item >= 0])/len(value_history[:10]) <= 0.2:
##            if mid_layer_grad <= mid_low_grad:
##                if short_layer_grad <= low_low_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[48]]
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[49]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[50]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[51]]
##            if mid_low_grad <= mid_layer_grad <= 0:
##                if short_layer_grad <= low_low_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[52]]
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[53]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[54]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[55]]
##            if 0 <= mid_layer_grad <= mid_high_grad:
##                if short_layer_grad <= low_low_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[56]]
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[57]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[58]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[59]]
##            if mid_high_grad <= mid_layer_grad:
##                if short_layer_grad <= low_low_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[60]]
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[61]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[62]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[63]]
##        else:
##            initialize = False

        if long_high_grad <= long_layer_grad:
            if 0 <= mid_layer_grad:
                if 0 <= short_layer_grad:
                    initialize = variable_dict[list(variable_dict.keys())[0]]
                elif short_layer_grad <= 0:
                    initialize = variable_dict[list(variable_dict.keys())[1]]
            if mid_layer_grad <= 0:
                if 0 <= short_layer_grad:
                    initialize = variable_dict[list(variable_dict.keys())[2]]
                elif short_layer_grad <= 0:
                    initialize = variable_dict[list(variable_dict.keys())[3]]
        if 0 <= long_layer_grad <= long_high_grad:
            if 0 <= mid_layer_grad:
                if 0 <= short_layer_grad:
                    initialize = variable_dict[list(variable_dict.keys())[4]]
                elif short_layer_grad <= 0:
                    initialize = variable_dict[list(variable_dict.keys())[5]]
            if mid_layer_grad <= 0:
                if 0 <= short_layer_grad:
                    initialize = variable_dict[list(variable_dict.keys())[6]]
                elif short_layer_grad <= 0:
                    initialize = variable_dict[list(variable_dict.keys())[7]]
        if long_low_grad <= long_layer_grad <= 0:
            if 0 <= mid_layer_grad:
                if 0 <= short_layer_grad:
                    initialize = variable_dict[list(variable_dict.keys())[8]]
                elif short_layer_grad <= 0:
                    initialize = variable_dict[list(variable_dict.keys())[9]]
            if mid_layer_grad <= 0:
                if 0 <= short_layer_grad:
                    initialize = variable_dict[list(variable_dict.keys())[10]]
                elif short_layer_grad <= 0:
                    initialize = variable_dict[list(variable_dict.keys())[11]]
        if long_layer_grad <= long_low_grad:
            if 0 <= mid_layer_grad:
                if 0 <= short_layer_grad:
                    initialize = variable_dict[list(variable_dict.keys())[12]]
                elif short_layer_grad <= 0:
                    initialize = variable_dict[list(variable_dict.keys())[13]]
            if mid_layer_grad <= 0:
                if 0 <= short_layer_grad:
                    initialize = variable_dict[list(variable_dict.keys())[14]]
                elif short_layer_grad <= 0:
                    initialize = variable_dict[list(variable_dict.keys())[15]]
##        elif 0 <= long_layer_grad <= long_high_grad:
##            if mid_layer_grad <= mid_low_grad:
##                if short_layer_grad <= low_low_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[16]]
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[17]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[18]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[19]]
##            if mid_low_grad <= mid_layer_grad <= 0:
##                if short_layer_grad <= low_low_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[20]]
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[21]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[22]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[23]]
##            if 0 <= mid_layer_grad <= mid_high_grad:
##                if short_layer_grad <= low_low_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[24]]
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[25]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[26]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[27]]
##            if mid_high_grad <= mid_layer_grad:
##                if short_layer_grad <= low_low_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[28]]
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[29]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[30]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[31]]
##        elif long_low_grad <= long_layer_grad <= 0:
##            if mid_layer_grad <= mid_low_grad:
##                if short_layer_grad <= low_low_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[32]]
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[33]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[34]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[35]]
##            if mid_low_grad <= mid_layer_grad <= 0:
##                if short_layer_grad <= low_low_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[36]]
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[37]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[38]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[39]]
##            if 0 <= mid_layer_grad <= mid_high_grad:
##                if short_layer_grad <= low_low_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[40]]
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[41]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[42]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[43]]
##            if mid_high_grad <= mid_layer_grad:
##                if short_layer_grad <= low_low_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[44]]
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[45]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[46]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[47]]
##        if 0 <= len([item for item in value_history[:10] if item >= 0])/len(value_history[:10]) <= 0.2:
##            if mid_layer_grad <= mid_low_grad:
##                if short_layer_grad <= low_low_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[48]]
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[49]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[50]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[51]]
##            if mid_low_grad <= mid_layer_grad <= 0:
##                if short_layer_grad <= low_low_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[52]]
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[53]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[54]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[55]]
##            if 0 <= mid_layer_grad <= mid_high_grad:
##                if short_layer_grad <= low_low_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[56]]
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[57]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[58]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[59]]
##            if mid_high_grad <= mid_layer_grad:
##                if short_layer_grad <= low_low_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[60]]
##                elif low_low_grad <= short_layer_grad <= 0:
##                    initialize = variable_dict[list(variable_dict.keys())[61]]
##                elif 0 <= short_layer_grad <= low_high_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[62]]
##                elif low_high_grad <= short_layer_grad:
##                    initialize = variable_dict[list(variable_dict.keys())[63]]
##        else:
##            initialize = False
##
##            
##        if mid_layer_grad >= 0.95*mid_high_grad and \
##           (0.05*low_high_grad <= short_layer_grad <= 0.45*low_high_grad and
##            len([item for item in value_history[:9] if item >= 0])/len(value_history[:9]) >= 0.7):
##            '''HEEEEEEEEEEEEEEEEERRRRRRRRRRRRRRRREEEEEEEEEEEEEEEEEEE
##            short layer changes everything
##            note how it affects each symbol differently
##            '''
##            initialize = False
##        if 0.8 <= len([item for item in value_history[:10] if item >= 0])/len(value_history[:10]) <= 1:
##            initialize = True
##        elif 0.5 <= len([item for item in value_history[:10] if item >= 0])/len(value_history[:10]) <= 0.7 and\
##             mid_layer_grad <= mid_low_grad and short_layer_grad <= 0.95*low_low_grad:
##            initialize = True
##        elif 0.5 <= len([item for item in value_history[:10] if item >= 0])/len(value_history[:10]) <= 0.7 and\
##             mid_low_grad <= mid_layer_grad <= mid_high_grad:
##            if short_layer_grad <= low_low_grad:
##                initialize = True
##            elif low_low_grad <= short_layer_grad <= low_high_grad:
##                initialize = True
##            elif low_high_grad <= short_layer_grad:
##                initialize = True    
##            '''
##            NEW
##            NEEDS WORK
##            DOESN'T PROTECT THE DOWN SIDE
##            '''
####            initialize = True
##        elif 0.5 <= len([item for item in value_history[:10] if item >= 0])/len(value_history[:10]) <= 0.7 and \
##             mid_high_grad <= mid_layer_grad:
##            '''
##            NEW
##            NEEDS WORK
##            DOESN'T PROTECT THE DOWN SIDE
##            '''
##            initialize = True
####        elif 0.5 <= len([item for item in value_history[:10] if item >= 0])/len(value_history[:10]) <= 0.7:
####            '''
####            NEW
####            NEEDS WORK
####            '''
####            initialize = False
##        elif 0.3 <= len([item for item in value_history[:10] if item >= 0])/len(value_history[:10]) <= 0.4 and\
##             mid_layer_grad <= 1*mid_low_grad and \
##             low_low_grad <= short_layer_grad <= low_high_grad:
##            '''
##            NEW
##            NEEDS WORK
##            '''
##            initialize = True
##        elif 0.3 <= len([item for item in value_history[:10] if item >= 0])/len(value_history[:10]) <= 0.4 and\
##             1*mid_low_grad <= mid_layer_grad and \
##             not low_low_grad <= short_layer_grad <= low_high_grad:
##            '''
##            NEW
##            NEEDS WORK
##            '''
##            initialize = True
####        elif 0.3 <= len([item for item in value_history[:10] if item >= 0])/len(value_history[:10]) <= 0.4:
####            '''
####            NEW
####            NEEDS WORK
####            '''
####            initialize = False
##        elif len([item for item in value_history[:10] if item >= 0])/len(value_history[:10]) <= 0.2:
##            initialize = False
##        else:
##            initialize = False
##
####        if initialize == True:
####            if short_layer_grad < 0:
####                initialize = False
####            else:
####                initialize = True
##
####        if long_layer_grad > 0:
####            initialize = True
####        else:
####            initialize = False
####            
####        if init_layer_grad > 0:
####            initialize = True
####        else:
####            initialize = False
##
##        #TRADE FILTER
##        if initialize == True:
##            if value_step_1 > 0:
##                trade = True
##            else:
##                trade = False
                
        '''ANALYSIS'''
        val_state = 0
        high = performance_log_df.loc[row, 'high']
        #EVALUATION STAGE
        if initialize == True:
            if row+1 < len(performance_log_df.index):
                if initialized == True:
                    val_state = 0
##                    val_state = performance_log_df.loc[row, 'ask price0']*initial_vol - \
##                                initial_price*initial_vol
##                    initial_price = performance_log_df.loc[row, 'ask price0']
##                    if trade == True:
##                        val_state = val_state + 0*((price_step_0*(1.0035)*vol) 
##                                                 - (price_step_0*vol)
##                                                 - (price_step_0*(1.0035)*vol +
##                                                    (price_step_0*vol))*0.001)
##                        symbol_perfomance_dict['Volume'] += 150*0  
                else:
                    val_state = 0
                    initial_high = performance_log_df.loc[row, 'high']
                    initial_price = price_step_0
##                    initial_price = performance_log_df.loc[row, 'ask price0']
                    initial_vol = 150/initial_price
                    trade_count += 1
                    buy += 1
                    if initial_price >= performance_log_df.loc[row, 'low']:
                        successful_trade_count += 1
                        successful_buy += 1
                        Volume += 150
                        
##                    val_state = -(initial_price*initial_vol*0.001)
            initialized = True
            conserved = False
        else:
            if conserved == False:
                sell_price = (performance_log_df.loc[row, 'low'] + \
                            (performance_log_df.loc[row, 'high'] -
                             performance_log_df.loc[row, 'low'])/4)*1.0035
                sell_price = performance_log_df.loc[row, 'high'] - (performance_log_df.loc[row, 'high'] -
                                                                    performance_log_df.loc[row, 'low'])/4
##                sell_price = (performance_log_df.loc[row, 'bid price0'] +
##                              performance_log_df.loc[row, 'ask price0'] )/2
                sell_price = performance_log_df.loc[row, 'bid price0']
                val_state = sell_price*initial_vol - \
                            initial_price*initial_vol - \
                            (sell_price*initial_vol +
                            initial_price*initial_vol)*0.001
                
##                val_state = val_state + 0*((price_step_1*vol) 
##                                         - (sell_price*vol)
##                                         - (price_step_1*vol +
##                                            (sell_price*vol))*0.001)
##                
                trade_count += 1
                sell += 1
                if sell_price <= performance_log_df.loc[row, 'high']:
                    successful_trade_count += 1
                    successful_sell += 1
                    Volume += 150
                else:
                    val_state = 0
                initialized= False
                conserved = True
                    

        #DOCUMENTATION STAGE
        if Tearnings > 3:
            earnings += Tearnings
            Tearnings = 0
            
        Tearnings += val_state
        if val_state >= 0:
            profit += val_state
        else:
            loss += val_state
        tc += 1

    if loss != 0:
        pr = profit/abs(loss)
    else:
        pr = profit/1
    if profit !=0:
        ts = successful_trade_count/trade_count
        bs = successful_buy/buy
        ss = successful_sell/sell
    return Tearnings, earnings, profit, loss, Volume

async def check_symbol_performance_L1(performance_log_df_dict, fees, fee_rate, fee_cushion,
                                      duration, order_life, symbol_perfomance_dict, variable_dict, config_no):
    try:
        #convert file to dataframe
        performance_log_df = performance_log_df_dict[0]
        file_name = performance_log_df_dict[1]
        #get the exchange name, symbol, timeframe, fee
        symbol = file_name.split('-')[1].replace('USDT', '/USDT')
        if '.csv' in symbol:
            symbol = symbol.replace('.csv', '')
        exchange = file_name.split('-')[0]
        
        #evaluate trades
        Tearnings, earnings, profit, loss, Volume = await simulate_trades(performance_log_df, duration,order_life,
                                                                          exchange, symbol, variable_dict, config_no)
        if Volume > 0:
##            symbol_perfomance_dict[config_no][exchange][symbol]['Tearnings'] = copy.deepcopy(Tearnings)
##            symbol_perfomance_dict[config_no][exchange][symbol]['earnings'] = copy.deepcopy(earnings)
            symbol_perfomance_dict[config_no][exchange][symbol] = OrderedDict()
##            symbol_perfomance_dict[config_no][exchange][symbol]['profit'] = None
##            symbol_perfomance_dict[config_no][exchange][symbol]['loss'] = None
##            symbol_perfomance_dict[config_no][exchange][symbol]['Volume'] = None
            symbol_perfomance_dict[config_no][exchange][symbol]['profit'] = copy.deepcopy(profit)
            symbol_perfomance_dict[config_no][exchange][symbol]['loss'] = copy.deepcopy(loss)
            symbol_perfomance_dict[config_no][exchange][symbol]['Volume'] = copy.deepcopy(Volume)
    except:
        print(traceback.format_exc(), file_name)
    return None

async def optimize_L1(performance_log_df_dict, fees, fee_rate, fee_cushion, duration, order_life,
                      symbol_perfomance_dict, config, config_no):
    for item in long_gradient_list:
        for mid_grad in mid_gradient_list:
            for low_grad in low_gradient_list:
                var_name = 'initialize_' + str(item)  + '_' + str(mid_grad) + '_' + str(low_grad)
                variable_dict[var_name] = False
    try:
        for key in variable_dict.keys():
            variable_dict[key] = config[list(variable_dict.keys()).index(key)]
        
        tasks = [asyncio.create_task(check_symbol_performance_L1(performance_log_df_dict[symbol],
                                                                 fees, fee_rate, fee_cushion,
                                                                 duration, order_life,
                                                                 symbol_perfomance_dict,
                                                                 variable_dict, config_no))
                  for symbol in performance_log_df_dict.keys()
                 ]
        if tasks:
            await asyncio.gather(*tasks)
        symbol_perfomance_dict[config_no]['config'] = copy.deepcopy(variable_dict)
        
    except:
        print(traceback.format_exc())
    return None

async def optimize_L0(fees, fee_rate, fee_cushion, duration, order_life):
    l = [False, True]
    p_list = list(itertools.product(l, repeat=16))[:30000]
    config_len = range(0, len(p_list))
    file_names = await get_performance_log_file_names()
    
    performance_log_df_dict = OrderedDict()
    
    for file_name in file_names:
        symbol = file_name.split('-')[1].replace('USDT', '/USDT')
        performance_log_df_dict[symbol] = [convert_trade_log_csv_to_df(file_name),
                                           file_name]
    symbol_perfomance_dict = await initialize_symbol_perfomance_dict(file_names, config_len)
    try:
        for config in p_list:
            await optimize_L1(performance_log_df_dict, fees,
                              fee_rate, fee_cushion,
                              duration, order_life,
                              symbol_perfomance_dict,
                              config,
                              config_no=p_list.index(config)
                              )
    except:
        print(traceback.format_exc())
    
    return symbol_perfomance_dict, config_len

def optimize(fees, fee_rate, fee_cushion, duration, order_life):
    tic = time.time()
    symbol_perfomance_dict, config_len = asyncio.run(optimize_L0(fees, fee_rate, fee_cushion, duration, order_life))

    for config_no in symbol_perfomance_dict.keys():
        symbol_perfomance_dict[config_no]['f_profit'] = 0
        symbol_perfomance_dict[config_no]['f_loss'] = 0
        symbol_perfomance_dict[config_no]['f_earnings'] = 0
        symbol_perfomance_dict[config_no]['f_vol'] = 0
        for exchange in  [item for item in symbol_perfomance_dict[config_no].keys() if 'binance' in item]:
            for symbol in  symbol_perfomance_dict[config_no][exchange].keys():
                symbol_perfomance_dict[config_no]['f_profit'] += symbol_perfomance_dict[config_no][exchange][symbol]['profit']
                symbol_perfomance_dict[config_no]['f_loss'] += symbol_perfomance_dict[config_no][exchange][symbol]['loss']
                symbol_perfomance_dict[config_no]['f_earnings'] = symbol_perfomance_dict[config_no]['f_profit'] + \
                                                                  symbol_perfomance_dict[config_no]['f_loss']
                symbol_perfomance_dict[config_no]['f_vol']  += symbol_perfomance_dict[config_no][exchange][symbol]['Volume']
                    
    symbol_perfomance_dict = OrderedDict(sorted(symbol_perfomance_dict.items(),
                                                key=lambda x: x[1]['f_profit'],
                                                reverse=True
                                                )
                                        )
    for config_no in list(symbol_perfomance_dict.keys())[:10]:
        print(symbol_perfomance_dict[config_no]['f_earnings'],
              symbol_perfomance_dict[config_no]['f_profit'],
              symbol_perfomance_dict[config_no]['f_loss'],
              symbol_perfomance_dict[config_no]['f_vol'],
              symbol_perfomance_dict[config_no]['config'])

    file__name = os.path.abspath(os.getcwd())+"/Optimization/" + 'combined30000_full.pkl'

    with open(file__name, 'wb') as f:
        pickle.dump(symbol_perfomance_dict, f)
    
    print('Time elapsed:', time.time()-tic)
    return 

async def initialize_symbol_perfomance_dict(file_names, config_len):
    try:
        symbol_perfomance_dict = OrderedDict()
        exchanges = list(set([item.split('-')[0] for item in file_names]))

        for config_no in config_len:
            symbol_perfomance_dict[config_no] = {}
            for exchange in exchanges:
                symbol_perfomance_dict[config_no][exchange] = OrderedDict()
    except:
        print(traceback.format_exc())
    return symbol_perfomance_dict

async def check_symbol_performance_L0(fees, fee_rate, fee_cushion, duration, order_life, variable_dict, config_len):
    try:
        file_names = await get_performance_log_file_names()
        tasks = []
        performance_log_df_dict = OrderedDict()
        for file_name in file_names:
            symbol = file_name.split('-')[1].replace('USDT', '/USDT')
            performance_log_df_dict[symbol] = [convert_trade_log_csv_to_df(file_name),
                                               file_name]
        symbol_perfomance_dict = await initialize_symbol_perfomance_dict(file_names, config_len)
        for config_no in config_len:
            tasks = [asyncio.create_task(check_symbol_performance_L1(performance_log_df_dict[symbol],
                                                                    fees,
                                                                    fee_rate, fee_cushion,
                                                                    duration, order_life,
                                                                    symbol_perfomance_dict,
                                                                    variable_dict, config_no
                                                                     )
                                        )
                     for symbol in performance_log_df_dict.keys()
                     ]
        if tasks:
            await asyncio.gather(tasks)
    except:
        print(traceback.format_exc())
    return symbol_perfomance_dict

def check_symbol_performance(fees, fee_rate, fee_cushion, duration, order_life, variable_dict, config_len):
    tic = time.time()
    symbol_perfomance_dict = asyncio.run(check_symbol_performance_L0(fees, fee_rate, fee_cushion,
                                                                     duration, order_life, variable_dict,
                                                                     config_len))
    
    symbol_perfomance_dict = symbol_perfomance_dict[0]
    for exchange in symbol_perfomance_dict.keys():
        symbol_perfomance_dict[exchange] = OrderedDict(sorted(symbol_perfomance_dict[exchange].items(),
                                                              key=lambda x: x[1]['profit'], reverse=True
                                                              )
                                                       )
    pref_symbol_list = [symbol for exchange in symbol_perfomance_dict.keys() for symbol in symbol_perfomance_dict[exchange].keys()
                        if symbol_perfomance_dict[exchange][symbol]['profit'] or
                        symbol_perfomance_dict[exchange][symbol]['loss']]
    print('Time elapsed:', time.time()-tic)
    return symbol_perfomance_dict, pref_symbol_list


if __name__ == '__main__':
    project_path = os.path.abspath(os.getcwd())+"/"
    fee_rate = 0.002
    fee_cushion = 0.0015
    duration = [1,0] #[start, stop] start must be higher than stop
    order_life = 25*60
    fees = {}
    variable_dict = OrderedDict()
    long_gradient_list = ['long_low', 'long_low0', '0long_high', 'long_high']
    mid_gradient_list = ['mid_low0', '0mid_high']
    low_gradient_list = ['low_low0', '0low_high']
    config_len=range(0,1)
    symbol_perfomance_dict = OrderedDict()
    
    final_dict = {}
    _dict = {}
    file__names = get_optimization_log_file_names()
    i = 0
    
##    for file__name in file__names:
##        file__name = os.path.abspath(os.getcwd())+"/Optimization/" + file__name
##        if '_long_low_' in file__name:
##            with open(file__name, 'rb') as f:
##                _dict = pickle.load(f)
##                for key in _dict.keys():
##                    for val in _dict[key].keys():
##                        if not 'final profit' in val:
##                            final_dict[key] = _dict[key][val]
##                            final_dict[key]['loss'] = 0
##                            final_dict[key]['profit'] = 0
##                            loss_list = []
##                            profit_list = []
##                            for o in _dict[key][val].keys():
##                                if not 'loss' in o and not 'profit' in o:
##                                    if isinstance(_dict[key][val][o], int):
##                                        set_trace()
##                                    loss_list.append(_dict[key][val][o]['loss'])
##                                    profit_list.append(_dict[key][val][o]['profit'])
##                                
##                            final_dict[key]['loss'] = sum(loss_list)
##                            final_dict[key]['profit'] += sum(profit_list)
##                            final_dict[key]['total profit'] = final_dict[key]['profit'] + final_dict[key]['loss']
##                
##                final_dict = OrderedDict(sorted(final_dict.items(),
##                                                key=lambda x: x[1]['total profit'],
##                                                reverse=True
##                                                )[:10]
##                                         )
##                
##                for key in final_dict.keys():
##                    symbol_perfomance_dict.update({i: final_dict[key]})
##                    i += 1
##            print(file__name,'transfered!')
##    
##    symbol_perfomance_dict = OrderedDict(sorted(symbol_perfomance_dict.items(),
##                                                key=lambda x: x[1]['total profit'],
##                                                reverse=True
##                                                )
##                                        )
##    print([[symbol_perfomance_dict[i]['total profit'], symbol_perfomance_dict[i]['profit'], symbol_perfomance_dict[i]['loss'],
##            sum([symbol_perfomance_dict[i][sym]['Volume']
##                 for sym in list(symbol_perfomance_dict[i].keys()) if not 'loss' in sym and not 'profit' in sym]),
##                symbol_perfomance_dict[i][list(symbol_perfomance_dict[i].keys())[0]]['variable_dict']]
##            for i in list(symbol_perfomance_dict.keys())[:10]])
##    filename = '/home/pi/Downloads/IEA/Optimization/var_dict_long_low.pkl'
##    with open(filename, 'wb') as f:
##        pickle.dump(symbol_perfomance_dict, f)

##    variable_dict = OrderedDict([('initialize_8_10_mid_low0_low_low0', True), ('initialize_8_10_mid_low0_0low_high', True),
##                                 ('initialize_8_10_0mid_high_low_low0', True), ('initialize_8_10_0mid_high_0low_high', True),
##                                 ('initialize_05_07_mid_low0_low_low0', True), ('initialize_05_07_mid_low0_0low_high', True),
##                                 ('initialize_05_07_mid_low0_low_high', True), ('initialize_05_07_0mid_high_low_low0', True),
##                                 ('initialize_05_07_0mid_high_0low_high', True), ('initialize_3_4_mid_low_low_low', True),
##                                 ('initialize_3_4_mid_low_low_low0', True), ('initialize_3_4_mid_low0_low_low', True),
##                                 ('initialize_3_4_mid_low0_low_low0', True), ('initialize_3_4_mid_low0_0low_high', True),
##                                 ('initialize_3_4_0mid_high_low_low0', True), ('initialize_3_4_0mid_high_0low_high', True),
##                                 ('initialize_3_4_0mid_high_low_high', True),  ('initialize_3_4_mid_high_0low_high', True)])
##    l = [False, True]
##    p_list = list(itertools.product(l, repeat=16))
##    
##    for item in ['long_low']:
##        for mid_grad in mid_gradient_list:
##            for low_grad in low_gradient_list:
##                var_name = 'initialize_' + str(item)  + '_' + str(mid_grad) + '_' + str(low_grad)
##                variable_dict[var_name] = False
    
    optimize(fees, fee_rate, fee_cushion, duration, order_life)

##    symbol_perfomance_dict, pref_symbol_list = check_symbol_performance(fees, fee_rate, fee_cushion, duration,
##                                                                        order_life, variable_dict, config_len)
##    
##    for exchange in symbol_perfomance_dict.keys():
##        print(exchange)
##        for symbol in symbol_perfomance_dict[exchange].keys():
##            if symbol_perfomance_dict[exchange][symbol]['profit'] or\
##               symbol_perfomance_dict[exchange][symbol]['loss']:
##                print(symbol,':')
##                print(round(symbol_perfomance_dict[exchange][symbol]['earnings'],2), ',',
##                      round(symbol_perfomance_dict[exchange][symbol]['Tearnings'],2), ',',
##                      round(symbol_perfomance_dict[exchange][symbol]['profit'],2), ',',
##                      round(symbol_perfomance_dict[exchange][symbol]['loss'],2), ',',
##                      round(symbol_perfomance_dict[exchange][symbol]['profit ratio'],2), ',',
##                      round(symbol_perfomance_dict[exchange][symbol]['% buy sucess'],2), ',',
##                      round(symbol_perfomance_dict[exchange][symbol]['% sell sucess'],2), ',',
##                      round(symbol_perfomance_dict[exchange][symbol]['Volume'],2))
##                
##        print('Overall Volume:', sum([symbol_perfomance_dict[exchange][symbol]['Volume']
##                                        for exchange in symbol_perfomance_dict.keys()
##                                        for symbol in symbol_perfomance_dict[exchange].keys() if
##                                        symbol_perfomance_dict[exchange][symbol]['Volume'] != 0]))
##        
##        print('Overall Trade success ratio:', np.mean([symbol_perfomance_dict[exchange][symbol]['% trade sucess']
##                                        for exchange in symbol_perfomance_dict.keys()
##                                        for symbol in symbol_perfomance_dict[exchange].keys() if
##                                        symbol_perfomance_dict[exchange][symbol]['% trade sucess'] != 0]))
##        print('Overall Profit Ratio:', np.mean([symbol_perfomance_dict[exchange][symbol]['profit ratio']
##                                               for exchange in symbol_perfomance_dict.keys()
##                                               for symbol in symbol_perfomance_dict[exchange].keys() if
##                                                symbol_perfomance_dict[exchange][symbol]['profit ratio'] != 0]))
##        
##        print('Overall Profit:', sum([symbol_perfomance_dict[exchange][symbol]['profit'] +
##                                        symbol_perfomance_dict[exchange][symbol]['loss']
##                                        for exchange in symbol_perfomance_dict.keys()
##                                        for symbol in symbol_perfomance_dict[exchange].keys() if
##                                        symbol_perfomance_dict[exchange][symbol]['profit'] or
##                                        symbol_perfomance_dict[exchange][symbol]['loss']]))
##        print('Overall Conserved:', sum([symbol_perfomance_dict[exchange][symbol]['earnings']
##                                        for exchange in symbol_perfomance_dict.keys()
##                                        for symbol in symbol_perfomance_dict[exchange].keys() if
##                                        symbol_perfomance_dict[exchange][symbol]['profit'] or
##                                        symbol_perfomance_dict[exchange][symbol]['loss']]))
##    print(pref_symbol_list)
