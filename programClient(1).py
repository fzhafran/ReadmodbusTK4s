import time
import datetime as dt
from urllib.parse import urlencode
from urllib.request import Request,urlopen
import mysql.connector

from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.transaction import ModbusRtuFramer

from pymodbus.constants import Defaults
Defaults.RetryOnEmpty=True
Defaults.Timeout= 0.25
Defaults.Retries= 3

client=ModbusClient('10.22.29.60', port=5000, framer=ModbusRtuFramer)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="databasefanur1"
)

mycursor = mydb.cursor()

#deklarasi
start = False
datapvvel=[]
datapvtemp=[]
datapvrh=[]
datapvpres=[]
datapvlux=[]
datapv=[datapvvel,datapvtemp,datapvrh,datapvpres,datapvlux]
writelist = "(maxvel,minvel,avgvel,maxtemp,mintemp,avgtemp,maxrh,minrh,avgrh,maxpres,minpres,avgpres,maxlux,minlux,avglux)"
writeSet = [1005,1000,1015,1010,1020]

qErr = 'DISCONNECT'
qSave = 'CONNECT'
strpvt = ''
strsvt = ''
strpvv = ''
strsvv = ''
durasi = 0
menit = 5
logTime = menit*60000 #sampling (a) menit sekali
currsVel = 0 
currsTemp = 0
currsLux = 0 
currsRh = 0
currsPres = 0

setparam 		= ["s_velocity","s_temperature","s_pressure","s_rh","s_lux"]
out 			= ["output1","output2","output3","output4","output5","output6"]
regoutput 		= [3200,3201,3202,3203,3204,3205]
alarmaddress 	= [1008,1003,1018,1013,1023]

param 			= ["VELOCITY","TEMPERATURE","PRESSURE","RH","LUX"]
startdate		= ["","","","",""]
enddate			= ["","","","",""]
alarm			= ["","","","",""]
alarmstat		= ["","","","",""]
savealstat		= ["","","","",""]
currAlarm		= [False,False,False,False,False]
setAl			= ["off","off","off","off","off"]
alarmset 		= ["alarmvel","alarmtemp","alarmrh","alarmpres","alarmlux"]
alarmstatset 	= ["alstatvel","alstattemp","alstatrh","alstatpres","alstatlux"]

