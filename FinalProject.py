from tkinter import *
from tkinter import ttk  
from qiskit import QuantumCircuit, execute, Aer
import numpy as np


def is_subsets(list1, list2):
    return set(list1).issubset(set(list2))

def message_to_binary(message):
    binary_message = ""
    for letter in message:
        ascii_value = ord(letter)
        binaryrep = bin(ascii_value)[2:]
        padded_binary = binaryrep.zfill(8)
        binary_message += padded_binary
    return [int(digit) for digit in binary_message]

def binary_to_message(binary_message):
    text_message = ""

    for i in range(0, len(binary_message), 8):
        binary_bits = binary_message[i:i+8]
        binary_str = ''.join(map(str, binary_bits))
        decimal_value = int(binary_str, 2)
        if decimal_value != 0:
            text_message += chr(decimal_value)

    return text_message


def BB84(message, include_eve=False):
    me = message_to_binary(message)
    n = len(me)
    
    qc = QuantumCircuit(n, n)
    fl = np.random.randint(0, 2, n)
    for i in range(n):
        if me[i] == 1:
            qc.x(i)
        elif me[i]==0:
            qc.i(i)
    for i in range(n):        
        if fl[i] == 1:
            qc.h(i)
        elif fl[i]==0:
            qc.x(i)    
    
    if include_eve:
        eavesdrop_outcomes = []
        for i in range(n):
            i = np.random.randint(n)
            random_gate = np.random.choice([qc.h, qc.x])
            random_gate(i)
            eavesdrop_outcomes.append(i)
    
   
    f2 = np.random.randint(0, 2, n)
    for i in range(n):
        if f2[i] == 1:
            qc.h(i)
        elif f2[i]==0:
            qc.x(i)    
    qc.barrier()  
    
    for i in range(n):
        if fl[i] == f2[i]:
            qc.measure(i, i)
    
    backend = Aer.get_backend('qasm_simulator')
    job = execute(qc, backend, shots=1)
    out = job.result().get_counts(qc)
    saa = list(out.keys())[0][::-1]
    lll=[]
    decoded_message = binary_to_message(me)
    for i in range(len(saa)):
        lll.append(saa[i])  # Initialize with a default value
    if set(lll).issubset(set(me)) and include_eve==FALSE:
        decoded_message = binary_to_message(message)
    elif include_eve: decoded_message = "eve is there"    
    print("Original message:", message)
    print("Decoded message:", decoded_message)
    
    if include_eve and len(eavesdrop_outcomes) > 0:
        print("Eavesdropping detected! Eavesdropper measured qubits:", eavesdrop_outcomes)
    elif include_eve:
        print("No eavesdropping detected by Eve.")
    return decoded_message




