import sys
p = sys.argv[1]
b = open(p,'rb').read(64)
print(repr(b[:64]))
print(list(b[:16]))