#program realtime
def register_word():
	#Ambil dan baca data dari PLC - HMI
	regPlc = client.read_holding_registers(address=1000, count=30, unit=0) #baca data word/analog dari address 1000 ke 1019
	
	intsvt 			= int(regPlc.registers[0])	#1000 - set value temperature
	intpvt 			= int(regPlc.registers[1])	#1001 - present value temperature
	runtemp 		= int(regPlc.registers[2])	#1002 - run temperature
	h_alarmtemp 	= int(regPlc.registers[3])	#1003 - Alarm HIGH temperature
	l_alarmtemp 	= int(regPlc.registers[4])	#1004 - Alarm LOW temperature

	intsvv 		= int(regPlc.registers[5])		#1005 - set value velocity
	intpvv 		= int(regPlc.registers[6])		#1006 - present value velocity
	runvel		= int(regPlc.registers[7])		#1007 - run velocity
	h_alarmvel	= int(regPlc.registers[8])		#1008 - Alarm HIGH velocity
	l_alarmvel 	= int(regPlc.registers[9])		#1009 - Alarm LOW velocity

	intsvrh 	= int(regPlc.registers[10])		#1010 - set value RH
	intpvrh 	= int(regPlc.registers[11])		#1011 - present value RH
	runrh		= int(regPlc.registers[12])		#1012 - run rh
	h_alarmrh	= int(regPlc.registers[13])		#1013 - Alarm HIGH rh
	l_alarmrh	= int(regPlc.registers[14])		#1014 - Alarm LOW rh

	intsvpres 	= int(regPlc.registers[15])		#1015 - set value pressure
	intpvpres 	= int(regPlc.registers[16])		#1016 - present value pressure
	runpres		= int(regPlc.registers[17])		#1017 - run pressure
	h_alarmpres	= int(regPlc.registers[18])		#1018 - Alarm HIGH pressure
	l_alarmpres	= int(regPlc.registers[19])		#1019 - Alarm LOW pressure

	intsvlux 	= int(regPlc.registers[20])		#1020 - set value lux
	intpvlux 	= int(regPlc.registers[21])		#1021 - present value lux
	runlux		= int(regPlc.registers[22])		#1022 - run lux
	h_alarmlux	= int(regPlc.registers[23])		#1023 - Alarm HIGH lux
	l_alarmlux	= int(regPlc.registers[24])		#1024 - Alarm LOW lux

	intsvnh3 	= int(regPlc.registers[25])		#1025 - set value NH3
	intpvnh3 	= int(regPlc.registers[26])		#1026- present value NH3
	runnh3		= int(regPlc.registers[27])		#1027- run value NH3
	h_alarmnh3	= int(regPlc.registers[28])		#1028 - Alarm HIGH NH3
	l_alarmnh3	= int(regPlc.registers[29])		#1029 - Alarm LOW NH3

	strsvt = str(intsvt)	#set value temperature
	strpvt = str(intpvt)	#present value temperature
	strsvv = str(intsvv)	#set value velocity
	strpvv = str(intpvv)	#present value velocity
	strsvrh = str(intsvrh)	#set value rh
	strpvrh = str(intpvrh)  #present value rh
	strsvpres = str(intsvpres)	#set value pressure
	strpvpres = str(intpvpres)	#present value pressure
	strsvlux = str(intsvlux)	#set value lux
	strpvlux = str(intpvlux) 	#present value pressure
	strsvnh3 = str(intsvnh3)	#set value NH3
	strpvnh3 = str(intpvnh3)	#present value NH3

	return strpvv,strpvt,strpvrh,strpvpres,strpvlux,strsvv,strsvt,strsvrh,strsvpres,strsvlux,h_alarmvel,h_alarmtemp,h_alarmrh,h_alarmpres,h_alarmlux,l_alarmvel,l_alarmtemp,l_alarmrh,l_alarmpres,l_alarmlux

def read_word(strpvv,strpvt,strpvrh,strpvpres,strpvlux):

	sqlpvv = "UPDATE realtime SET velocity = %s  WHERE id = %s"
	valpvv = (strpvv,"13")

	sqlpvt = "UPDATE realtime SET temperature = %s WHERE id = %s"
	valpvt = (strpvt,"13")

	sqlpvrh = "UPDATE realtime SET rh = %s  WHERE id = %s"
	valpvrh = (strpvrh,"13")

	sqlpvlux = "UPDATE realtime SET lux = %s WHERE id = %s"
	valpvlux = (strpvlux,"13")

	sqlpvpres = "UPDATE realtime SET pressure = %s WHERE id = %s"
	valpvpres = (strpvpres,"13")

	sqlnotice = "UPDATE realtime SET notice = %s WHERE id = %s"
	valnotice = (qSave,"13")

	# sqlsvv = "UPDATE realtime SET s_velocity = %s  WHERE id = %s"
	# valsvv = (strsvv,"1")

	# sqlsvt = "UPDATE realtime SET s_temperature = %s WHERE id = %s"
	# valsvt = (strsvt,"1")

	# sqlsvrh = "UPDATE realtime SET s_rh = %s  WHERE id = %s"
	# valsvrh = (strsvrh,"1")

	# sqlsvlux = "UPDATE realtime SET s_lux = %s WHERE id = %s"
	# valsvlux = (strsvlux,"1")

	# sqlsvpres = "UPDATE realtime SET s_pressure = %s WHERE id = %s"
	# valsvpres = (strsvpres,"1")

	mycursor.execute(sqlpvv,valpvv)
	mycursor.execute(sqlpvt,valpvt)
	mycursor.execute(sqlpvrh,valpvrh)
	mycursor.execute(sqlpvlux,valpvlux)
	mycursor.execute(sqlpvpres,valpvpres)
	# mycursor.execute(sqlsvv,valsvv)
	# mycursor.execute(sqlsvt,valsvt)
	# mycursor.execute(sqlsvrh,valsvrh)
	# mycursor.execute(sqlsvlux,valsvlux)
	# mycursor.execute(sqlsvpres,valsvpres)
	mycursor.execute(sqlnotice,valnotice)

