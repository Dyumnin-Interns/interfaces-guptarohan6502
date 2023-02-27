import constraint
import random

class PacketGenerator:

	def __init__(self):
		self.p = constraint.Problem()
		self.p.addVariable("hdrlen", [14,16])
		self.p.addVariable("payload", range(50, 1500))
		self.p.addVariable("length", range(64, 1500))
		self.p.addVariable("type", range(0x800, 0xffff))
		self.p.addVariable("hasVlan", [True, False])


		self.p.addConstraint(lambda len,hdr,pld: len==hdr+pld, ("length", "hdrlen", "payload"))

		self.p.addConstraint(lambda vlan,hdrlen: hdrlen==16 if vlan else hdrlen==14, ["hasVlan", "hdrlen"])
		self.p.addConstraint(lambda ethtype: ethtype <= 0x810 , ["type"])
		self.p.addConstraint(lambda len, type: len == 64 if type == 0x806 else len >= 64, ["length", "type"])

	
	def solve(self):
		self.solutions = self.p.getSolutions()

	def get(self):
		return random.choice(self.solutions)

	# def addConstraint(self, constraint, variables):
	# 	self.p.addConstraint(constraint, variables)

if __name__ == "__main__":
	pg = PacketGenerator()
	pg.p.addConstraint(lambda type: type == 0x806, ["type"])
	pg.solve()
	for i in range(5):
		print(pg.get())

		 



		
