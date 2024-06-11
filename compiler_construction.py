class Parse_tree(object):
    def __init__(self,grammar,terminals):
        self.grammar=grammar
        self.terminals=terminals
        self.non_terminals=self.grammar.keys()
        self.first={}
        self.follow={}
        self.parse_table={}
        self.parser=[]
    def computing_first_set(self):
        for non_terminal in self.grammar:
            self.first.update({non_terminal:set()})
        epsilon="null"

        def first_of(symbol):
            if symbol in self.terminals:
                return {symbol}
            if symbol is epsilon:
                return {epsilon}
            else:
                result=set()
                for productions in self.grammar[symbol]:
                    if productions==epsilon:
                        result.add(epsilon)
                    else:
                        for production in productions.split():
                            first_pro=first_of(production)
                            result.update(first_pro-{epsilon})
                            if epsilon not in first_pro:
                                break
                        else:
                            result.add(epsilon)
            return result
        for i in self.non_terminals:
            self.first[i]= first_of(i)
        
    def computing_follow_set(self):
        for non_terminal in self.grammar:
            self.follow.update({non_terminal:set()})
        self.follow["<Start>"].add("$")

        while True:
            updated=False
            for head,productions in self.grammar.items():
                for production in productions:
                    part=production.split()
                    for i in range(0,len(part)):
                        if part[i] in self.non_terminals:
                            follow_before=self.follow[part[i]].copy()
                            if i+1< len(part):
                                next_part=part[i+1]
                                if next_part in self.terminals:
                                    self.follow[part[i]].add(next_part)
                                else:
                                    self.follow[part[i]].update(self.first[next_part]-{"null"})
                                    if "null" in self.first[next_part]:
                                        self.follow[part[i]].update(self.follow[head])
                            else:
                                self.follow[part[i]].update(self.follow[head])

                            if follow_before != self.follow[part[i]]:
                                updated=True
            if not updated:
                break

        return self.follow
    
    def ll1_table(self):
        for non_terminals in self.grammar:
            self.parse_table[non_terminals]={}
            for terminals in self.terminals +["$"]:
                self.parse_table[non_terminals][terminals]=None
        
        epsilon="null"

        for non_terminals in self.grammar:
            for production in self.grammar[non_terminals]:
                first_production=self.first_of_string(production.split())
                for terminals in first_production:
                    if terminals!=epsilon:
                        self.parse_table[non_terminals][terminals]=production
                    if production==epsilon or epsilon in first_production:
                        for terminals in self.follow[non_terminals]:
                            self.parse_table[non_terminals][terminals]=production

    def first_of_string(self,symbols):
        result=set()
        for symbol in symbols:
            if symbol=="null":
                result.add("null")
                continue
            if symbol in self.terminals:
                result.add(symbol)
                break
            result.update(self.first[symbol]-{'null'})
            if "null" not in self.first[symbol]:
                break
        else:
            result.add("null")
        return result


    def parse_tree(self,input_code,start_symbol):
        stack=[start_symbol]
        input_tokens=input_code.split()+["$"]
        index=0

        while stack:
            top=stack.pop()
            if top in self.terminals or top=="$":
                if top==input_tokens[index]:
                    index+=1
                else:
                    raise ValueError("Parsing Error:Unexpected tokens")
            elif top in self.non_terminals:
                production=self.parse_table[top].get(input_tokens[index],None)
                if not production:
                    raise ValueError(f"Parsing Error: no rule for {top} on {input_tokens[index]}")
                self.parser.append((top,production))
                production_symbols=production.split()
                for symbol in reversed(production_symbols):
                    if symbol!="null":
                        stack.append(symbol)
        if index==len(input_tokens)-1:
            return self.parser
        else:
            raise("Parsing Error: Incomplete Parser")
            
grammar={
    "<Start>": ["<init>","<for>","<print>"],
    "<init>": ["DT ID <init'>"],
    "<init'>": ["comma ID <init'>", "EQ <value>", "null"],
    "<value>": ["string <value'>", "INT <value'>", "U2705 <value'>", "U274E <value'>"],
    "<value'>": ["comma <value>", "<Start>", "null"],
    "<for>": ["U27B0 ORB <init> comma <condition> comma <count> CRB OCB <Start> CCB"],
    "<condition>": ["ID <operators> <condition'>"],
    "<condition'>": ["ID", "INT", "string"],
    "<operators>": ["LT", "GT", "LTE", "GTE", "EQT", "NEQ"],
    "<count>": ["ID <count'>"],
    "<count'>": ["INC", "DEC"],
    "<print>": ["U1F548 ORB <print'> CRB <Start>"],
    "<print'>": ["ID <exit>", "INT <exit>", "string <exit>"],
    "<exit>": ["comma <print>", "null"]
}

terminals=["DT","ID","comma","EQ","string","INT","U2705","U274E","U27B0","ORB","CRB","OCB","CCB","LT","GT","LTE","GTE","EQT","NEQ","INC","DEC","U1F548"]

Tree=Parse_tree(grammar,terminals)
Tree.computing_first_set()
print("First Sets Are: ")
for i,j in Tree.first.items():
    print(i,"=",j)

Tree.computing_follow_set()
print("\n\n Follow Sets Are: ")
for i,j in Tree.follow.items():
    print(i,"=",j)
    
#print("LL(1) Table")
Tree.ll1_table()
#print(Tree.parse_table)
#for i,j in Tree.parse_table.items():
#    print(i)
#    for r,s in j.items():
#        print(r,":",s)
input_code = '''DT ID EQ INT 
                  DT ID EQ INT
                  U27B0  ORB  DT ID EQ INT comma ID LTE INT comma ID INC CRB OCB
                  DT ID EQ INT
                  CCB 
                 '''
Tree.parse_tree(input_code,"<Start>")
print("\n\nParse Tree:")
for nt, production in Tree.parser:
    print(f"{nt} -> {production}")