# memasukkan paramater di autonics
def config(currsVel,currsTemp,currsPres,currsRh,currsLux,writeSet):
	# ambil dari database
	s = []
	for x in range(5):
		sql_Query = "select " 
		sql_Query += setparam[x] 
		sql_Query += " from realtime where id =%s"
		id = (13,)
		cursor = mydb.cursor()
		cursor.execute(sql_Query, id)
		setparameter = cursor.fetchone()
		sparam = int(setparameter[0])
		s.append(sparam)

	currsVel = int(currsVel)
	currsTemp = int(currsTemp)
	currsPres = int(currsPres)
	currsRh = int(currsRh)
	currsLux = int(currsLux)
	cur = [currsVel,currsTemp,currsPres,currsRh,currsLux]

	for x in range(5):
		if cur[x] != s[x]:
			cur[x] = s[x]
			client.write_registers(writeSet[x], [s[x]]*1, unit=0)
			# print("set2")
	return s[0],s[1],s[2],s[3],s[4]

# Program I/O digital
def input_digital():
	regBit = client.read_coils(3200, 6, unit=0) #baca data bit/digital dari address 2000 ke 2019
	writeDigital = [1100,1101,1102,1103,1104]
	strbit=[]

	for x in range(6):
		reg = regBit.bits[x]
		if reg == False:
			strbit.append("0")
		else:
			strbit.append("1")
			
		sql_Query = "select " 
		sql_Query += out[x] 
		sql_Query += " from realtime where id =%s"
		id = (13,)
		cursor = mydb.cursor()
		cursor.execute(sql_Query, id)
		setBit = cursor.fetchone()
		sBit = int(setBit[0])
		currsBit = int(strbit[x])

		# PROGRAM UNTUK DIGITAL INPUT
		# if currsBit != sBit:
		# 	if sBit == 0:
		# 		client.write_coils(regoutput[x] , [False]*1, unit=0)
		# 		client.write_registers(writeDigital[x], [0]*1, unit=0)
		# 	else:
		# 		client.write_coils(regoutput[x] , [True]*1, unit=0)
		# 		client.write_registers(writeDigital[x], [1]*1, unit=0)
		# 	strbit[x] = str(sBit)
		# 	print("set")
		
		bitsql = "UPDATE realtime SET "
		bitsql += out[x]
		bitsql += " = %s  WHERE id = %s"
		bitval = (strbit[x],"13")
		mycursor.execute(bitsql,bitval)

# masukkan ke masing-masing dataArray
def datainput(dataArray,datapv):
	for x in range(5):
		number = int(dataArray[x])
		datapv[x].append(number)
	
	return datapv

def dataprocess(datainput):
	avg = [0,0,0,0,0]
	maks = [0,0,0,0,0]
	minim = [0,0,0,0,0]
	for x in range(5):
		jumlah = 0
		for y in datainput[x]:
			jumlah = jumlah + y
		avg[x] = round((jumlah / len(datainput[x])),2)
		maks[x] = max(datainput[x])
		minim[x] = min(datainput[x])

	return maks,minim,avg

#program logger ke database
def function_log(dataprocess,writelist):
	sql = "INSERT INTO tabelparameter " 
	sql += writelist
	sql +=" VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
	val = (dataprocess[0][0],dataprocess[1][0],dataprocess[2][0],dataprocess[0][1],dataprocess[1][1],dataprocess[2][1],dataprocess[0][2],dataprocess[1][2],dataprocess[2][2],dataprocess[0][3],dataprocess[1][3],dataprocess[2][3],dataprocess[0][4],dataprocess[1][4],dataprocess[2][4])
	mycursor.execute(sql,val)
	

#if koneksi error
def koneksiError():
	print('koneksi gagal')
	sqlnotice = "UPDATE realtime SET notice = %s WHERE id = %s"
	valnotice = (qErr,"13")
	mycursor.execute(sqlnotice,valnotice)

