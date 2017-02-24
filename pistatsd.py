import sys
import sched, time

# check for appropriate command line arguments
if (len(sys.argv) != 9 or len(sys.argv) != 9):
	print('usage: pistatsd -b <message_broker> [-p <virtual_host>] [-c <login>:<password>] -k <routing_key>')
	sys.exit(2)
elif sys.argv[1] != "-b":
	print('usage: pistatsd -b <message_broker> [-p <virtual_host>] [-c <login>:<password>] -k <routing_key>')
	sys.exit(2)
elif sys.argv[3] != "[-p" and sys.argv[3] != "[-c":
	print('usage: pistatsd -b <message_broker> [-p <virtual_host>] [-c <login>:<password>] -k <routing_key>')
	sys.exit(2)
elif sys.argv[3] == "[-p":
	if sys.argv[4][len(sys.argv[4])-1] != "]":
		print('usage: pistatsd -b <message_broker> [-p <virtual_host>] [-c <login>:<password>] -k <routing_key>')
		sys.exit(2)
	elif sys.argv[5] != "[-c" or sys.argv[6][len(sys.argv[6])-1] != "]":
		print('usage: pistatsd -b <message_broker> [-p <virtual_host>] [-c <login>:<password>] -k <routing_key>')
		sys.exit(2)
	elif sys.argv[7] != "-k":
		print('usage: pistatsd -b <message_broker> [-p <virtual_host>] [-c <login>:<password>] -k <routing_key>')
		sys.exit(2)
elif sys.argv[3] == "[-c":
	if sys.argv[3] != "[-c" or sys.argv[4][len(sys.argv[4])-1] != "]":
		print('usage: pistatsd -b <message_broker> [-p <virtual_host>] [-c <login>:<password>] -k <routing_key>')
		sys.exit(2)
	elif sys.argv[5] != "-k":
		print('usage: pistatsd -b <message_broker> [-p <virtual_host>] [-c <login>:<password>] -k <routing_key>')
		sys.exit(2)

# gather information from command line
message_broker = sys.argv[2]
if len(sys.argv) == 9:
	virtual_host = sys.argv[4]
	virtual_host = virtual_host[:len(virtual_host)-1]
else:
	virtual_host = "/"
if len(sys.argv) == 9:
	loginpassword = sys.argv[6]
else:
	loginpassword = sys.argv[4]
loginpassword = loginpassword[:len(loginpassword)-1]
loginpassword = loginpassword.split(":")
if len(loginpassword) != 2:
	print('usage: pistatsd -b <message_broker> [-p <virtual_host>] [-c <login>:<password>] -k <routing_key>')
	sys.exit(2)
login = loginpassword[0]
password = loginpassword[1]
if len(sys.argv) == 9:
	routing_key = sys.argv[8]
else:
	routing_key = sys.argv[6]

# for timing interface
s = sched.scheduler(time.time, time.sleep)

# function to run every second
def getTimes(sc, oldUp, oldIdle, oldwlanRec, oldwlanTran, oldloRec, oldloTran, oldethRec, oldethTran, time):
	with open('/proc/uptime') as f:
		readTimes = f.readlines()
	with open('/proc/net/dev') as f:
		readNet = f.readlines()
	# increment time
	time += 1
	print('\n\nat time: ' + str(time))
	# gather all new readings
	times = readTimes[0].split(' ')
	newUp = times[0]
	newIdle = times[1]
	newIdle = newIdle[:len(newIdle)-1]
	wlan = readNet[2]
	wlan = wlan.split(' ')
	newwlanRec = wlan[2]
	newwlanTran = wlan[37]
	wlan0rx = float(newwlanRec) - float(oldwlanRec) #wlan0:rx on JSON
	wlan0tx = float(newwlanTran) - float(oldwlanTran) #wlan0:tx on JSON
	
	lo = readNet[3]
	lo = lo.split(' ')
	newloRec = lo[7] 
	newloTran = lo[52]
	lorx = float(newloRec) - float(oldloRec) #lo:rx on JSON
	lotx = float(newloTran) - float(oldloTran) #lo:tx on JSON
	
	eth = readNet[4]
	eth = eth.split(' ')
	newethRec = eth[9] 
	newethTran = eth[52]
	eth0rx = float(newethRec) - float(oldethRec) #eth0:rx on JSON
	eth0tx = float(newethTran) - float(oldethTran) #eth0:tx on JSON
	
	# print relevant information and send JSON message only
	# after initial values have been taken
	
	if time != 1:
		print('wlan0:\n\trx: ' + str(wlan0rx))
		print('\ttx: ' + str(wlan0tx))
		print('lo:\n\trx: ' + str(lorx))
		print('\ttx: ' + str(lotx))
		print('eth0:\n\trx: ' + str(eth0rx))
		print('\ttx: ' + str(eth0tx))
		
		
		print('\nold uptime: ' + str(oldUp))
		print('new uptime: ' + str(newUp))
		print('old idle time: ' + str(oldIdle))
		print('new idle time: ' + str(newIdle))
		deltaIdle = float(newIdle) - float(oldIdle)
		deltaIdle = deltaIdle/4 #adjusted for four cores on Rpi
		print('change in idle time (per core): ' + str(deltaIdle))
		deltaUp = float(newUp) - float(oldUp)
		print('change in uptime: ' + str(deltaUp))
		util = (deltaIdle/deltaUp)
		util = 1 - util
		print('utilization: ' + str(util)) # marked as cpu in JSON
	s.enter(1, 1, getTimes, (sc,newUp,newIdle,newwlanRec, newwlanTran, newloRec, newloTran, newethRec, newethTran,time,))
	
# runs function every second
s.enter(1, 1, getTimes, (s,0,0,0,0,0,0,0,0,0,))
s.run()