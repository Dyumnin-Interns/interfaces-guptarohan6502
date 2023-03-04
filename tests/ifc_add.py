import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly, NextTimeStep, FallingEdge, ClockCycles
from cocotb_bus.drivers import BusDriver
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db
from cocotb_bus.monitors import BusMonitor
from cocotb_coverage.coverage import  CoverCross, CoverPoint, coverage_db
from cocotb_bus.monitors import BusMonitor

import os
import random
import logging

@CoverPoint("top.p",  # noqa F405
            xf=lambda x, y: x,
            bins=[0, 1]
            )
@CoverPoint("top.r",  # noqa F405
            xf=lambda x, y: y,
            bins=[0, 1]
            )
@CoverCross("top.cross.pr",
            items=["top.p",
                   "top.r"
                   ]
            )
def pr_cover(p,r):
	print(p,r)
	pass

logging.basicConfig(level=logging.DEBUG)
global logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def sb_fn(actual_value):
	global expected_value
	#Convert actual value to decimal
	logger.info(f"Actual value is {int(actual_value)}")
	#logger.info(f"Expected value is {expected_value.pop(0)}")
	logger.info(f"Expected value is {expected_value[0]}")
	assert actual_value == expected_value.pop(0) , "Scoreboard Matching Failed"

def sb_cfg_fn(actual_value):
	pass
	#global expected_value
	#assert actual_value == expected_value.pop(0), "Scoreboard Matching Failed"

def get_int(signal):
	try:
		int_val = int(signal.value)
	except ValueError:
		int_val = 0

	return int_val

@cocotb.coroutine
async def detect_signal_change(dut, signal):
    prev_val = dut.signal.value.integer
    event = Event()
    while True:
        await event.wait()
        curr_val = dut.signal.value.integer
        if curr_val != prev_val:
            print("Signal changed from 0x{:08x} to 0x{:08x}".format(prev_val, curr_val))
            prev_val = curr_val
        event.clear()
        await RisingEdge(dut.clock)

@CoverPoint("top.prot.din.current", # noqa F405
		xf = lambda x: x['current'],
		bins = ['IDLE','READY','TXN']
		)
@CoverPoint("top.prot.din.previous", # noqa F405
		xf = lambda x: x['previous'],
		bins = ['IDLE','READY','TXN']
		)
@CoverCross("top.cross.din_prot.cross", # noqa F405
		items = ["top.prot.din.previous", "top.prot.din.current"],
		ign_bins = [('READY', 'IDLE')]
		)
def din_prot_cover(txn):
	pass

@cocotb.test()
async def ifc_add(dut):

	global expected_value 
	expected_value = []

	await FallingEdge(dut.CLK)
	dut.RST_N.value = 0
	await FallingEdge(dut.CLK)
	dut.RST_N.value = 1
	dut.dout_en.value = 0
	dut.cfg_en.value = 1
	dut.cfg_op.value = 1
	dut.cfg_address.value =0
	await FallingEdge(dut.CLK)
	dut.cfg_en.value = 0
	await RisingEdge(dut.CLK)
	#Till here we have reset the DUT and now we start sending signals
	
	In_drv = InputDriver(dut, 'din', dut.CLK,dut.cfg_en, dut.len_en)
	OutputDriver(dut, 'dout', dut.CLK, sb_fn)
	Len_drv = InputDriver(dut, 'len', dut.CLK)
	cfg_indrv = Cfg_InDriver(dut, 'cfg', dut.CLK)
	#cfg_outdrv = Cfg_OutDriver(dut, 'cfg', dut.CLK, sb_cfg_fn)

	IO_Monitor(dut, 'din', dut.CLK,callback = din_prot_cover)
	# Out_mon = IO_Monitor(dut, 'dout', dut.CLK)
	# Len_mon = IO_Monitor(dut, 'len', dut.CLK)
	# cfg_mon = IO_Monitor(dut, 'cfg', dut.CLK)


	#DC1 
	#list of 100 0s
	#lis_l = [[0 for i in range(random.randint(2,255))] for j in range(100)]

	#DC2
	#list of 255s
	#lis_l = [[255 for i in range(random.randint(2,255))] for j in range(100)]

	#DC3 
	#list of 1s
	lis_l = [[1 for i in range(random.randint(2,255))] for j in range(100)]

	#RC1
	#list of random numbers
	#lis_l = [[random.randint(0,255) for i in range(random.randint(2,255))] for j in range(100)]


	#list defines whether to have operation from the port or register
	port_reg = [random.randint(0,1) for i in range(len(lis_l))]

	# lis_l = [[2, 1, 23, 24], [16, 9, 10, 24, 11]]
	# port_reg = [1,0]

	print(lis_l, port_reg)

	
	prev_sw = None
	for list_n in range(len(lis_l)):

		
		L_n = lis_l[list_n]
		print(len(L_n))
		print(port_reg[0])
		current_sw = port_reg[0]
		
		cfg_indrv.append((4, port_reg[0]))
		await RisingEdge(dut.CLK)
		if(port_reg.pop(0) == 0):
			Len_drv.append(len(L_n))
		else:
			cfg_indrv.append((8,len(L_n)))
		if(prev_sw!= None):
			#print(prev_sw, current_sw)
			pr_cover(prev_sw, current_sw)

		sum = 0
		for i in range(len(L_n)):
			sum+=L_n[i]
		expected_value.append(sum%256)


		for i in range(len(L_n)):
			In_drv.append(L_n[i])
			await FallingEdge(dut.CLK)
		
		prev_sw = current_sw
		await FallingEdge(dut.dout_en)


	while len(expected_value) > 0:
		await Timer(2, 'ns')

	coverage_db.report_coverage(cocotb.log.info, bins = True)
	coverage_file = os.path.join(os.path.dirname(__file__), "coverage.xml")
	coverage_db.export_to_xml(filename = coverage_file)

