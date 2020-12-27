calcul_data = [1,4,6,3,2,8,5,1,8,3,5,9,2,4,1,3,1,8,6,5,7,5,3,5,6,4,3,2,4,5,6,7,8,6,5,6,4,3,4,5,6,4,6,7,8,6,5,4,3,3,4,5,2,3,4,5,2,6,7,5,5,7,4,5,4,5,6]
total_price = 0
for value in calcul_data[:120]:
    total_price += int(value[1])
moving_average_price = total_price / 120

total_price_120 = 0
for value in calcul_data[:120]:
    total_price_120 += int(value[1])
ma_120 = total_price_120 / 120

total_price_60 = 0
for value in calcul_data[:60]:
    total_price_60 += int(value[1])
ma_60 = total_price_60 / 60

total_price_5 = 0
for value in calcul_data[:5]:
    total_price_5 += int(value[1])
ma_5 = total_price_5 / 5



rsi_rs_n = 9
count = len(calcul_data) - 1


rsi_list = []

for value in reversed(calcul_data):
    print(value)
    if len(rsi_list) <= 8 :
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

print(rsi_upstream)
print(rsi_downstream)

sum_up = 0
for ai in rsi_upstream:
    sum_up = sum_up + ai
    average_up = sum_up / len(rsi_upstream)
print(average_up)
sum_down = 0
for ai in rsi_downstream:
    sum_down = sum_down + ai
    average_down = sum_down / len(rsi_downstream)
print(average_down)

rs = abs(average_up / average_down)
print(rs)
rsi_result = rs / (1 + rs)

print(rsi_result)

leverage = False
inverse = False
hold = False
lev_up_market = False
lev_gap = False
lev_decre_market = False
inv_down_market = False
inv_incre_market = False
inv_gap = False

# 현재 주가가 5가 60보다 높음
# int(self.calcul_data[0][1])
if ma_5 >= ma_60:
    print("leverage구간")
    leverage = True
elif ma_5 < ma_60:
    print("inverse구간")
    inverse = True

if leverage == True:
    while True:
        if int(calcul_data[0][1]) >= ma_5:  # 5일봉 위일때
            print("상승장")
            lev_up_market = True

        elif int(calcul_data[0][1]) <= ma_5 and int(calcul_data[0][1]) >= ma_60:  # 5일봉 아래 60일봉 사이
            print("레버리지갭")
            lev_gap = True

        else:
            print("급락")
            lev_decre_market = True

if inverse == True:
    while True:
        if int(calcul_data[0][1]) <= ma_5:  # 5일봉 아래
            print("하락장")
            inv_down_market = True

        elif int(calcul_data[0][1]) >= ma_5 and int(calcul_data[0][1]) >= ma_60:  # 5일봉 아래 60일봉 사이
            print("인버스갭")
            inv_gap = True

        else:
            print("급등")
            inv_incre_market = True

if lev_up_market == True and rsi_result > 0.7:
    print("팔아야할 타이밍")
