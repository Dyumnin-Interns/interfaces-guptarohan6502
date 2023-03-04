# Testplan

Testplan:
1. Data Interface - It is used for I/o
2. Control Interface - Used by other hardware to control or  change behaviour of IP
3. Configutation interface - Used by processor to change the behaviour of IP

3 interfaces 3 RDY/EN Protocol

Lenght port is used to provide how many inputs will be given
DUT adds all those input values

Once DUT starts accumulating bytes it ignores changes to the length and 
field or register until it has generated output

The Value of N can be provided either
At the Interface via the length port
Or via the length register accessible via the configuration register.


Which are the control interfaces?

May be make 2 output driver and test both ouputs expected and check with expected..
Callback for assserting ouptut will happen depending upon wheter to chech
cfg_output or data_output

One input interface for d_in and length
and 1 output interface for d_out 
and 1 input output interface with different callback function

# Testplan
set cgf values
await
send len depending upon the cfg values
await 
send data
and monitor the output from d_in callback

now for cfg_output 
whenever i am giving read operation i will then i will monito the output



where will my data go...


