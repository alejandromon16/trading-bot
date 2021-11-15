from iqoptionapi.stable_api import IQ_Option
from datetime import datetime
import time
import sys


def stop(gain, profit, loss):
	if gain <= float('-' + str(abs(loss))):
		print('Stop Loss already reach!')
		sys.exit()
		
	if gain >= float(abs(profit)):
		print('Stop profit already reach!')
		sys.exit()

def Martingale(valor, payout):
	gain_esperado = valor * payout
	perca = float(valor)	
		
	while True:
		if round(valor * payout, 2) > round(abs(perca) + gain_esperado, 2):
			return round(valor, 2)
			break
		valor += 0.01

def Payout(par):
	API.subscribe_strike_list(par, 1)
	while True:
		d = API.get_digital_current_profit(par, 1)
		if d != False:
			d = round(int(d) / 100, 2)
			break
		time.sleep(1)
	API.unsubscribe_strike_list(par, 1)
	
	return d

API = IQ_Option('login', 'password')
API.connect()

API.change_balance('PRACTICE') # PRACTICE / REAL

if API.check_connect():
	print(' Succes Connection!')
else:
	print(' Error to connect')
	input('\n\n Press enter to exit')
	sys.exit()


while True:
	try:
		operation = int(input('\n Which option would you like to trade  na\n  1 - Digital\n  2 - Binaria\n  :: '))
		
		if operation > 0 and operation < 3 : break
	except:
		print('\n Invalid Option')

while True:
	try:
		tipo_mhi = int(input('which strategie \n  1 - Minoria\n  2 - Maioria\n  :: '))
		
		if tipo_mhi > 0 and tipo_mhi < 3 : break
	except:
		print('\n Invalid Option')


par = input(' Insert currency pair to trade: ').upper()
valor_entrada = float(input(' Entrace value: '))
valor_entrada_b = float(valor_entrada)

martingale = int(input('how many martingales? : '))
martingale += 1

stop_loss = float(input('Stop Loss: '))
stop_profit = float(input('Stop Profit: '))

gain = 0
payout = Payout(par)
while True:
	minutos = float(((datetime.now()).strftime('%M.%S'))[1:])
	entrar = True if (minutos >= 4.58 and minutos <= 5) or minutos >= 9.58 else False
	print('time to start?',entrar,'/ Minutes:',minutos)
	
	if entrar:
		print('\n\nStarting trade!')
		dir = False
		print('Verificando cores..', end='')
		velas = API.get_candles(par, 60, 3, time.time())
		
		velas[0] = 'g' if velas[0]['open'] < velas[0]['close'] else 'r' if velas[0]['open'] > velas[0]['close'] else 'd'
		velas[1] = 'g' if velas[1]['open'] < velas[1]['close'] else 'r' if velas[1]['open'] > velas[1]['close'] else 'd'
		velas[2] = 'g' if velas[2]['open'] < velas[2]['close'] else 'r' if velas[2]['open'] > velas[2]['close'] else 'd'
		
		cores = velas[0] + ' ' + velas[1] + ' ' + velas[2]		
		print(cores)
	
		if cores.count('g') > cores.count('r') and cores.count('d') == 0 : dir = ('put' if tipo_mhi == 1 else 'call')
		if cores.count('r') > cores.count('g') and cores.count('d') == 0 : dir = ('call' if tipo_mhi == 1 else 'put')
		
		if dir:
			print('Direction:',dir)
			
			valor_entrada = valor_entrada_b
			for i in range(martingale):
			
				status,id = API.buy_digital_spot(par, valor_entrada, dir, 1) if operation == 1 else API.buy(valor_entrada, par, dir, 1)
				
				if status:
					while True:
						try:
							status,valor = API.check_win_digital_v2(id) if operation == 1 else API.check_win_v3(id)
						except:
							status = True
							valor = 0
						
						if status:
							valor = valor if valor > 0 else float('-' + str(abs(valor_entrada)))
							gain += round(valor, 2)
							
							print('Results: ', end='')
							print('WIN /' if valor > 0 else 'LOSS /' , round(valor, 2) ,'/', round(gain, 2),('/ '+str(i)+ ' GALE' if i > 0 else '' ))
							
							valor_entrada = Martingale(valor_entrada, payout)
							
							stop(gain, stop_profit, stop_loss)
							
							break
						
					if valor > 0 : break
					
				else:
					print('\n Error\n\n')
				
	time.sleep(0.5)
