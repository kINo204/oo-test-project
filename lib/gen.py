from lib.config import *
from random import *
# DEBUG
"""
configuration for release: 1, 0, 1
"""
GEN_OPTIONAL_OPT = 1 # whether the generator generates optional operators
SHOW_CALLER = 0
USE_INDENT_BLANK = 0

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
        self.__gen_fundef()
        self.__gen_expr(brac=0,allow_func=1)
        return self.__string


    def __gen_attributes(self):
        self.__string = "" # init __string
        self.__fun_num = randint(0, 3)
        self.__para_num = randint(1, 3)
        self.__fun_name = ["f", "g", "h"]
        shuffle(self.__fun_name)
        self.__para_name = ["x", "y", "z"]
        shuffle(self.__para_name)


    def __gen_fundef(self):
        # def -> fun_name blank ( blank fun_param blank [, blank fun_param blank]{2} ) blank = blank expr

        # Function num
        print(self.__fun_num)
        self.__string += str(self.__fun_num)
        self.__string += "\n"
        # Function all func defs
        for i in range(0,self.__fun_num):
            print(self.__fun_name[i],end="")
            self.__string += self.__fun_name[i]
            self.__gen_blank()
            print("(",end="")
            self.__string += "("
            self.__gen_blank()
            print(self.__para_name[0],end="")
            self.__string += self.__para_name[0]
            self.__gen_blank()
            for i in range(1,self.__para_num):
                print(",",end="")
                self.__string += ","
                self.__gen_blank()
                print(self.__para_name[i],end="")
                self.__string += self.__para_name[i]
                self.__gen_blank()
            print(")",end="")
            self.__string += ")"
            self.__gen_blank()
            print("=",end="")
            self.__string += "="
            self.__gen_blank()
            self.__gen_expr(max_brac-fun_def_brac,allow_func=0) # Reduce max brace num to limit complexity.
            print("")
            self.__string += "\n"
    

    def __gen_expr(self,brac,allow_func):
        # expr -> blank [+-t blank] term blank {+- blank term blank}
        if SHOW_CALLER:
            print("\nexpr: ")

        self.__gen_blank()
        if randint(0,GEN_OPTIONAL_OPT) == 1:
            self.__gen_opt()
            self.__gen_blank()
        self.__gen_term(brac,allow_func)
        self.__gen_blank()
        num_term = randrange(max_term) # num_term + 1 = total num of terms
        for i in range(0,num_term):
            self.__gen_opt()
            self.__gen_blank()
            self.__gen_term(brac,allow_func)
            self.__gen_blank()

        if SHOW_CALLER:
            print("\n:exprE")


    def __gen_func(self,brac):
        # call -> fun_name blank ( blank fact blank [, blank fact blank]{2} )

        # Choose a function available for generation.
        if self.__fun_num == 0:
            return
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
            self.__gen_expr(brac+1,allow_func=1)
        else:
            self.__gen_fact(brac+1,allow_func=1)
        self.__gen_blank()
        for i in range(0,self.__para_num-1):
            print(",",end="")
            self.__string += ","
            self.__gen_blank()
            if use_expr_func:
                self.__gen_expr(brac+1,allow_func=1)
            else:
                self.__gen_fact(brac+1,allow_func=1)
            self.__gen_blank()
        print(")",end="")
        self.__string += ")"
        self.__gen_blank()


    def __gen_term(self,brac,allow_func):
        # term -> [+-f blank] fact {blank * blank fact}
        if SHOW_CALLER:
            print("\nterm: ")

        if randint(0,GEN_OPTIONAL_OPT) == 1:
            self.__gen_opt()
            self.__gen_blank()
        self.__gen_fact(brac,allow_func)
        num_fact = randrange(max_fact)
        for i in range(0,num_fact):
            self.__gen_blank()
            print("*", end="")
            self.__string += "*"
            self.__gen_blank()
            self.__gen_fact(brac,allow_func)

        if SHOW_CALLER:
            print("\n:termE")


    def __gen_fact(self,brac,allow_func):
        """
        fact -> 
            [+-b] int|
            x index|
            (expr) index
            "exp" blank ( blank factor blank ) index
            func_call
        """
        if SHOW_CALLER:
            print("\nfactS: ")

        can_gen_expr = 1 if brac < max_brac else 0


        use_func = allow_func & self.__fun_num != 0
        kind = 0
        if can_gen_expr:
            will_gen_brac = randint(0,1)
            if will_gen_brac:
                kind = randint(1-use_func,4)
            else:
                kind = randint(3,4)
        else:
            kind = randint(3,4)
        
        match kind:
            case 0: # func_call
                self.__gen_func(brac+1)
            case 1: # (expr) [blank ^ blank [+] int]
                print("(", end="")
                self.__string += "("
                self.__gen_expr(brac+1,allow_func)
                print(")", end="")
                self.__string += ")"
                self.__gen_index(
                    max_brac-brac \
                    if max_brac-brac < max_index \
                    else max_index
                    )
            case 2: # "exp" blank ( blank factor blank ) index
                print("exp", end="")
                self.__string += "exp"
                self.__gen_blank()
                print("(", end="")
                self.__string += "("
                self.__gen_blank()
                if use_expr_func:
                    self.__gen_expr(brac+1,allow_func)
                else:
                    self.__gen_fact(brac+1,allow_func)
                self.__gen_blank()
                print(")", end="")
                self.__string += ")"
                self.__gen_index(
                    max_brac-brac \
                    if max_brac-brac < max_index \
                    else max_index
                    )
            case 3: # [+-b] int(int >= 0)
                if randint(0,GEN_OPTIONAL_OPT):
                    self.__gen_opt()
                self.__gen_int()
            case 4: # x [blank ^ blank [+] int]
                print("x", end="") # TODO
                self.__string += "x"
                self.__gen_index(max_index)

        if SHOW_CALLER:
            print("\n:factE")


    def __gen_blank(self):
        # blank -> {blankchar}
        num_blan = randrange(max_blan+1)
        for i in range(0,num_blan):
            kind = randrange(1+USE_INDENT_BLANK)
            match kind:
                case 0:
                    print(" ", end="")
                    self.__string += " "
                case 1:
                    print("\t", end="")
                    self.__string += "\t"


    def __gen_opt(self):
        # opt -> "+"|"-"
        kind = randint(0,1)
        match kind:
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


    def __gen_int(self):
        numlen = randint(1,max_numlen)
        for i in range(0, numlen):
            n = randint(0,9)
            print(n, end="")
            self.__string += str(n)