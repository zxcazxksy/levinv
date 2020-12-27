import os
import sys
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
from config.kiwoomType import *

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self.realType = RealType()

        #print("kiwoom() class start. ")
        print("Kiwoom() class start.")

        ####### event loop를 실행하기 위한 변수모음
        self.login_event_loop = QEventLoop() #로그인 요청용 이벤트루프
        self.detail_account_info_event_loop = QEventLoop() # 예수금 요청용 이벤트루프
        self.calculator_event_loop = QEventLoop()
        #########################################

        ########### 전체 종목 관리
        self.all_stock_dict = {}
        ###########################


        ####### 계좌 관련된 변수
        self.account_stock_dict = {}
        self.not_account_stock_dict = {}
        self.deposit = 0 #예수금
        self.use_money = 0 #실제 투자에 사용할 금액
        self.use_money_percent = 0.5 #예수금에서 실제 사용할 비율
        self.output_deposit = 0 #출력가능 금액
        self.total_profit_loss_money = 0 #총평가손익금액
        self.total_profit_loss_rate = 0.0 #총수익률(%)
        ########################################

        ######## 종목 정보 가져오기
        self.portfolio_stock_dict = {}
        self.jango_dict = {}
        ########################

        ########### 종목 분석 용
        self.calcul_data = []
        ##########################################


        ####### 요청 스크린 번호
        self.screen_my_info = "2000" #계좌 관련한 스크린 번호
        self.screen_calculation_stock = "4000" #계산용 스크린 번호
        self.screen_real_stock = "5000" #종목별 할당할 스크린 번호
        self.screen_meme_stock = "6000" #종목별 할당할 주문용스크린 번호
        self.screen_start_stop_real = "1000" #장 시작/종료 실시간 스크린번호
        ########################################

        ######### 초기 셋팅 함수들 바로 실행
        self.get_ocx_instance() #OCX 방식을 파이썬에 사용할 수 있게 변환해 주는 함수
        self.event_slots() # 키움과 연결하기 위한 시그널 / 슬롯 모음
        self.real_event_slot()  # 실시간 이벤트 시그널 / 슬롯 연결
        self.signal_login_commConnect() #로그인 요청 시그널 포함
        self.get_account_info() #계좌번호 가져오기

        self.detail_account_info() #예수금 요청 시그널 포함
        self.detail_account_mystock() #계좌평가잔고내역 요청 시그널 포함
        QTimer.singleShot(5000, self.not_concluded_account) #5초 뒤에 미체결 종목들 가져오기 실행
        #########################################

        QTest.qWait(10000)
        self.read_code()
        self.screen_number_setting()


        QTest.qWait(5000)


    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        if sRQName == "주식분봉차트조회":

            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            # data = self.dynamicCall("GetCommDataEx(QString, QString)", sTrCode, sRQName)
            # [[‘’, ‘현재가’, ‘거래량’, ‘거래대금’, ‘날짜’, ‘시가’, ‘고가’, ‘저가’. ‘’], [‘’, ‘현재가’, ’거래량’, ‘거래대금’, ‘날짜’, ‘시가’, ‘고가’, ‘저가’, ‘’]. […]]

            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            print("남은 일자 수 %s" % cnt)


            for i in range(cnt):
                data = []

                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")  # 출력 : 000070
                value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")  # 출력 : 000070
                trading_value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래대금")  # 출력 : 000070
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")  # 출력 : 000070
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")  # 출력 : 000070
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")  # 출력 : 000070
                low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")  # 출력 : 000070

                data.append("")
                data.append(current_price.strip())
                data.append(value.strip())
                data.append(trading_value.strip())
                data.append(date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())
                data.append("")

                self.calcul_data.append(data.copy())


            if sPrevNext == "2":
                self.day_kiwoom_db(code=code, sPrevNext=sPrevNext)

            else:
                print("총 일수 %s" % len(self.calcul_data))

                pass_success = False

                # 120일 이평선을 그릴만큼의 데이터가 있는지 체크
                if self.calcul_data == None or len(self.calcul_data) < 120:
                    pass_success = False

                else:

                    # 120일 이평선의 최근 가격 구함
                    total_price = 0
                    for value in self.calcul_data[:120]:
                        total_price += int(value[1])
                    moving_average_price = total_price / 120

                    total_price_120 = 0
                    for value in self.calcul_data[:120]:
                        total_price_120 += int(value[1])
                    ma_120 = total_price_120 / 120

                    total_price_60 = 0
                    for value in self.calcul_data[:60]:
                        total_price_60 += int(value[1])
                    ma_60 = total_price_60 / 60

                    total_price_5 = 0
                    for value in self.calcul_data[:5]:
                        total_price_5 += int(value[1])
                    ma_5 = total_price_5 / 5

                    #RSI 계산 RSI = 100 – 100 (1 + RS)   RS = (N일간의 상승폭 평균 / N일간의 하락폭 평균)
                    rsi_rs_n = 9 # rsi 기간
                    rsi_list = []

                    for value in reversed(self.calcul_data):
                        print(value)
                        if len(rsi_list) <  rsi_rs_n:
                            rsi_list.append(value)

                    print(rsi_list)

                    i = 0
                    rsi_upstream = []
                    rsi_downstream = []
                    while i + 1 < len(rsi_list):
                        a = int(rsi_list[i])
                        b = int(rsi_list[i + 1])
                        i += 1
                        result = a - b
                        if result > 0:
                            rsi_upstream.append(result)
                        elif result < 0:
                            rsi_downstream.append(result)


                    sum_up = 0
                    for ai in rsi_upstream:
                        sum_up = sum_up + ai
                        average_up = sum_up / len(rsi_upstream)

                    sum_down = 0
                    for ai in rsi_downstream:
                        sum_down = sum_down + ai
                        average_down = sum_down / len(rsi_downstream)

                    rs = abs(average_up / average_down)
                    rsi_result = rs / (1 + rs)




                    leverage = False
                    inverse = False
                    hold = False
                    lev_up_market = False
                    lev_gap = False
                    lev_decre_market = False
                    inv_down_market = False
                    inv_incre_market = False
                    inv_gap = False

                    #현재 주가가 5가 60보다 높음
                    #int(self.calcul_data[0][1])
                    if  ma_5 >= ma_60:
                        print("leverage구간")
                        leverage = True
                    elif ma_5 < ma_60:
                        print("inverse구간")
                        inverse = True

                    if leverage == True:
                        while True:
                            if int(self.calcul_data[0][1]) >= ma_5: #5일봉 위일때
                                print("상승장")
                                lev_up_market = True

                            elif int(self.calcul_data[0][1]) <= ma_5 and int(self.calcul_data[0][1]) >= ma_60: # 5일봉 아래 60일봉 사이
                                print("레버리지갭")
                                lev_gap = True

                            else:
                                print ("급락")
                                lev_decre_market = True

                    if inverse == True:
                        while True:
                            if int(self.calcul_data[0][1]) <= ma_5: #5일봉 아래
                                print("하락장")
                                inv_down_market = True

                            elif int(self.calcul_data[0][1]) >= ma_5 and int(self.calcul_data[0][1]) >= ma_60: # 5일봉 아래 60일봉 사이
                                print("인버스갭")
                                inv_gap = True

                            else:
                                print ("급등")
                                inv_incre_market = True

                    '''
                    lev_up_market = False
                    lev_gap = False
                    lev_decre_market = False
                    inv_down_market = False
                    inv_incre_market = False
                    inv_gap = False
                    '''
                    if lev_decre_market == True and rsi_result > 0.7:
                        print("팔아야할 타이밍")
                    if lev_up_market == True and rsi_result < 0.4:
                        print("사야되는 타이밍")
                    if inv_down_market == True and rsi_result > 0.7:
                        print("고평가, 팔아야할 타이밍")
                    if inv_incre_market == True and rsi_result < 0.4:
                        print("구매타이밍")

















                   # 오늘자 주가가 120일 이평선에 걸쳐있는지 확인, [‘’, ‘현재가’, ‘거래량’, ‘거래대금’, ‘날짜’, ‘시가’, ‘고가’, ‘저가’. ‘’]
                    bottom_stock_price = False
                    check_price = None
                    if int(self.calcul_data[0][7]) <= moving_average_price and moving_average_price >= int(self.calcul_data[0][6]):
                        print("오늘 주가 120이평선 아래에 걸쳐있는 것 확인")
                        bottom_stock_price = True
                        check_price = int(self.calcul_data[0][6])


                    # 과거 일봉 데이터를 조회하면서 120일 이평선보다 주가가 계속 밑에 존재하는지 확인
                    prev_price = None
                    if bottom_stock_price == True:

                        moving_average_price_prev = 0
                        price_top_moving = False
                        idx = 1
                        while True:

                            if len(self.calcul_data[idx:]) < 120:  # 120일치가 있는지 계속 확인
                                print("120일치가 없음")
                                break

                            total_price = 0
                            for value in self.calcul_data[idx:120+idx]:
                                total_price += int(value[1])
                            moving_average_price_prev = total_price / 120

                            if moving_average_price_prev <= int(self.calcul_data[idx][6]) and idx <= 20:
                                print("20일 동안 주가가 120일 이평선과 같거나 위에 있으면 조건 통과 못함")
                                price_top_moving = False
                                break

                            elif int(self.calcul_data[idx][7]) > moving_average_price_prev and idx > 20:  # 120일 이평선 위에 있는 구간 존재
                                print("120일치 이평선 위에 있는 구간 확인됨")
                                price_top_moving = True
                                prev_price = int(self.calcul_data[idx][7])
                                break

                            idx += 1

                        # 해당부분 이평선이 가장 최근의 이평선 가격보다 낮은지 확인
                        if price_top_moving == True:
                            if moving_average_price > moving_average_price_prev and check_price > prev_price:
                                print("포착된 이평선의 가격이 오늘자 이평선 가격보다 낮은 것 확인")
                                print("포착된 부분의 저가가 오늘자 주가의 고가보다 낮은지 확인")
                                pass_success = True

                if pass_success == True:
                    print("조건부 통과됨")

                    code_nm = self.dynamicCall("GetMasterCodeName(QString)", code)

                    f = open("files/condition_stock.txt", "a", encoding="utf8")
                    f.write("%s\t%s\t%s\n" % (code, code_nm, str(self.calcul_data[0][1])))
                    f.close()


                elif pass_success == False:
                    print("조건부 통과 못함")

                self.calcul_data.clear()
                self.calculator_event_loop.exit()

    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):
        QTest.qWait(3600)  # 3.6초마다 딜레이를 준다.

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", "233740")
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")

        if date != None:
            self.dynamicCall("SetInputValue(QString, QString)", "틱범위", "5")

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식분봉차트조회", "opt10080", sPrevNext,
                         self.screen_calculation_stock)  # Tr서버로 전송 -Transaction

        self.calculator_event_loop.exec_()

