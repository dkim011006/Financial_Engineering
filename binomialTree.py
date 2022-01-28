"""
한달을 주말을 제외해 21일로 일년을 252일로 계산한다.
increaingRate는 S&P500 index의 increasing rate를 의미한다.
increaingRate와 couponRate의 numpy배열 크기는 같다.
increasingRate에 시작 가치를 1로 잡은 다음 얼마나 오르고 내렸는지 값을 넣어준다.
couponRate의 마지막 줄에 increasingRate의 마지막 줄의  값이 1보다 작으면 0을 넣어주고 1과 1.07사이이면 값에서 1을 뺸 값을 넣어주고 1.07보다 크면 0.05를 넣어준다.
couponRate의 마지막줄부터 첫번째 줄까지 차례대로 가치를 계산한다.
"""

import numpy as np
import pandas as pd

def binomialTree(n,u,d,p,q,r,t,IRfile,CRfile):
    increasingRate = np.zeros((n+1,n+1)) # increasingRate를 크기가 (n+1)X(n+1)가 되게 만듬

    increasingRate[0,0] = 1 # increasingRate의 시작값을 1로 한다.
    for i in range(1, n+1):
        for j in range(0, i+1):
            increasingRate[i, j] = (u**(i-j))*(d**j) # increasingRate를 binomial tree에 맞추어 계산

    couponRate = np.zeros((505,505)) # couponRate를 크기가 (n+1)X(n+1)가 되게 만듬
    for i in range(0, n+1):
        if(increasingRate[n, i] > 1.07): #increaingRate가 7%보다 클때
            couponRate[n, i] = 0.05
        elif(increasingRate[n, i] <= 1): #increaingRate가 1일때 -> S&P가 오르지 않았을때
            couponRate[n, i] = 0
        else:  #increaingRate가 0%부터 7%사이일때
            couponRate[n, i] = increasingRate[n, i]-1
    

    for i in range(0,n):
        for j in range(0,n-i):
            couponRate[n-i-1,j] = np.exp(-r*t)*(p*couponRate[n-i,j]+q*couponRate[n-i,j+1])
    
    IR = pd.DataFrame(increasingRate)
    CR = pd.DataFrame(couponRate)
    IR.to_excel(IRfile)
    CR.to_excel(CRfile)
    return couponRate
CR_3M = binomialTree(63,1.012094473,0.988050056,0.497192603,0.502807397,0.0012,0.003968254,'IR_3M.xlsx','CR_3M.xlsx')
CR_6M = binomialTree(126,1.012094473,0.988050056,0.497192603,0.502807397,0.0012,0.003968254,'IR_6M.xlsx','CR_6M.xlsx')
CR_9M = binomialTree(189,1.012094473,0.988050056,0.497192603,0.502807397,0.0012,0.003968254,'IR_9M.xlsx','CR_9M.xlsx')
CR_12M = binomialTree(252,1.012094473,0.988050056,0.497192603,0.502807397,0.0012,0.003968254,'IR_12M.xlsx','CR_12M.xlsx')
CR_15M = binomialTree(315,1.012094473,0.988050056,0.497192603,0.502807397,0.0012,0.003968254,'IR_15M.xlsx','CR_15M.xlsx')
CR_18M = binomialTree(378,1.012094473,0.988050056,0.497192603,0.502807397,0.0012,0.003968254,'IR_18M.xlsx','CR_18M.xlsx')
CR_21M = binomialTree(441,1.012094473,0.988050056,0.497192603,0.502807397,0.0012,0.003968254,'IR_21M.xlsx','CR_21M.xlsx')
CR_24M = binomialTree(504,1.012094473,0.988050056,0.497192603,0.502807397,0.0012,0.003968254,'IR_24M.xlsx','CR_24M.xlsx')
CR_SUM = CR_3M + CR_6M + CR_9M + CR_12M + CR_15M + CR_18M + CR_21M + CR_24M
CR_SUM_EXCEL = pd.DataFrame(CR_SUM)
CR_SUM_EXCEL.to_excel("CR_SUM.xlsx")   
print("done")