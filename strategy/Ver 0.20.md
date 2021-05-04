# 매수 매도 전략 Ver 0.20
![dsBuffer bmp](https://user-images.githubusercontent.com/55151796/113850320-4c5e2a80-97d5-11eb-98f4-9f499b2920d0.png)
## 개선 사항  
1. 가격 데이터 전체를 판다스로 옮김 ( 5이평 10이평 현재가 등 모두 )
2. 30이평 데이터 추가

## 매수 전략
1분전 현재가 < 30이평 and 지금 현재가 > 30이평
30이평을 뚫는 순간 매수

## 매도 전략
10이평 < 20이평 조건이 충족하면 매도

### 문제점
매수가와 매도가가 비슷해서 세금만 내고 있다.  
매수와 매도 차이를 두어야 할 것 같다.

## 운영 기간
2021-04-06 ~ 
## 이전 버전
[Ver 0.00](https://github.com/E-know/AutoKStock/blob/main/strategy/Ver%200.00.md)  
[Ver 0.01](https://github.com/E-know/AutoKStock/blob/main/strategy/Ver%200.01.md)  
[Ver 0.10](https://github.com/E-know/AutoKStock/blob/main/strategy/Ver%200.10.md)  
