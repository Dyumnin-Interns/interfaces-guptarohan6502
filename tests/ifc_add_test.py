import cocotb
from cocotb.triggers import Timer, RisingEdge, ReadOnly, NextTimeStep, FallingEdge
from cocotb_bus.drivers import BusDriver
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db
from cocotb_bus.monitors import BusMonitor
import os
import random
import logging
def sb_fn(actual_value):
    global expected_value
    assert actual_value == expected_value.pop(0), "Scoreboard Matching Failed"
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
			output  =get_int(self.bus.value)
			logger.info(f"Output is {output}")
			await RisingEdge(self.clk)
			await NextTimeStep()
			self.bus.en.value = 0

def get_int(signal):
	try:
		int_val = int(signal.value)
	except ValueError:
		int_val = 0

	return int_val


logging.basicConfig(level = logging.NOTSET)
global logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# @cocotb.test()
# async def ifc_add(dut):
# 	""" Simple test to check if Dut adds N values"""
# 	N =5
# 	L_n = [4,5,1,6,7,10]
# 	await FallingEdge(dut.CLK)
# 	dut.RST_N.value = 0
# 	await FallingEdge(dut.CLK)
# 	dut.RST_N.value = 1
# 	dut.dout_en.value = 0
# 	#Till here we have reset the DUT and now we start sending signals

# 	if dut.len_rdy.value != 1:
#             	await RisingEdge(dut.len_rdy)
# 	await FallingEdge(dut.CLK)
# 	dut.len_en.value = 1
# 	dut.len_value.value = len(L_n)
# 	await FallingEdge(dut.CLK)
# 	dut.len_en.value = 0


# 	if dut.cfg_rdy.value != 1:
# 		await RisingEdge(dut.cfg_rdy)
# 	await FallingEdge(dut.CLK)
# 	dut.cfg_en.value = 1
# 	dut.cfg_address.value = 4
# 	dut.cfg_op.value = 1
# 	dut.cfg_data_in.value =0
# 	await FallingEdge(dut.CLK)
# 	dut.cfg_en.value = 0

# 	for i in range(len(L_n)):
# 		if dut.din_rdy.value !=1:
# 			await RisingEdge(dut.din_rdy)
# 		await FallingEdge(dut.CLK)
# 		dut.din_en.value =1
# 		dut.din_value.value = L_n[i]
# 		await FallingEdge(dut.CLK)
# 		dut.din_en.value =0

# 	if dut.cfg_rdy.value != 1:
# 		await RisingEdge(dut.cfg_rdy)
# 	await FallingEdge(dut.CLK)
# 	dut.cfg_en.value = 1
# 	dut.cfg_address.value = 0
# 	dut.cfg_op.value = 0
# 	logger.info(f"{get_int(dut.cfg_data_out)}")

# 	await FallingEdge(dut.CLK)
# 	dut.cfg_en.value = 0


# 	if(dut.dout_rdy.value !=1):
# 		await RisingEdge(dut.dout_rdy)

# 	output  =get_int(dut.dout_value)
# 	logger.info(f"Output is {output}")


# @cocotb.test()
# async def ifc_conf(dut):
# 	""" write and readin config space..."""
# 	N =5
# 	L_n = [4,5,1,6,7,10]
# 	await FallingEdge(dut.CLK)
# 	dut.RST_N.value = 0
# 	await FallingEdge(dut.CLK)
# 	dut.RST_N.value = 1
# 	dut.dout_en.value = 0
# 	#Till here we have reset the DUT and now we start sending signals
# 	# cgf_data_out = dut.cgf_data_out.value.intege
# 	# fifth_bit = (cgf_data_out >> 4) & 0x1
# 	#data = 0b10010000
# 	data = 144
# 	if dut.cfg_rdy.value != 1:
# 		await RisingEdge(dut.cfg_rdy)
# 	await FallingEdge(dut.CLK)
# 	dut.cfg_en.value = 1
# 	dut.cfg_address.value = 4
# 	dut.cfg_op.value = 1
# 	dut.cfg_data_in.value =0
# 	await FallingEdge(dut.CLK)
# 	#dut.cfg_data_in.value = (dut.cfg_data_in.value & ~(1 << 6)) | (1 << 6)
# 	#dut.cfg_data_in.value = (dut.cfg_data_in.value & 0xFF) | (data << 8)
# 	#dut.cfg_data_in.value = (dut.cfg_data_in.value & 0xFF) | (data << 8)
# 	#dut.cfg_data_in.value = (dut.cfg_data_in.value & 0xFF) | (0xFF << 8)
# 	dut.cfg_data_in.value = (dut.cfg_data_in.value) | (data<<1)
# 	await FallingEdge(dut.CLK)
# 	dut.cfg_en.value = 0
# 	await NextTimeStep()

# 	output  =get_int(dut.cfg_data_in)
# 	logger.info(f"Output is {output}")
# 	logger.info(f"Output is {(output) & 0xFF}") # To read from 7:0 bits
# 	logger.info(f"Output is {(output  >> 8) & 0xFF}") # To read from 15:8 bits

@cocotb.test()
async def ifc_add(dut):
	""" Simple test to check if Dut adds N values frpm config space..."""
	N =5
	L_n = [4,5,1,6,7,10]
	await FallingEdge(dut.CLK)
	dut.RST_N.value = 0
	await FallingEdge(dut.CLK)
	dut.RST_N.value = 1
	dut.dout_en.value = 0
	#Till here we have reset the DUT and now we start sending signals
	OutputDriver(dut, 'dout', dut.CLK, sb_fn)

	if dut.cfg_rdy.value != 1:
		await RisingEdge(dut.cfg_rdy)
	await FallingEdge(dut.CLK)
	dut.cfg_en.value = 1
	dut.cfg_address.value = 4
	dut.cfg_op.value = 1
	await FallingEdge(dut.CLK)
	dut.cfg_data_in.value =0b1
	await FallingEdge(dut.CLK)
	dut.cfg_address.value = 8
	dut.cfg_op.value = 1
	await FallingEdge(dut.CLK)
	dut.cfg_data_in.value = len(L_n)-2
	await FallingEdge(dut.CLK)
	dut.cfg_en.value = 0

	for i in range(len(L_n)):
		if dut.din_rdy.value !=1:
			await RisingEdge(dut.din_rdy)
		await FallingEdge(dut.CLK)
		dut.din_en.value =1
		dut.din_value.value = L_n[i]
		await FallingEdge(dut.CLK)
		dut.din_en.value =0


	# if dut.cfg_rdy.value != 1:
	# 	await RisingEdge(dut.cfg_rdy)
	# await FallingEdge(dut.CLK)
	# dut.cfg_en.value = 1
	# dut.cfg_address.value = 0
	# dut.cfg_op.value = 0
	# logger.info(f"{get_int(dut.cfg_data_out)}")
	# await FallingEdge(dut.CLK)
	# dut.cfg_en.value = 0


	# if(dut.dout_rdy.value !=1):
	# 	await RisingEdge(dut.dout_rdy)
	# dut.dout_en.value = 1
	# output  =get_int(dut.dout_value)
	# logger.info(f"Output is {output}")


