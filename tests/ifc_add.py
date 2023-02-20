import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly, NextTimeStep, FallingEdge
from cocotb_bus.drivers import BusDriver
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db
from cocotb_bus.monitors import BusMonitor
import os
import random
import logging

logging.basicConfig(level=logging.DEBUG)
global logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def sb_fn(actual_value):
	global expected_value
	#Convert actual value to decimal
	logger.info(f"Actual value is {int(actual_value)}")
	#logger.info(f"Expected value is {expected_value.pop(0)}")
	#assert actual_value == expected_value.pop(0), "Scoreboard Matching Failed"

def sb_cfg_fn(actual_value):
	global expected_value
	assert actual_value == expected_value.pop(0), "Scoreboard Matching Failed"

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



@cocotb.test()
async def ifc_add(dut):

	global expected_value 
	expected_value = []

	await FallingEdge(dut.CLK)
	dut.RST_N.value = 0
	await FallingEdge(dut.CLK)
	dut.RST_N.value = 1
	dut.dout_en.value = 0
	#Till here we have reset the DUT and now we start sending signals
	In_drv = InputDriver(dut, 'din', dut.CLK)
	Out_drv = OutputDriver(dut, 'dout', dut.CLK, sb_fn)
	Len_drv = InputDriver(dut, 'len', dut.CLK)
	op_val = [1]
	
	#list of lists of random numbers 4,5,6,7 in length such that sum of numbers in list is less than 256
	# lis_l = [[random.randint(0,25) for i in range(random.randint(4,7))] for j in range(10)]
	lis_l = [[2, 1, 23, 24], [16, 9, 10, 24, 11]]
	print(lis_l)
	for list_n in range(len(lis_l)):
		L_n = lis_l[list_n]
		print(L_n)
		print("Starting the test")

		if dut.cfg_rdy.value != 1:
			await RisingEdge(dut.cfg_rdy)
		await FallingEdge(dut.CLK)
		dut.cfg_en.value = 1
		dut.cfg_address.value = 4
		dut.cfg_op.value = 1
		await FallingEdge(dut.CLK)
		dut.cfg_data_in.value =0b0
		await FallingEdge(dut.CLK)
		dut.cfg_en.value = 0
		await FallingEdge(dut.CLK)
		Len_drv.append(len(L_n))
		await FallingEdge(dut.CLK)
		dut.cfg_en.value = 1
		dut.cfg_address.value = 0
		dut.cfg_op.value = 0
		await FallingEdge(dut.CLK)
		assert ((get_int(dut.cfg_data_out)>>8) & 0xF) == len(L_n), "Length is not matching"
		await FallingEdge(dut.CLK)
		#cfg_drv = In_OutDriver(dut, 'cfg', dut.CLK, sb_cfg_fn)



		#Giving Input Values
		#Giving Input Values
		sum = 0
		for i in range(len(L_n)):
			sum+=L_n[i]
		assert sum <= 2**8, "Sum of the list is greater than 8 bits"
		expected_value.append(sum)

		for i in range(len(L_n)):
			sum+=L_n[i]
			In_drv.append(L_n[i])
			await FallingEdge(dut.CLK)
		await FallingEdge(dut.CLK)


	# while len(expected_value) > 0:
	# 	await Timer(2, 'ns')



class InputDriver(BusDriver):
	_signals = ['rdy', 'en', 'value']

	def __init__(self, dut, name, clk):
		BusDriver.__init__(self, dut, name, clk)
		self.bus.en.value = 0
		self.clk = clk

	async def _driver_send(self, value, sync=True):
		if self.bus.rdy.value != 1:
			await RisingEdge(self.bus.rdy)
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

class In_OutDriver(BusDriver):
	_signals = ['rdy', 'en','address', 'op', 'data_in', 'data_out']
	def __init__(self, dut, name, clk, sb_callback):
		BusDriver.__init__(self, dut, name, clk)
		self.bus.en.value = 0
		self.clk = clk
		self.callback = sb_callback
		self.append(0)


	async def _driver_send(self, value, sync=True):
		if self.bus.rdy.value != 1:
			await RisingEdge(self.bus.rdy)
		self.bus.en.value = 1
		await ReadOnly()
		if(self.bus.op.value == 1):
			if(self.bus.address.value == 4):
				self.bus.data_in.value  = value
			elif(self.bus.address.value == 8):
				self.bus.data_in.value = (self.bus.data_in.value) | (value & 0xFF)
		await RisingEdge(self.clk)
		self.bus.en.value = 0
		await NextTimeStep()
	
	async def _driver_get(self, value, sync=True):
		while True:
			await FallingEdge(self.bus.op)
			if self.bus.rdy.value != 1:
				await RisingEdge(self.bus.rdy)
			self.bus.en.value = 1
			await ReadOnly()
			if(self.bus.op.value == 0):
				if(self.bus.address.value == 0):
					self.callback(self.bus.data_out.value)
				if(self.bus.address.value == 4):
					self.callback(self.bus.data_out.value & 0b11)
				if(self.bus.address.value == 8):
					self.callback(self.bus.data_out.value & 0xFF)
			# output = get_int(self.bus.value)
			# logger.info(f"Output is {output}")	
			await RisingEdge(self.clk)
			await NextTimeStep()
			self.bus.en.value = 0


