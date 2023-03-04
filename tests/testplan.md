#Coverages

# doubt 
according to the code of the dut... if in between we chagne cfg reg then 
programmed lenght can change in between of the operation 
so i should take it as expected behaviour or modify the code so that it takes busy into acoount

soln - we are expectin the software to check for busy...

## Functional Coverage
port - Register
Register - port
port - port
Register - Register

#
Random input
0 - max input(255 inputs) - with port and Register 
max input - 0 - with port and Register
walking one and walking zero - with port and Register

all combination with random lenghts of the sum...

when the sum overflows
when the sum does not over flows

Known Corner cases:
1. when the sum overflows
2. add only 1 number 
3. put len =0 add nothing

when at certain random time pause is rasied and then resumed with all the above cases....

4*2 means total 8 combinations

code coverage: each and every line of code is covered
FSM coverage : wheter we covered all possible state transitions

for each test case we either write an assertion or we write a coverage bin

# No cross coverage
Code coverage - Measured by simulator
1. Statement/line/block coverage
2. Branch coverage
3. Toggle coverage

Functional coverage - Defined by test env writer
1. Bins
2. Cross coverage -- Not required

# Testplan
1. Design Specification
It uses the RDY EN Protocol on all interfaces
The DUT takes N 8 bit input values. Adds them and outputs the result.
The Value of N can be provided either
At the Interface via the length port
Or via the length register accessible via the configuration register.
The decision on which length is used (port or register) is controlled via a bit in the configuration space.
Once the DUT starts accumulating the bytes it ignores changes to the length field or register until it has generated the output.

2. machine : 1 Lapto
3. Repository : Github
4. Regression : Vscode
5. Software Python >3.11 , iverilog, xcelium/vcs/questaium
6. License : Simulator license
7. BFM : None

The RTL is designed in such a way that it won't work for programmed lenght input 0 or 1.

8. TC1 
Directed test
input from 0 -255 and check additon with all port-register combinations
output Expected output? - 255
sum till 1-22 output expected 253

# delay between data packets


9. C2 Randomised test
input from 0 -255  with random lenght sequence and check additon with all port-register combinations
output Expected -sum of all the inputs

Target:
x% code coverage and Toggle coverage
x% functional coverage
for toggle coverage we will se all the i/o pins are toggling

Bins: input [0:255]
bins: lengtht [0:255]


### States: 
Port -Register
Register - Port
Port - Port
Register - Register
we need to verify all this transitions

### EN-RDY states
Em Rd Des
0  0  Idle
0  1  Ready
1  0  Transaction
Verify all this transition states for the inputdrivers


### Write Read states
Back to back write
gaps between write
pausing in between write and reading 