# Fungsi Alarm
def AlarmFunc(dataArray,alarmset,alarm,alarmstatset,alarmstat,savealstat,currAlarm,startdate,enddate,param):
	for x in range(5):
		h_alarmval 	= int(dataArray[x+10])
		l_alarmval = int(dataArray[x+15])

		if h_alarmval == 0 and l_alarmval == 0:
			alarm[x] = "off"
		else:
			alarm[x] = "on"
			if h_alarmval != 0 and l_alarmval == 0:
				alarmstat[x] = "HIGH"
			elif h_alarmval == 0 and l_alarmval != 0:
				alarmstat[x] = "LOW"
			else:
				alarmstat[x] = ""
		
		alsql 	= "UPDATE realtime SET "
		alsql 	+= alarmset[x]
		alsql 	+= " = %s  WHERE id = %s"
		alval 	= (alarm[x],"13")
		mycursor.execute(alsql,alval)

		alsql 	= "UPDATE realtime SET "
		alsql 	+= alarmstatset[x]
		alsql 	+= " = %s  WHERE id = %s"
		alval 	= (alarmstat[x],"13")
		mycursor.execute(alsql,alval)

		if alarm[x] == "on":
			if currAlarm[x] == False:
				dtime 		 = dt.datetime.now()
				startdate[x] = dtime.strftime("%Y-%m-%d %H:%M:%S")
				savealstat[x] = alarmstat[x]
				dtsql 		 = "INSERT INTO alarm (parameter,startdate,keterangan,work) VALUES (%s,%s,%s,%s)"
				dtval 		 = (param[x],startdate[x],savealstat[x],param[x])
				mycursor.execute(dtsql,dtval)
				currAlarm[x] = True
		
		if alarm[x] == "off":
			if currAlarm[x] == True:
				dtime 		 = dt.datetime.now()
				enddate[x] 	 = dtime.strftime("%Y-%m-%d %H:%M:%S")
				endsql 		 = "UPDATE alarm SET enddate"
				endsql 		 += " = %s  WHERE work = %s"
				endval 		 = (enddate[x],param[x])
				ketsql 		 = "UPDATE alarm SET keterangan"
				ketsql 		 += " = %s  WHERE work = %s"
				ketval 		 = (savealstat[x],param[x])
				worksql 	 = "UPDATE alarm SET work"
				worksql 	 += " = %s  WHERE work = %s"
				workval 	 = ("",param[x])
				mycursor.execute(endsql,endval)
				mycursor.execute(ketsql,ketval)
				mycursor.execute(worksql,workval)
				currAlarm[x] = False

# Program berjalan
while True:
	currentmilliseconds = int(round(time.time() * 1000))
	try:
		client.connect()
		input_digital()
		dataString = register_word()
		read_word(dataString[0],dataString[1],dataString[2],dataString[3],dataString[4])
		datapv = datainput(dataString,datapv)
		AlarmFunc(dataString,alarmset,alarm,alarmstatset,alarmstat,savealstat,currAlarm,startdate,enddate,param)
		currSet = config(dataString[5],dataString[6],dataString[8],dataString[7],dataString[9],writeSet)
		currsVel = currSet[0]
		currsTemp = currSet[1]
		currsPres = currSet[2]
		currsRh = currSet[3]
		currsLux = currSet[4]
	except:
		koneksiError()
	currentmilliseconds = int(round(time.time() * 1000)) - currentmilliseconds
	durasi += currentmilliseconds

	try:	
		if durasi > logTime: 
			hasilproses = dataprocess(datapv)
			# function_log(dataString)
			function_log(hasilproses,writelist)

			# reset
			datapvvel=[]
			datapvtemp=[]
			datapvrh=[]
			datapvpres=[]
			datapvlux=[]
			datapv=[datapvvel,datapvtemp,datapvrh,datapvpres,datapvlux]

			durasi = 0
	except:
		print('data tidak tersedia.')
	mydb.commit()
	client.close()
	print(currentmilliseconds,'\t',durasi)