class IO_Monitor(BusMonitor):
	_signals = ['rdy', 'en', 'value']

	async def _monitor_recv(self):
		fallingedge = FallingEdge(self.clock)
		rdonly = ReadOnly()
		phases = {
			0: 'IDLE',
			1: 'READY',
			3: 'TXN',
		}
		prev= 'IDLE'
		while True:
			await fallingedge
			await rdonly
			txn  = (self.bus.en.value <<1) | self.bus.rdy.value
			#logger.info(f"txn = {txn}")
			self._recv({'previous': prev, 'current': phases[txn]})
			prev = phases[txn]
			
# class IO_Monitor(BusMonitor):
#     _signals = ['rdy', 'en', 'data']

#     async def _monitor_recv(self):
#         fallingedge = FallingEdge(self.clock)
#         rdonly = ReadOnly()
#         phases = {
#             0: 'Idle',
#             1: 'Rdy',
#             3: 'Txn'
#         }
#         prev = 'Idle'
#         while True:
#             await fallingedge
#             await rdonly
#             txn = (self.bus.en.value << 1) | self.bus.rdy.value
#             self._recv({'previous': prev, 'current': phases[txn]})
#             prev = phases[txn]

class InputDriver(BusDriver):
	_signals = ['rdy', 'en', 'value']

	def __init__(self, dut, name, clk,cfg_en = None,len_en = None):
		BusDriver.__init__(self, dut, name, clk)
		self.bus.en.value = 0
		self.clk = clk
		self.cfg_en = cfg_en
		self.len_en = len_en

	async def _driver_send(self, value, sync=True):
		if self.bus.rdy.value != 1:
			await RisingEdge(self.bus.rdy)
		if(self.cfg_en!=None and self.len_en!=None):
			while(self.cfg_en.value ==1 or self.len_en.value == 1):
				await FallingEdge(self.clk)
		self.bus.en.value = 1
		self.bus.value.value = value
		await ReadOnly()
		await RisingEdge(self.clk)
		self.bus.en.value = 0
		await NextTimeStep()

class OutputDriver(BusDriver):
	_signals = ['rdy', 'en', 'value']
	def __init__(self, dut, name, clk, sb_callback):
		BusDriver.__init__(self, dut, name, clk)
		self.bus.en.value = 0
		self.clk = clk
		self.callback = sb_callback
		self.append(0)

	async def _driver_send(self, value, sync=True):
		while True:
			if self.bus.rdy.value != 1:
				await RisingEdge(self.bus.rdy)
			self.bus.en.value = 1
			await ReadOnly()
			self.callback(self.bus.value.value)
			# output  =get_int(self.bus.value)
			# logger.info(f"Output is {output}")
			await RisingEdge(self.clk)
			await NextTimeStep()
			self.bus.en.value = 0

class Cfg_InDriver(BusDriver):
	_signals = ['rdy', 'en','address', 'op', 'data_in', 'data_out']
	def __init__(self, dut, name, clk):
		BusDriver.__init__(self, dut, name, clk)
		self.bus.en.value = 0
		self.clk = clk
		self.append(0)

	async def _driver_send(self, value = (1,1), sync=True):
		#Value should be a tuple of (address, data)
		if(type(value) == tuple):
			if self.bus.rdy.value != 1:
				await RisingEdge(self.bus.rdy)
			self.bus.en.value = 1
			await ReadOnly()
			await RisingEdge(self.clk)
			self.bus.op.value = 1
			self.bus.address.value = value[0] & 0xFF
			if(value[0] == 4):
				self.bus.data_in.value = value[1] & 0b11
			elif(value[0] == 8):
				#logger.info(f"Writing {value[1] & 0xFF} to the register")
				await FallingEdge(self.clk)
				self.bus.data_in.value = value[1] & 0xFF
			await RisingEdge(self.clk)
			self.bus.en.value = 0
			await NextTimeStep()

class Cfg_OutDriver(BusDriver):
	_signals = ['rdy', 'en','address', 'op', 'data_in', 'data_out']

	def __init__(self, dut, name, clk, sb_callback):
		BusDriver.__init__(self, dut, name, clk)
		self.bus.en.value = 0
		self.clk = clk
		self.callback = sb_callback
		self.append(0)

	async def _driver_send(self, value, sync=True):
		#Value can be just address
		while True:
			if self.bus.rdy.value != 1:
				await RisingEdge(self.bus.rdy)
			self.bus.en.value = 1
			await ReadOnly()
			await RisingEdge(self.clk)
			self.bus.address.value = value
			self.bus.op.value = 0
			if(value == 0):
				self.callback(self.bus.data_out.value)
			if(value == 4):
				self.callback(self.bus.data_out.value & 0b11)
			if(value == 8):
				self.callback(self.bus.data_out.value & 0xFF)

			await RisingEdge(self.clk)
			await NextTimeStep()
			self.bus.en.value = 0
			self.bus.op.value =1