class EveOptionsWindow:
    def __init__(self, chat_windows):
        self.chat_windows = chat_windows
        self.root = Tk()
        self.root.title("Eve Options")
        self.BG_COLOR = "#000000"
        self.TEXT_COLOR = "#ECF0F1"
        self.CHECK_COLOR = "#3498DB" 
        self.FONT = "Helvetica 14"
        self.FONT_BOLD = "Helvetica 13 bold"
        
        self.create_ui()

    def create_ui(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        window_width = 300
        window_height = 200
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        self.label = Label(self.root, bg=self.BG_COLOR, fg=self.TEXT_COLOR, text="Eve Options", font=self.FONT_BOLD, pady=10)
        self.label.pack()

        self.include_eve_var = IntVar()
        self.include_eve_var.set(0)
        
        style = ttk.Style()
        style.configure("Custom.TCheckbutton", font=self.FONT, background=self.BG_COLOR, foreground=self.TEXT_COLOR, focuscolor=self.BG_COLOR)
        
        self.eve_checkbox = ttk.Checkbutton(self.root, text="Include Eve (Eavesdropper)", style="Custom.TCheckbutton", variable=self.include_eve_var, onvalue=1, offvalue=0)
        self.eve_checkbox.pack()

        self.start_button = Button(self.root, text="Start Chat", font=self.FONT_BOLD, command=self.start_chat)
        self.start_button.pack()

        self.root.configure(bg=self.BG_COLOR)

    def start_chat(self):
        include_eve = self.include_eve_var.get()
        self.root.destroy()
        
        for user_num in range(1, 3):
            chat_windows[user_num] = ChatWindow(user_num, include_eve)
        
        for chat_window in chat_windows.values():
            chat_window.start()

    def run(self):
        self.root.mainloop()




class ChatWindow:
    def __init__(self, user_num, include_eve=False):
        self.user_num = user_num
        self.include_eve = include_eve
        
        self.root = Tk()
        self.root.title(f"Chat - User {user_num}")
        self.BG_COLOR = "#000000"
        self.TEXT_COLOR = "#ECF0F1"
        self.ENTRY_BG_COLOR = "#212121"
        self.BUTTON_BG_COLOR = "#3498DB"
        self.FONT = "Helvetica 14"
        self.FONT_BOLD = "Helvetica 13 bold"
        
        self.create_ui()

    def create_ui(self):
        self.label = Label(self.root, bg=self.BG_COLOR, fg=self.TEXT_COLOR, text="Chat", font=self.FONT_BOLD, pady=10, width=20, height=1)
        self.label.grid(row=0, column=0, columnspan=3)

        self.chat_text = Text(self.root, bg=self.BG_COLOR, fg=self.TEXT_COLOR, font=self.FONT, width=60, state=DISABLED)
        self.chat_text.grid(row=1, column=0, columnspan=3)

        self.scrollbar = Scrollbar(self.chat_text)
        self.scrollbar.place(relheight=1, relx=0.974)

        self.entry = Entry(self.root, bg=self.ENTRY_BG_COLOR, fg=self.TEXT_COLOR, font=self.FONT, width=60)
        self.entry.grid(row=2, column=0, columnspan=2)

        self.send_button = Button(self.root, text="Send", font=self.FONT_BOLD, bg=self.BUTTON_BG_COLOR, command=self.send)
        self.send_button.grid(row=2, column=2)

     

        if self.include_eve:
            self.eve_status_label = Label(self.root, bg=self.BG_COLOR, fg=self.TEXT_COLOR, text="Eve: Enabled", font=self.FONT, pady=10)
        else:
            self.eve_status_label = Label(self.root, bg=self.BG_COLOR, fg=self.TEXT_COLOR, text="Eve: Disabled", font=self.FONT, pady=10)
        self.eve_status_label.grid(row=3, column=0, columnspan=2)

        self.root.configure(bg=self.BG_COLOR)

    def send(self):
        message = self.entry.get()

        if message:
            bb84_encoded_message = BB84(message, include_eve=self.include_eve)
            display_text = f"User {self.user_num} -> {message}"

            self.chat_text.config(state=NORMAL)
            self.chat_text.insert(END, "\n" + display_text)
            self.chat_text.config(state=DISABLED)
            self.entry.delete(0, END)

            # Store the encoded message
            self.encoded_message = bb84_encoded_message

            other_user_num = 3 - self.user_num
            other_chat_window = chat_windows[other_user_num]
            other_chat_window.receive_message(bb84_encoded_message, is_encoded=True)

    def receive_message(self, message, is_encoded=False):
        if is_encoded:
            decrypted_message = BB84(message, include_eve=self.include_eve)  # Use the received encoded message
            display_text = f"User {self.user_num} (Received Decrypted) -> {decrypted_message}"
        else:
            display_text = f"User {self.user_num} (Received) -> {message}"

        self.chat_text.config(state=NORMAL)
        self.chat_text.insert(END, "\n" + display_text)
        self.chat_text.config(state=DISABLED)





    def start(self):
        self.root.mainloop()


chat_windows = {}

eve_options_window = EveOptionsWindow(chat_windows)
eve_options_window.run()