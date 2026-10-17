# 다나와 크롤러

현재 다나와의 `productListArea`, `ProductListTitle`, `ProductListPriceCompare` 구조를 사용합니다.
신상품순으로 페이지당 90개, 최대 22페이지를 수집하며, 다른 구성 옵션도 펼쳐서 저장합니다.
한 카테고리라도 실패하면 Actions가 실패하고 기존 `crawl_data`는 갱신하지 않습니다.
실패 시 Actions의 `crawler-diagnostics` 아티팩트에서 HTML, 화면, 오류 로그를 확인할 수 있습니다.

로컬 검증: `python -m unittest test_data_safety test_danawa_parser`

CSV를 변경하지 않는 실제 사이트 검증: `python smoke_crawler.py --category CPU --pages 2`

크롤링은 GitHub의 Actions를 사용하여 매일 KST 0시, 9시, 12시, 15시, 18시, 21시에 실행되도록 설정하였습니다

Actions의 큐 대기시간이 존재해 보통 5~20분정도 기다려야 완료됩니다

[sammy310/Danawa-Crawler](https://github.com/sammy310/Danawa-Crawler)을 기반으로 만들었습니다

## [크롤링 데이터](https://github.com/SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler/tree/master/crawl_data) / [(구글 스프레드시트)](https://docs.google.com/spreadsheets/d/173z04QolUloLeTZMjXjdQvW6NQFzGrxdr4PXjKt8_EI/edit?usp=sharing)
- [CPU](https://github.com/SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler/blob/master/crawl_data/CPU.csv) / [(Raw Data)](https://raw.githubusercontent.com/SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler/master/crawl_data/CPU.csv)
- [메인보드](https://github.com/SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler/blob/master/crawl_data/Mainboard.csv) / [(Raw Data)](https://raw.githubusercontent.com/SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler/master/crawl_data/Mainboard.csv)
- [RAM](https://github.com/SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler/blob/master/crawl_data/RAM.csv) / [(Raw Data)](https://raw.githubusercontent.com/SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler/master/crawl_data/RAM.csv)
- [공랭 쿨러](https://github.com/SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler/blob/master/crawl_data/Air%20Cooler.csv) / [(Raw Data)](https://raw.githubusercontent.com/SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler/master/crawl_data/Air%20Cooler.csv)
- [수랭 쿨러](https://github.com/SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler/blob/master/crawl_data/AIO%20Cooler.csv) / [(Raw Data)](https://raw.githubusercontent.com/SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler/master/crawl_data/AIO%20Cooler.csv)
- [그래픽카드](https://github.com/SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler/blob/master/crawl_data/VGA.csv) / [(Raw Data)](https://raw.githubusercontent.com/SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler/master/crawl_data/VGA.csv)
- [SSD](https://github.com/SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler/blob/master/crawl_data/SSD.csv) / [(Raw Data)](https://raw.githubusercontent.com/SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler/master/crawl_data/SSD.csv)
- [하드디스크](https://github.com/SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler/blob/master/crawl_data/HDD.csv) / [(Raw Data)](https://raw.githubusercontent.com/SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler/master/crawl_data/HDD.csv)
- [케이스](https://github.com/SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler/blob/master/crawl_data/Case.csv) / [(Raw Data)](https://raw.githubusercontent.com/SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler/master/crawl_data/Case.csv)
- [파워서플라이](https://github.com/SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler/blob/master/crawl_data/PSU.csv) / [(Raw Data)](https://raw.githubusercontent.com/SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSun/Danawa-Crawler/master/crawl_data/PSU.csv)
---

### 제작에 사용된 것들

- Python : 3.12
- selenium : 4.22.0
- PyGithub : 1.51
- pytz : 2020.1
- urllib3 : 2.0.1
- Chromedriver : [126.0.6478.126 (r1300313) (Win64)](https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.126/win64/chromedriver-win64.zip)
