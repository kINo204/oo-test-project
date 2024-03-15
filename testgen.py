# Author: kINo, Mio
# Created on 2024/3/2

import os
from re import *

from lib.gen import Generator
from sympy import *
from sympy.abc import *

generator = Generator()

while true:
    # Generate a test case.
    generated = ""
    print("gen: ")
    generated = generator.generate()
    print("")
    generated += "\n"
    # generated = "1\nf(x)...\nexpression\n"

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
        defs[i] = sub(r"dx", "diff", defs[i])
        defs[i] = sub("=", " :return ", defs[i])
        defs[i] = "def " + defs[i];
        exec(defs[i])

    # Sub expression for sympy to use. 
    subed = ""
    subed = sub(r"(?<=[,=+\-*(^])\s*0+\s*(?=\d)|^\s*0+\s*(?=\d)", "", expression)
    subed = sub(r"\^\s*\+", "**", subed)
    subed = sub(r"\^", "**", subed)
    subed = sub(r"dx", "diff", subed)
    print("subed: "+subed)

    # Sympy calculates the answer.
    exec("val=expand(" + subed+")")
    ans = val.simplify().expand()
    print("ans: "+str(ans))

    # Sympy transfer the jar output for comparison.
    jar_trans = expand(jar_out)
    print("jar_trans: "+str(jar_trans))
    print("")

    # Compare and write the error log.
    if ans != jar_trans:
        errlog = open("errs.log", 'a')
        errlog.write("case: \n"+generated+"expect: \n"+str(ans)+"\njar_exp: \n"+str(jar_trans)+"\njar_out: \n"+jar_out+"\nexpect_out: \n"+str(ans).replace("**","^")+"\n\n")
        errlog.close()