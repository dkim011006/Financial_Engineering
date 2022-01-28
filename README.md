# 2021_Introduction to Financial Engineering Term Project
Professor Jang Bong Gyu (장봉규)

# Condition

principal = $100

maturity = 2 year

2020년 11월 9일을 오늘로 하고 fair price를 찾는다.

# US Treasury rate

[https://www.treasury.gov/resource-center/data-chart-center/interest-rates/pages/TextView.aspx?data=yieldYear&year=2020](https://www.treasury.gov/resource-center/data-chart-center/interest-rates/pages/TextView.aspx?data=yieldYear&year=2020) 

위의 링크에서 Treasury Yield Curve를 구한다.

| Month | 3 | 6 | 12 | 24 |
| --- | --- | --- | --- | --- |
| rate(%) | 0.11 | 0.11 | 0.12 | 0.17 |

3, 6, 12, 24개월만 나와 있으므로 9, 15, 18, 21개월을 추정하여야 한다.

| Month | 3 | 6 | 9 | 12 | 15 | 18 | 21 | 24 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rate(%) | 0.11 | 0.11 | 0.115 | 0.12 | 0.1325 | 0.145 | 0.1575 | 0.17 |

평균값을 이용하여 9, 15, 18, 21개월을 추정한다.

# Calculate Volatility ![math](https://latex.codecogs.com/gif.latex?%5Csigma)

```python
import yfinance as yf
import pandas as pd

data = yf.download('^GSPC',start = '1927-12-30',end='2020-11-09')

data.to_excel('history.xlsx')
```

위의 코드를 통하여 S&P 500 index의 자료를 history.xlsx파일로 가져온다.

<img width="637" alt="스크린샷_2021-12-06_오후_8 55 28" src="https://user-images.githubusercontent.com/65712771/151545432-9108daff-4a49-4f04-8f4d-938dc8b9e369.png">
위와 같이 1927년 12월 30일부터 2020년 11월 9일까지의 모든 자료를 가져온다.

종가를 기준으로 ![math](https://latex.codecogs.com/gif.latex?%5Cln%20%28S_i/S_%7Bi-1%7D%29)를 구하고 이것의 Variance를 구하면 

- Variance = 0.000144527

따라서 Volatility per day는

- ![math](https://latex.codecogs.com/gif.latex?%5Csigma_D%20%3D%20%5Csqrt%7B0.000144527%7D%3D0.012021919)

이것을 Volatility per annum으로 바꾸면 

- ![math](https://latex.codecogs.com/gif.latex?%5Csigma_Y%3D%5Csigma_D%5Ctimes%5Csqrt%7B252%7D%3D0.190842048)

# Calculate ![math](https://latex.codecogs.com/gif.latex?u%2Cd%2Cp%2Cq)

하루 단위로 기간을 자르면 ![math](https://latex.codecogs.com/gif.latex?dt%20%3D%201/252%3D0.003968254) 이다.

CRR method를 쓰면 

- ![math](https://latex.codecogs.com/gif.latex?u%3De%5E%7B%5Csigma%20%5Csqrt%7B%5CDelta%20t%7D%7D%3De%5E%7B0.190842048%5Ctimes%20%5Csqrt%7B0.003968254%7D%7D%3D1.012094473)
- ![math](https://latex.codecogs.com/gif.latex?d%3De%5E%7B-%5Csigma%20%5Csqrt%7B%5CDelta%20t%7D%7D%3De%5E%7B-0.190842048%5Ctimes%20%5Csqrt%7B0.003968254%7D%7D%3D0.988050056)
- ![math](https://latex.codecogs.com/gif.latex?p%20%3D1-q%3D%5Cfrac%7Be%5E%7Br%5CDelta%20t%7D-d%7D%7Bu-d%7D%3D0.497192603)
- ![math](https://latex.codecogs.com/gif.latex?q%3D0.502807397)

# Apply Binomial Model

```python
import numpy as np
import pandas as pd
"""
n은 몇일이 지났는지 의미한다. 
1년을 252일 1달을 21일로 보고 실행한다.
하루씩 쪼갰기 때문에 t = 1/252 = 0.003968254 이다.
"""
def binomialTree(n,u,d,p,q,r,t,IRfile,CRfile):
    increasingRate = np.zeros((n+1,n+1)) # increasingRate를 크기가 (n+1)X(n+1)가 되게 만듬

    increasingRate[0,0] = 1 # increasingRate의 시작값을 1로 한다.
    for i in range(1, n+1):
        for j in range(0, i+1):
            increasingRate[i, j] = (u**(i-j))*(d**j) # increasingRate를 binomial tree에 맞추어 계산

    couponRate = np.zeros((n+1,n+1)) # couponRate를 크기가 (n+1)X(n+1)가 되게 만듬
    for i in range(0, n+1):
        if(increasingRate[n, i] > 1.07): #increaingRate가 7%보다 클때
            couponRate[n, i] = 0.05
        elif(increasingRate[n, i] <= 1): #increaingRate가 1일때 -> S&P가 오르지 않았을때
            couponRate[n, i] = 0
        else:  #increaingRate가 0%부터 7%사이일때
            couponRate[n, i] = increasingRate[n, i]-1

    for i in range(0,n): # coupon rate를 만기일부터 오늘까지 차례로 계산해옴
        for j in range(0,n-i):
            couponRate[n-i-1,j] = np.exp(-r*t)*(p*couponRate[n-i,j]+q*couponRate[n-i,j+1])

    IR = pd.DataFrame(increasingRate)
    CR = pd.DataFrame(couponRate)
    IR.to_excel(IRfile) # excel에 icreasing rate를 입력
    CR.to_excel(CRfile) # excel에 coupon rate를 입력

binomialTree(63,1.012094473,0.988050056,0.497192603,0.502807397,0.0012,0.003968254,'IR.xlsx','CR.xlsx')
```

이전 쿠폰 지급 시점부터 현재까지의 increasing rate를 구하면 된다. 따라서 3개월(63일) 간의 increasing rate만 계산을 하면 된다.

S&P500 index의 imcreasing rate를 구하기 위하며 (n+1)X(n+1) 크기의 배열을 선언한다.

1행 1열의 값을 1로 놓고 u와 d의 값을 차례로 곱해주어 S&P index의 increasing rate를 구한다. 

couponRate라는 (n+1)X(n+1) 크기의 배열을 선언한다. increasingRate배열의 (n+1) 행의 값이 1.07 이상이면 0.05를 1 이하이면 0을 나머지는 값에서 1을 뺸 값을 couponRate (n+1) 행의 같은 자리에 넣어준다.

이후에 n행의 coupon rate를 구하기 위하여 (n+1)행의 coupon rate를 이용한다. 이것을 couponRate 1행의 값을 구할때까지 반복한다.

따라서 couponRate의 1행 1열의 값이 coupon rate의 기대값이 되고 이를 principal인 100과 곱해주면 coupon의 기대값이 된다.

1행 1열의 값

- 0.020099772243439

따라서 3개월 뒤에 받는 coupon의 현재 가치는

- $2.0099772243439

이다. 

Principal과 coupon의 현재가치를 모두 더하면 fair price가 된다. 

![math](https://latex.codecogs.com/gif.latex?2.0099772243439&plus;2.0099772243439%20%5Ctimes%5Cfrac%7B1%7D%7Be%5E%7B0.0011%20%5Ctimes%200.25%7D%7D&plus;2.0099772243439%20%5Ctimes%5Cfrac%7B1%7D%7Be%5E%7B0.0011%20%5Ctimes%200.5%7D%7D&plus;2.0099772243439%20%5Ctimes%5Cfrac%7B1%7D%7Be%5E%7B0.00115%20%5Ctimes%200.75%7D%7D&plus;2.0099772243439%20%5Ctimes%5Cfrac%7B1%7D%7Be%5E%7B0.0012%20%5Ctimes%201%7D%7D&plus;2.0099772243439%20%5Ctimes%5Cfrac%7B1%7D%7Be%5E%7B0.001325%20%5Ctimes%201.25%7D%7D&plus;2.0099772243439%20%5Ctimes%5Cfrac%7B1%7D%7Be%5E%7B0.00145%20%5Ctimes%201.5%7D%7D&plus;2.0099772243439%20%5Ctimes%5Cfrac%7B1%7D%7Be%5E%7B0.001575%20%5Ctimes%201.75%7D%7D&plus;100%20%5Ctimes%5Cfrac%7B1%7D%7Be%5E%7B0.0017%20%5Ctimes%202%7D%7D%3D115.7213683)

# ![math](https://latex.codecogs.com/gif.latex?%5CDelta)-hedged position

principal인 $100은 risk-free rate에 따라 현재의 가치가 변하지만 coupon은 S&P index에 따라 값이 변한다. 따라서 coupon에 대한 hedge를 해야한다. S&P index 와 increasing rate가 같은 파생상품을 통하여 hedge를 할 수 있다.

![math](https://latex.codecogs.com/gif.latex?%5CDelta)-hedged position을 구하기 위하여 아래의 연립방정식을 이용한다. V와 S모두 coupon에 대한 함수이다.

- ![math](https://latex.codecogs.com/gif.latex?V_1%28H%29%3DX_1%28H%29%3De%5E%7Br%5CDelta%20t%7D%28X_0-%5CDelta_0S_0%29&plus;%5CDelta_0S_1%28H%29)
- ![math](https://latex.codecogs.com/gif.latex?V_1%28T%29%3DX_1%28T%29%3De%5E%7Br%5CDelta%20t%7D%28X_0-%5CDelta_0S_0%29&plus;%5CDelta_0S_1%28T%29)
- ![math](https://latex.codecogs.com/gif.latex?S_1%28H%29%3DS_0%5Ctimes%20u)
- ![math](https://latex.codecogs.com/gif.latex?S_1%28T%29%3DS_0%5Ctimes%20d)

2020년 11월 9일 기준으로 

- ![math](https://latex.codecogs.com/gif.latex?V_1%28H%29%3D16.3077767487)
- ![math](https://latex.codecogs.com/gif.latex?V_1%28T%29%3D15.8165822864)

![math](https://latex.codecogs.com/gif.latex?S_0%5CDelta_0%3D%5Cfrac%7BV_1%28H%29-V_1%28T%29%7D%7Bu-d%7D%3D%5Cfrac%7B16.3077767487-15.8165822864%7D%7B1.012094473-0.988050056%7D%3D20.4286285)

따라서 increasing rate가 S&P500 index와 동일한 파생상품을 20.4286285만큼 구매하여 hedge를 할 수 있다.
