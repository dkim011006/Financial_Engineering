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

# Calculate Volatility $\sigma$

```python
import yfinance as yf
import pandas as pd

data = yf.download('^GSPC',start = '1927-12-30',end='2020-11-09')

data.to_excel('history.xlsx')
```

위의 코드를 통하여 S&P 500 index의 자료를 history.xlsx파일로 가져온다.

<img width="637" alt="스크린샷_2021-12-06_오후_8 55 28" src="https://user-images.githubusercontent.com/65712771/151545432-9108daff-4a49-4f04-8f4d-938dc8b9e369.png">
위와 같이 1927년 12월 30일부터 2020년 11월 9일까지의 모든 자료를 가져온다.

종가를 기준으로 $\ln (S_i/S_{i-1})$를 구하고 이것의 Variance를 구하면 

- Variance = 0.000144527

따라서 Volatility per day는

- $\sigma_D = \sqrt{0.000144527}=0.012021919$

이것을 Volatility per annum으로 바꾸면 

- $\sigma_Y=\sigma_D\times\sqrt{252}=0.190842048$

# Calculate \u,d,p,q

하루 단위로 기간을 자르면 $dt = 1/252=0.003968254$ 이다.

CRR method를 쓰면 

- $u=e^{\sigma \sqrt{\Delta t}}=e^{0.190842048\times \sqrt{0.003968254}}=1.012094473$
- $d=e^{-\sigma \sqrt{\Delta t}}=e^{-0.190842048\times \sqrt{0.003968254}}=0.988050056$
- $p =1-q=\frac{e^{r\Delta t}-d}{u-d}=0.497192603$
- $q=0.502807397$

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

$2.0099772243439+2.0099772243439 \times\frac{1}{e^{0.0011 \times 0.25}}+2.0099772243439 \times\frac{1}{e^{0.0011 \times 0.5}}+2.0099772243439 \times\frac{1}{e^{0.00115 \times 0.75}}+2.0099772243439 \times\frac{1}{e^{0.0012 \times 1}}+2.0099772243439 \times\frac{1}{e^{0.001325 \times 1.25}}+2.0099772243439 \times\frac{1}{e^{0.00145 \times 1.5}}+2.0099772243439 \times\frac{1}{e^{0.001575 \times 1.75}}+100 \times\frac{1}{e^{0.0017 \times 2}}=115.7213683$

# $\Delta$-hedged position

principal인 $100은 risk-free rate에 따라 현재의 가치가 변하지만 coupon은 S&P index에 따라 값이 변한다. 따라서 coupon에 대한 hedge를 해야한다. S&P index 와 increasing rate가 같은 파생상품을 통하여 hedge를 할 수 있다.

$\Delta$-hedged position을 구하기 위하여 아래의 연립방정식을 이용한다. V와 S모두 coupon에 대한 함수이다.

- $V_1(H)=X_1(H)=e^{r\Delta t}(X_0-\Delta_0S_0)+\Delta_0S_1(H)$
- $V_1(T)=X_1(T)=e^{r\Delta t}(X_0-\Delta_0S_0)+\Delta_0S_1(T)$
- $S_1(H)=S_0\times u$
- $S_1(T)=S_0\times d$

2020년 11월 9일 기준으로 

- $V_1(H)=16.3077767487$
- $V_1(T)=15.8165822864$

$S_0\Delta_0=\frac{V_1(H)-V_1(T)}{u-d}=\frac{16.3077767487-15.8165822864}{1.012094473-0.988050056}=20.4286285$

따라서 increasing rate가 S&P500 index와 동일한 파생상품을 20.4286285만큼 구매하여 hedge를 할 수 있다.
