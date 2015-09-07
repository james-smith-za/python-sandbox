reglist = [elem for elem in dir(fpga.registers) if elem[0] <> '_']
for i in reglist:
    foo = getattr(fpga.registers, i)
    if type(foo) == casperfpga.register.Register:
        print i, foo.read_uint()
