# AutoKStock
키움증권의 Open API를 이용한 자동 기술적 매매 프로그램

**Auto** + **K**orean + **Stock** = AutoKStock

# Main Language
Python 3.8

## API & Library
키움증권 Open API
Telegram Bot API
Pandas


## 매수/매도 전략 Strategy 
### 매수/매도 전략
![현대사료(016790)_분_20210503160016](https://user-images.githubusercontent.com/55151796/116849514-dd37f280-ac29-11eb-881a-d946a5deaad1.jpg)
매수 기준 : 5분 이동평균선이 20분 이동평균선을 뚫고 위로 올라갈 때 1매수호가로 지정값 매수 및 3분간 매도 금지
매도 기준 : 1분전에 5분 이동평균선이 20분이동평균선 밑으로 내려 갔을 때 매도 or 현재가가 20분 이동평균선으로 밑으로 내려갈 때 매도
(이동평균선 기준 : 실시간 값 + 과거 N분의 값 평균)

조건 : 매수/매도가 체결된 시간에는 동일 종목에 한하여 매수/매도 금지

### 매수/매도 전략 변경 이력
[Ver 0.00](https://github.com/E-know/AutoKStock/blob/main/strategy/Ver%200.00.md)  
[Ver 0.01](https://github.com/E-know/AutoKStock/blob/main/strategy/Ver%200.01.md)  
[Ver 0.10](https://github.com/E-know/AutoKStock/blob/main/strategy/Ver%200.10.md)  
[Ver 0.20](https://github.com/E-know/AutoKStock/blob/main/strategy/Ver%200.20.md)  
[Ver 0.30](https://github.com/E-know/AutoKStock/blob/main/strategy/Ver%200.30.md)  
[Ver 0.31](https://github.com/E-know/AutoKStock/blob/main/strategy/Ver%200.31.md)  

## 개발일지
[2021-03-24](https://slowsure.tistory.com/116)  
[2021-03-29](https://slowsure.tistory.com/117)  
[2021-03-30](https://slowsure.tistory.com/119)  
[2021-04-07](https://slowsure.tistory.com/120)  
