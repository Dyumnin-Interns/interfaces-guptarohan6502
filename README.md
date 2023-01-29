# IP Introduction

A typical DUT has 3 set's of interfaces

1. Data Interface
2. Control Interface
3. Configuration Interface

The data interface is used for Data I/O

The control interface is used by other hardware to control or change the behavior of the IP

The configuration interface is used by the processor to change the behavior of the IP.

# IP Functionality

* It uses the RDY EN Protocol on all interfaces
* The DUT takes N 8 bit input values. Adds them and outputs the result.
* The Value of N can be provided either
	* At the Interface via the `length` port
	* Or via the length register accessible via the configuration register.
* The decision on which length is used (port or register) is controlled via a bit in the configuration space.  
* Once the DUT starts accumulating the bytes it ignores changes to the length field or register until it has generated the output.

# Interfaces

| Port         | Direction | Width | Description                                         |
| --           | --        | --    | ------                                              |
| din_rdy      | out       | 1     | RDY for Input data                                  |
| din_en       | in        | 1     | EN for Input data                                   |
| din_value    | in        | 8     | Data                                                |
| dout_rdy     | out       | 1     | RDY for Output data                                 |
| dout_en      | in        | 1     | EN for output data                                  |
| dout_value   | out       | 8     | Accumulated data output                             |
| len_rdy      | out       | 1     | RDY for Length                                      |
| len_en       | in        | 1     | EN for length                                       |
| len_value    | in        | 8     | Number of bytes that should be accumulated          |
| cfg_rdy      | out       | 1     | RDY for Configuration Interface                     |
| cfg_en       | in        | 1     | EN for Configuration Interface                      |
| cfg_address  | in        | 8     | Address of the register  in cfg space               |
| cfg_op       | in        | 1     | Operation type, 0=Read, 1=Write                     |
| cfg_data_in  | in        | 32    | The data that needs to be written, ignored for read |
| cfg_data_out | out       | 32    | The data returned by read operation                 |

# Configuration Space Register Map

| Address | Access | Bit map | reset value | Field             | Description                                                                      |
| ---     | ---    | ---     | ---         | ---               | ------                                                                           |
| 0       | R      | 7:0     | 0           | current_count     | The count of bytes processed                                                     |
| 0       | R      | 15:8    | 0           | programmed_length | The length programmed for this session                                           |
| 0       | R      | 16      | 0           | busy              | An operation has started and is ongoing                                          |
| 4       | R/W    | 0       | 0           | s/w override      | 0 => use len from port. 1=>use len from register                                 |
| 4       | R/W    | 1       | 0           | pause             | 0 => normal mode. 1=>Input Rdy will be deasserted after end of current data set. |
| 8       | R/W    | 7:0     | 0           | len               | len register                                                                     |
