import Tkinter as tk
import sys
import string
import Queue

class MyDialog:
    def __init__(self, parent):

        top = self.top = parent

        self.entry_frame = tk.Frame(parent)
        tk.Label(self.entry_frame, text="Please enter English sentence:").pack()
        tk.Label(top, text="Example: move disk1 from pole1 to pole2").pack()
        tk.Label(top, text="Example: pick up disk1 from pole1").pack()
        tk.Label(top, text="Example: put down disk1 on pole2").pack()

        self.e = tk.Entry(self.entry_frame, width=100)
        self.e.pack(padx=15)

        self.entry_frame.pack(side=tk.TOP, fill=tk.BOTH)
        
        self.log_frame = tk.Frame(parent)
        self.text = tk.Text(self.log_frame)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scroll = tk.Scrollbar(self.log_frame)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.text.config(font="Courier 12", yscrollcommand=self.scroll.set)
        self.scroll.config(command=self.text.yview)

        self.log_frame.pack(side=tk.BOTTOM)
        
        self.fBottom = tk.Frame(top)

        c = tk.Button(self.fBottom, text="Close", command=self.close)
        c.pack(side = tk.RIGHT)

        b = tk.Button(self.fBottom, text="Execute", command=self.ok)
        b.pack(side = tk.RIGHT)
        self.value = ""

        c = tk.Button(self.fBottom, text="Parse", command=self.parse)
        c.pack(side = tk.RIGHT)

        self.fBottom.pack(side=tk.BOTTOM)

        #setup other stuff
        self.log_frame.bind('<<display-text>>', self.display_text_handler)
        
        self.message = Queue.Queue()

        self.parsed_plan = ""

        #Used to store which disk 'it' is, probably used durring uses of AND...
        self.it = ""

    def parse(self):
        if self.parsed_plan == "":
            self.value = self.e.get()
            #parse the plan
            self.parsed_plan = self.semantic_parser(self.value)
            self.log_info("{0} -> {1}".format(self.value, self.parsed_plan))
        else:
            self.log_error("Already parsed plan: {0}, cannot parse new plan.".format(self.parsed_plan))
        
    def semantic_parser(self, plan):
            #move disk1 from pole1 to pole2 and move disk2 from pole1 to pole3
            #Write code for simple semantic grammar here
            #Actions should be returned in the following format:
            #1. Mov Object Source Destination
            #2. Pick Object Source
            #3. Put Object Destination
        #But first, if for some reason the plan string is empty just exit
        if (len(plan) == 0):
            return plan

        #init case 2 boolean
        #this boolean is used to tell if we should do (VP1 NP1 NP4 NP3)
        self.case2 = False

        # split plan into words
        plan = string.lower(plan)
        words = string.split(plan) # A list of the words in the user command
        result = plan # In case we cannot parse the plan propperly, return it unmodified

        #check for and in words
        try:
            and_index = words.index("and") #and location
        except ValueError:
            and_index = -1

        # parse
        if and_index >= 0:
            #parse commpount
            first_command = words[:and_index]
            second_command = words[and_index + 1:]
            result = []
            
            temp_command1 = self.get_verb_phrase(first_command) + self.get_noun_phrases(first_command)
            temp_command1 = self.reorder_cmd_for_case_2(temp_command1)
            result.append(temp_command1)

            ###########################################################################################

            temp_command2 = self.get_verb_phrase(second_command) + self.get_noun_phrases(second_command)
            temp_command2 = self.reorder_cmd_for_case_2(temp_command2)
            result.append(temp_command2)

            # check for error in parsing
            self.result_mul_error_check(result)
        else:
            #parse sigular
            temp_command = self.get_verb_phrase(words) + self.get_noun_phrases(words)
            temp_command = self.reorder_cmd_for_case_2(temp_command)

            # check for error in parsing
            self.result_error_check(temp_command)
            result = temp_command

        return result

    def get_verb_phrase(self, words):
        #The verb phrase should come first, so look at the first word
        #If the verb phase is present go ahead and parse the noun phrase
        self.log_info("Expanding sentence 'S' to VP1 NP1 NP3 NP4 | VP2 NP1 NP3 | VP3 NP1 NP4,")
        self.log_info("the identifying initial verb phrase...")
        if words[0] == "mov" or words[0] == "move":
            self.log_info("Case VP1 NP1 NP3 NP4 (\"Move\") found")
            self.log_info("Identifying noun phrases...")
            result = "Mov "
            self.case2 = self.case_2_check(words)
        elif words[0] == "pick":
            self.log_info("Case VP2 NP1 NP3 (\"Move\") found.")
            self.log_info("Identifying noun phrases...")            
            result = "Pick "
        elif words[0] == "put":
            self.log_info("Case VP3 NP1 NP4 (\"Move\") found.")
            self.log_info("Identifying noun phrases...")            
            result = "Put "
        else:
            self.log_error(words, "Instructions must begin with Move, Pick or Put.")
            return ""
        return result

    def case_2_check(self, words):

        # if two comes before from then we should do VP1 NP1 NP4 NP3
        for word in words:
            if word == "to":
                return True
            if word == "from":
                return False

    def reorder_cmd_for_case_2(self, cmd):

        # VP1 NP1 NP3 NP4
        if not self.case2:
            return cmd

        # VP1 NP1 NP4 NP3
        words = string.split(cmd)
        try:
            new_cmd = str(words[0] + " " + words[1] + " " + words[3] + " " + words[2])
        except IndexError:
            self.log_error("Failed to reorder command!")
            return cmd

        return new_cmd

    def get_noun_phrases(self, words):
        """
        Helper method. Given a string representing a plan,
        finds the noun phrases by removing every word other than "disk*" or "pole*.
		Does not check whether these are in the correct order."
        """
        result = ""

        #assume that the noun phrases are in a fixed order
        #then just look for the keywords "disk" and "pole", ignoring everything elsee
        index = 0
        for w in words:
            if "disk" in w or "pole" in w:

                #store our disk in 'it' to later refer to it if 'it' is used
                if "disk" in w:
                    self.it = w

                # handling adj case
                if "pole" in w:
                    prev_word = words[index - 1]
                    if prev_word == "left":
                        w = "pole1"
                    elif prev_word == "middle":
                        w = "pole2"
                    elif prev_word == "right":
                        w = "pole3"

                self.log_info("\"{0}\" found!".format(w))
                result += w.title() + " "

            # handling 'it' case
            if w == "it":
                w = self.it
                result += w.title() + " "
            index += 1
                
        return result

    def result_mul_error_check(self, result):
        for res in result:

            # check validity
            is_valid = self.result_validate(res)

            # handle validity
            if is_valid:
                return
            else:
                self.log_error ("Failed to parse command!")

    def result_error_check(self, result):

        # check validity
        is_valid = self.result_validate(result)

        # handle validity
        if is_valid:
            return
        else:
            self.log_error ("Failed to parse command! Please check grammar!")

    def result_validate(self, result):
        words = string.split(str(result))
        if words[0] == "Mov":
            try:
                is_valid = ("Disk" in words[1]) and ("Pole" in words[2]) and ("Pole" in words[3])
            except IndexError:
                is_valid = False
        elif words[0] == "Pick":
            try:
                is_valid = ("Disk" in words[1]) and ("Pole" in words[2])
            except IndexError:
                is_valid = False
        elif words[0] == "Put":
            try:
                is_valid = ("Disk" in words[1]) and ("Pole" in words[2])
            except IndexError:
                is_valid = False
        else:
            is_valid = False

        return is_valid

    def ok(self):
        if self.parsed_plan == "":
            self.parse()

        if (type(self.parsed_plan) == list):
    	    for command_string in self.parsed_plan:
    	        print command_string
    	else:
    	    print self.parsed_plan
    	self.top.destroy()

    def close(self):
    	self.value = "close"
    	print self.value
    	self.top.destroy()
        
    def log_info(self, printable_object, message=""):
        s = "[INFO]{0}:{1}".format(printable_object, message)
        self.message.put(s)
        self.log_frame.event_generate('<<display-text>>')    
    
    def log_error(self, printable_object, message=""):
        s =  "[ERROR]{0}:{1}".format(printable_object, message)
        self.message.put(s)
        self.log_frame.event_generate('<<display-text>>')        

    def display_text_handler(self, event=None):
        s = self.message.get()
        self.text.insert(tk.END, s)
        self.text.insert(tk.END, '\n')
        self.text.yview(tk.END)

def main():
    root = tk.Tk()
    root.title('Enter Command')
    d = MyDialog(root)
    root.wait_window(d.top)
   
if __name__ == "__main__":
        main()
