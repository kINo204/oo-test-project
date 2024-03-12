import os
from re import *

from lib.gen import Generator
from sympy import *
from sympy.abc import *

generated = input()
funnum = int(generated)
for i in range(0,funnum+1):
	generated += "\n"
	generated += input()

generated += "\n"

print("finish")
# Run case in jar and get jar_out.
fin = open("in.txt", "w")
fin.write(generated)
fin.close()
execute = "java < in.txt > out.txt -jar test.jar"
os.system(execute)
fout = open("out.txt", "r")
jar_out = fout.readline();
print("jar_out: "+jar_out,end="")
fout.close()

# Split generated into num, defs and expression.
num = 0
defs = []
expression = ""
num = int(generated.split("\n")[0])
for i in range(1,num+1):
    defs.append(generated.split("\n")[i])
expression = generated.split("\n")[num+1]

# Format function defs and define them.
for i in range(0,num):
    defs[i] = sub(r"(?<=[,=+\-*(^])\s*0+\s*(?=\d)|^\s*0+\s*(?=\d)", "", defs[i])
    defs[i] = sub(r"\^\s*\+", "**", defs[i])
    defs[i] = sub(r"\^", "**", defs[i])
    defs[i] = sub("=", " :return ", defs[i])
    defs[i] = "def " + defs[i];
    exec(defs[i])

# Sub expression for sympy to use. 
subed = ""
subed = sub(r"(?<=[,=+\-*(^])\s*0+\s*(?=\d)|^\s*0+\s*(?=\d)", "", expression)
subed = sub(r"\^\s*\+", "**", subed)
subed = sub(r"\^", "**", subed)
print("subed: "+subed)

# Sympy calculates the answer.
exec("val=expand(" + subed+")")
ans = val.simplify().expand()
print("ans: "+str(ans))

# Sympy transfer the jar output for comparison.
jar_trans = expand(jar_out)
print("jar_trans: "+str(jar_trans))
print("")

if ans != jar_trans:
	print("Wrong Answer.")
else:
	print("Correct.")