from lib.config import *
from random import *
from enum import Enum
# DEBUG
"""
configuration for release: 1, 0, 1
"""
GEN_OPTIONAL_OPT = 1 # whether the generator generates optional operators
SHOW_CALLER = 0
USE_INDENT_BLANK = 1

"""
Grammar:
func_def -> fun_name blank ( blank fun_param blank [, blank fun_param blank]{2} ) blank = blank expr
func_call -> fun_name blank ( blank fact blank [, blank fact blank]{2} )
fun_name -> f|g|h
fun_param -> x|y|z

expr -> blank [+-t blank] term blank {+- blank term blank}
term -> [+-f blank] fact {blank * blank fact}
fact -> 
    [+-b] int|
    x index|
    (expr) index
    "exp" blank ( blank factor blank ) index
    func_call
    dx blank ( blank expr blank )

index -> [blank ^ blank [+] int]  (not same as required)
"""

class Generator:
    __string=""
    __fun_num=0
    __fun_name=[]
    __para_num=0
    __para_name=[]

    def __init__(self):  
        self.__gen_attributes()

    def generate(self):
        self.__gen_attributes()
        self.__gen_fundef(
            max_brac-fun_def_brac,  # Reduce max brace num inside functions to limit complexity.
            max_diff,               # Diff in function def disabled.
            gen_func_in_def
        )
        self.__gen_expr(brac=0,diff=0,allow_func=1,banned_func="")
        return self.__string


    def __gen_attributes(self):
        self.__string = "" # init __string
        self.__fun_num = (0 if gen_func==0 else randint(0, 3))
        self.__para_num = randint(1, 3)
        self.__fun_name = ["f", "g", "h"]
        shuffle(self.__fun_name)
        self.__para_name = ["x", "y", "z"]
        shuffle(self.__para_name)


    def __gen_expr(self,brac,diff,allow_func,banned_func):
        # expr -> blank [+-t blank] term blank {+- blank term blank}
        if SHOW_CALLER:
            print("\nexpr: ")

        self.__gen_blank()
        if randint(0,GEN_OPTIONAL_OPT) == 1:
            self.__gen_opt()
            self.__gen_blank()
        self.__gen_term(brac,diff,allow_func,banned_func)
        self.__gen_blank()
        num_term = randrange(max_term) # num_term + 1 = total num of terms
        for i in range(0,num_term):
            self.__gen_opt()
            self.__gen_blank()
            self.__gen_term(brac,diff,allow_func,banned_func)
            self.__gen_blank()

        if SHOW_CALLER:
            print("\n:exprE")


    def __gen_term(self,brac,diff,allow_func,banned_func):
        # term -> [+-f blank] fact {blank * blank fact}
        if SHOW_CALLER:
            print("\nterm: ")

        if randint(0,GEN_OPTIONAL_OPT) == 1:
            self.__gen_opt()
            self.__gen_blank()
        self.__gen_fact(brac,diff,allow_func,banned_func)
        num_fact = randrange(max_fact)
        for i in range(0,num_fact):
            self.__gen_blank()
            print("*", end="")
            self.__string += "*"
            self.__gen_blank()
            self.__gen_fact(brac,diff,allow_func,banned_func)

        if SHOW_CALLER:
            print("\n:termE")


    def __gen_fact(self,brac,diff,allow_func,banned_func):
        """
        fact -> 
            [+-b] int|
            x index|
            (expr) index
            "exp" blank ( blank factor blank ) index
            func_call
            dx blank ( blank expr blank )
        """
        if SHOW_CALLER:
            print("\nfactS: ")

        # Factor type generation controls
        FT = Enum("FT", ("NUM","VAR","EXPR","EXP","FUNC","DIFF"))
        factor_type_list = list(range(1,len(FT)+1))

        can_gen_brac = 1 if brac < max_brac else 0
        can_gen_diff = 1 if (gen_diff == 1 and diff < max_diff) else 0
        can_gen_func = 1 if (allow_func and self.__fun_num != 0 and ((self.__fun_num > 1) or (banned_func == ""))) else 0

        if (can_gen_brac == 0):
            factor_type_list.remove(FT.EXPR.value)
            factor_type_list.remove(FT.EXP.value)
            factor_type_list.remove(FT.FUNC.value)
            factor_type_list.remove(FT.DIFF.value)
        if (can_gen_diff == 0):
            if (FT.DIFF.value in factor_type_list):
                factor_type_list.remove(FT.DIFF.value)
        if (can_gen_func == 0):
            if (FT.FUNC.value in factor_type_list):
                factor_type_list.remove(FT.FUNC.value)

        factor_type = choice(factor_type_list)
        
        # Generate factor based on type
        match factor_type:
            case FT.NUM.value: # [+-b] int(int >= 0)
                if randint(0,GEN_OPTIONAL_OPT):
                    self.__gen_opt()
                self.__gen_num()
            case FT.VAR.value: # x [blank ^ blank [+] int]
                print("x", end="") # TODO
                self.__string += "x"
                self.__gen_index(max_index)
            case FT.EXPR.value: # (expr) [blank ^ blank [+] int]
                print("(", end="")
                self.__string += "("
                self.__gen_expr(brac+1,diff,allow_func,banned_func)
                print(")", end="")
                self.__string += ")"
                self.__gen_index(
                    max_brac-brac \
                    if max_brac-brac < max_index \
                    else max_index
                    )
            case FT.EXP.value: # "exp" blank ( blank factor blank ) index
                print("exp", end="")
                self.__string += "exp"
                self.__gen_blank()
                print("(", end="")
                self.__string += "("
                self.__gen_blank()
                if use_expr_func:
                    self.__gen_expr(brac+1,diff,allow_func,banned_func)
                else:
                    self.__gen_fact(brac+1,diff,allow_func,banned_func)
                self.__gen_blank()
                print(")", end="")
                self.__string += ")"
                self.__gen_index(
                    max_brac-brac \
                    if max_brac-brac < max_index \
                    else max_index
                )
            case FT.FUNC.value: # func_call
                self.__gen_func(brac,diff,1,banned_func) # `allow_func` configurable, but not yet.
            case FT.DIFF.value: # diff
                self.__gen_diff(brac,diff,1,banned_func) # `allow_func` configurable, but not yet.

        if SHOW_CALLER:
            print("\n:factE")


    def __gen_fundef(self,brac,diff,allow_func):
        # def -> fun_name blank ( blank fun_param blank [, blank fun_param blank]{2} ) blank = blank expr
        # Function num
        print(self.__fun_num)
        self.__string += str(self.__fun_num)
        self.__string += "\n"
        # Function all func defs
        for i in range(0,self.__fun_num):
            # Function Name
            print(self.__fun_name[i],end="")
            self.__string += self.__fun_name[i]
            self.__gen_blank()
            # Function params
            print("(",end="")
            self.__string += "("
            self.__gen_blank()
            print(self.__para_name[0],end="")
            self.__string += self.__para_name[0]
            self.__gen_blank()
            for j in range(1,self.__para_num):
                print(",",end="")
                self.__string += ","
                self.__gen_blank()
                print(self.__para_name[j],end="")
                self.__string += self.__para_name[j]
                self.__gen_blank()
            print(")",end="")
            self.__string += ")"
            self.__gen_blank()
            # Function body
            print("=",end="")
            self.__string += "="
            self.__gen_blank()
            self.__gen_expr(brac,diff,allow_func,self.__fun_name[i]) # Banned function def from recursing itself.
            print("")
            self.__string += "\n"
    

    def __gen_func(self,brac,diff,allow_func,banned_func):
        # call -> fun_name blank ( blank fact blank [, blank fact blank]{2} )

        # Choose a function available for generation.
        if self.__fun_num == 0:
            return
        func_ind=0
        fun_name=""
        if banned_func != "":
            while True:
                func_ind = randint(0,self.__fun_num-1)
                fun_name = self.__fun_name[func_ind]
                if fun_name != banned_func:
                    # print("\n"+fun_name+"!="+banned_func)
                    break;
        else:
            func_ind = randint(0,self.__fun_num-1)
            fun_name = self.__fun_name[func_ind]

        print(fun_name,end="")
        self.__string += fun_name
        self.__gen_blank()
        print("(",end="")
        self.__string += "("
        # The function"s generating behavior
        # is configurable between expr / fact.
        if use_expr_func:
            self.__gen_expr(brac+1,diff,allow_func,banned_func)
        else:
            self.__gen_fact(brac+1,diff,allow_func,banned_func)
        self.__gen_blank()
        for i in range(0,self.__para_num-1):
            print(",",end="")
            self.__string += ","
            self.__gen_blank()
            if use_expr_func:
                self.__gen_expr(brac+1,diff,allow_func,banned_func)
            else:
                self.__gen_fact(brac+1,diff,allow_func,banned_func)
            self.__gen_blank()
        print(")",end="")
        self.__string += ")"
        self.__gen_blank()


    def __gen_diff(self,brac,diff,allow_func,banned_func):
        # dx blank ( blank expr blank )
        print("dx",end="")
        self.__string += "dx"
        self.__gen_blank()
        print("(",end="")
        self.__string += "("
        self.__gen_blank()
        self.__gen_expr(brac+1,diff+1,allow_func,banned_func)
        self.__gen_blank()
        print(")",end="")
        self.__string += ")"


    def __gen_blank(self):
        # blank -> {blankchar}
        num_blan = randrange(max_blan+1)
        for i in range(0,num_blan):
            factor_type = randrange(1+USE_INDENT_BLANK)
            match factor_type:
                case 0:
                    print(" ", end="")
                    self.__string += " "
                case 1:
                    print("\t", end="")
                    self.__string += "\t"


    def __gen_opt(self):
        # opt -> "+"|"-"
        factor_type = randint(0,1)
        match factor_type:
            case 0:
                print("-", end="")
                self.__string += "-"
            case 1:
                print("+", end="")
                self.__string += "+"


    def __gen_index(self,mindex):
        # [blank ^ blank [+] int]
        if randint(0,1) == 1:
            self.__gen_blank()
            print("^", end="")
            self.__string += "^"
            self.__gen_blank()
            if randint(0,GEN_OPTIONAL_OPT) == 1:
                print("+", end="")
                self.__string += "+"

            assert mindex >= 0
            index = randint(0,mindex)
            print(index, end="")
            self.__string += str(index)


    def __gen_num(self):
        numlen = randint(1,max_numlen)
        for i in range(0, numlen):
            n = randint(0,9)
            print(n, end="")
            self.__string += str(n)