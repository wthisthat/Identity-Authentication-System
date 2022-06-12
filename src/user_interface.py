from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Combobox, Treeview
from PIL import Image, ImageTk
from datetime import datetime
import cv2
import pickle

class GUI:

    # initialization
    def __init__(self,face_detector,face_recognition,db):
        self.window = Tk()
        self.window.maxsize()
        self.window.state("zoomed")
        self.window.title("Face-Recognition-Capable Surveillance System")
        self.window.bind("<Escape>", lambda e: self.window.quit())

        # face detector and recognition instantiation
        self.face_detector = face_detector
        self.face_recognition = face_recognition
        # db instantiation for query functions
        self.db = db

    def dashboard(self):
        # create a label to display the live video stream
        disp = Label(self.window)
        disp.grid(row=0,columnspan=2)

        # create a labelframe to display the recognition results
        self.lblFrame = LabelFrame(self.window,text="Authentication Results")
        self.lblFrame.grid(row=0,rowspan=2,column=2,sticky="NESW",ipadx=25,padx=5)

        # initialize canvas in the labelframe and fix width
        canvas = Canvas(self.lblFrame,width=190)

        # create frame in canvas
        self.frame = Frame(canvas)

        # create scrollbar for scrolling purpose
        # scrollbar = Scrollbar(canvas, orient="vertical", command = canvas.yview)
        # canvas.configure(yscrollcommand=scrollbar.set)
        # scrollbar.pack(side=RIGHT, fill="y")
        canvas.pack(side=LEFT, fill="both", expand=True)
        
        # fix canvas size to avoid sizing issue
        canvas.pack_propagate(0)
        canvas.create_window((0,0), window=self.frame, anchor="nw")
        self.frame.bind("<Configure>", lambda e: canvas.configure(scrollregion = canvas.bbox("all")))

        self.result_limit = []
        self.widgets = {}
        for r in range(1,9):
            lbl_result = Label(self.frame, image=None, text='', compound=LEFT)
            lbl_result.grid(row=r,column=0)
            self.widgets[(r,0)] = lbl_result
        self.default_color = lbl_result.cget("background")

        btn_register = Button(self.window,text="Manage Identity Database", command=self.identity_database_window)
        btn_register.grid(row=1,column=0,pady=15)

        btn_view = Button(self.window,text="View Authentication Records", command=self.view_authentication_window)
        btn_view.grid(row=1,column=1,pady=15)

        return disp

    def view_authentication_window(self):
        # define new window attributes
        self.rec_window = Toplevel(self.window)
        self.rec_window.geometry("800x400+350+150")
        self.rec_window.title("View Authentication Records")
        self.rec_window.resizable(False,False)
        self.rec_window.grab_set()

        # define table columns
        cols = ("ID", "Timestamp", "Recognized (Y/N)", "Distance", "Identity ID","Name")
        table = Treeview(self.rec_window, columns=cols, show="headings")

        # define headings & set columns width
        for col in cols:
            table.heading(col,text=col)
            if col == "ID":
                table.column(col, anchor="center", width=80, stretch = "no")
            elif col == "Name":
                table.column(col, width=230, stretch= "no")
            else:
                table.column(col, width=120, stretch= "no")
        
        # load data from database
        data_list = self.db.load_record()
        for i in data_list:
            if i[2]:
                recognized = "Y"
            else:
                recognized = "N"
            table.insert("", END, values=(i[0],i[1],recognized,i[3],i[4],i[5]))

        # table in whole window
        table.pack(fill="both",expand=True)
        # declare scrollbar to the table
        scrollbar = Scrollbar(table, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill="y")
        
        btn_clear = Button(self.rec_window, text="Clear Record", command=self.clear_record)
        btn_clear.pack(pady=3)

    def identity_database_window(self):
        # define new window attributes
        self.idb_window = Toplevel(self.window)
        self.idb_window.geometry("700x400+400+150")
        self.idb_window.title("Manage Identity Database")
        self.idb_window.resizable(False,False)
        self.idb_window.grab_set() # disable interact with main window

        # define table columns
        cols = ("ID", "Name", "Gender", "Remarks")
        table = Treeview(self.idb_window, columns=cols, show="headings")

        # define headings & set columns width
        for col in cols:
            table.heading(col,text=col)
            if col == "ID":
                table.column(col, anchor="center", width=60, stretch = "no")
            else:
                table.column(col, width=210, stretch= "no")

        # load data from database
        data_list = self.db.load_identity()
        for i in data_list:
            table.insert("", END, values=(i[0],i[1],i[2],i[4])) # ignore encoding
        
        # place ui components
        table.pack(fill="both",expand=True)

        scrollbar = Scrollbar(table, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT,fill="y")

        btn_register = Button(self.idb_window, text="Register", width=12, command=self.register_identity_window)
        btn_register.pack(side=LEFT, padx=(160,80), pady=5)

        btn_search = Button(self.idb_window, text="Search/Modify", width=12, command=self.search_identity_window)
        btn_search.pack(side=LEFT, padx=80, pady=5)

    def register_identity_window(self):
        # variable for browse file to provide different function
        self.top = "register"
        # define new window attributes
        self.top_window = Toplevel(self.idb_window)
        self.top_window.geometry("600x400+450+150")
        self.top_window.title("Identity Registration")
        self.top_window.resizable(False,False)
        self.top_window.grab_set()

        # set ui column weight
        self.top_window.grid_columnconfigure(1, weight=1)

        # hide manage identity database window
        self.idb_window.withdraw()

        # define ui components
        # static labels
        lbl_name = Label(self.top_window, text="Name")
        lbl_gender = Label(self.top_window, text="Gender")
        lbl_remarks = Label(self.top_window, text="Remarks")
        lbl_face = Label(self.top_window, text="Upload Image (Contain only 1 face)")
        
        # entries, combobox, button, and dynamic labels
        self.entry_name = Entry(self.top_window, width=60)
        self.cmb_gender = Combobox(self.top_window, width=5, state="readonly", values=("M", "F"))
        self.cmb_gender.current(0)
        self.entry_remarks = Entry(self.top_window, width=60)
        self.btn_browse = Button(self.top_window, text="Browse Files", command=self.browse_file)
        self.lbl_file = Label(self.top_window, text="")
        self.lbl_img = Label(self.top_window)
        self.btn_confirm = Button(self.top_window, width=8, text="Confirm", state="disabled", command=self.reg_identity)

        # place ui components
        lbl_name.grid(row=0, column=0, pady=(5,0))
        self.entry_name.grid(row=0, column=1, sticky="W", pady=(5,0))

        lbl_gender.grid(row=1, column=0)
        self.cmb_gender.grid(row=1, column=1, sticky="W")

        lbl_remarks.grid(row=2, column=0)
        self.entry_remarks.grid(row=2, column=1, sticky="W")

        lbl_face.grid(row=3, column=0)
        self.btn_browse.grid(row=3, column=1, sticky="W")
        self.lbl_file.grid(row=4, column=1, sticky="W")
        self.lbl_img.grid(row=5, column=0, columnspan=2)
        self.btn_confirm.grid(row=6, column=0, columnspan=2)

        # window close event
        self.top_window.protocol("WM_DELETE_WINDOW", self.on_close)

    def search_identity_window(self):
        # variable for browse file to provide different function
        self.top = "search"
        # define new window attributes
        self.top_window = Toplevel(self.idb_window)
        self.top_window.geometry("600x480+450+150")
        self.top_window.title("Search/Modify Identity")
        self.top_window.resizable(False,False)
        self.top_window.grab_set()

        # set ui column weight
        self.top_window.grid_columnconfigure(1, weight=1)

        # hide manage identity database window
        self.idb_window.withdraw()

        # define ui components
        # for search purpose
        lbl_search = Label(self.top_window, text="Search Name")
        self.entry_search = Entry(self.top_window, width=60)
        self.btn_search = Button(self.top_window, width=8, text="Search", command=self.search_identity)
        self.lbl_search_msg = Label(self.top_window, text="")

        # for display and modify purpose
        # static labels
        lbl_name = Label(self.top_window, text="Name")
        lbl_gender = Label(self.top_window, text="Gender")
        lbl_remarks = Label(self.top_window, text="Remarks")
        lbl_face = Label(self.top_window, text="Upload Image (Contain only 1 face)")
        
        # entries, combobox, button, and dynamic labels
        self.entry_name = Entry(self.top_window, width=60)
        self.cmb_gender = Combobox(self.top_window, width=5, state="readonly", values=("M", "F"))
        self.cmb_gender.current(0)
        self.entry_remarks = Entry(self.top_window, width=60)
        self.btn_browse = Button(self.top_window, text="Browse Files", state="disabled", command=self.browse_file)
        self.lbl_file = Label(self.top_window, text="")
        self.lbl_img = Label(self.top_window)
        self.lbl_img.image = None
        self.btn_confirm = Button(self.top_window, width=8, text="Confirm", state="disabled", command=self.edit_identity)
        self.btn_delete = Button(self.top_window, width=8, text="Delete", state="disabled",command=self.delete_identity)

        # place ui components
        lbl_search.grid(row=0, column=0, pady=(5,0))
        self.entry_search.grid(row=0, column=1, sticky="W", pady=(5,0))
        self.btn_search.grid(row=1,column=0, columnspan=2)
        self.lbl_search_msg.grid(row=2,column=1,sticky="W", pady=(0,10))

        lbl_name.grid(row=3, column=0)
        self.entry_name.grid(row=3, column=1, sticky="W")

        lbl_gender.grid(row=4, column=0)
        self.cmb_gender.grid(row=4, column=1, sticky="W")

        lbl_remarks.grid(row=5, column=0)
        self.entry_remarks.grid(row=5, column=1, sticky="W")

        lbl_face.grid(row=6, column=0)
        self.btn_browse.grid(row=6, column=1, sticky="W")
        self.lbl_file.grid(row=7, column=1, sticky="W")
        self.lbl_img.grid(row=8, column=0, columnspan=2)
        self.btn_confirm.grid(row=9, column=0, columnspan=2, padx=(0,100))
        self.btn_delete.grid(row=9, column=0, columnspan=2, padx=(100,0))

        # window close event
        self.top_window.protocol("WM_DELETE_WINDOW", self.on_close)

    # function for clearing recognition record
    def clear_record(self):
        self.rec_window.destroy()
        prompt = messagebox.askyesno("Clear Record", "Are you sure you want to clear all existing records?")
        if prompt == True:
            # call database query function
            self.db.truncate_record()
            messagebox.showinfo("Info","Records cleared successfully!")
            self.view_authentication_window()
        else:
            self.view_authentication_window()

    # function for window close event (register & search window)
    def on_close(self):
        self.top_window.destroy()
        # open up identity database window
        self.identity_database_window()

    # function for browse file button
    def browse_file(self):
        # choose file window
        filename = filedialog.askopenfilename(
            parent = self.top_window, initialdir =  "/", title = "Select An Image", 
            filetypes = [("Image files (*.jpg;*.jpeg;*.jfif;*.png)",".jpg .jpeg .jfif .png")])
        
        # declare chosen image
        # for gui display purpose
        img = Image.open(filename)
        # for face detection and recognition purpose
        cv_img = cv2.imread(filename) 
        self.resized_cv_img = cv2.resize(cv_img,(640,480))
        # clone for detect function to avoid face count annonation
        self.clone_resized_cv_img = self.resized_cv_img.copy()

        # ensure only one face detected in the chosen image
        self.detected = self.face_detector.detect(self.clone_resized_cv_img)
        if len(self.detected)==1:
            # resize for display purpose
            display_img = img.resize((300,250))
            photo = ImageTk.PhotoImage(display_img)
            # configure label to display image
            self.lbl_file.configure(text=filename,fg="black")
            self.lbl_img.configure(image=photo)
            self.lbl_img.image = photo
            # enable confirm button
            self.btn_confirm.configure(state="normal")
        else:
            # display error message
            self.lbl_file.configure(text="Invalid image!",fg="red")
            self.lbl_img.image = None
            # disable confirm button if this function used in register
            if self.top == "register":
                self.btn_confirm.configure(state="disabled")
    
    # function for confirm register button in register
    def reg_identity(self):
        name = self.entry_name.get().strip()
        gender = self.cmb_gender.get()
        remarks = self.entry_remarks.get().strip()
        
        # face bounding box
        x1,y1,x2,y2 = self.detected[0][0],self.detected[0][1],self.detected[0][2],self.detected[0][3]
        crop_face = self.resized_cv_img[y1:y2, x1:x2]
        # obtain encoding
        encoding = self.face_recognition.encoding(crop_face)
        # store serialized encoding in BLOB datatype with pickle
        pickled_encoding = pickle.dumps(encoding)
        
        # check if name contains only alphabet and not empty
        if name and all(n.isalpha() or n.isspace() for n in name):
            # check if name used
            try:
                # call database add function
                self.db.add_identity(name, gender, pickled_encoding, remarks)
                # train nearest neighbor
                self.face_recognition.nn_train()
                # success messagebox
                messagebox.showinfo("Info","Identity registered successfully!")
                self.top_window.destroy()
                self.identity_database_window()
            except:
                messagebox.showerror("Error","Existing name!")
        else:
            messagebox.showerror("Error","Invalid name input!")

    # function for search identity
    def search_identity(self):
        # set default values to prevent stacking information when call multiple times
        self.entry_name.delete(0, END)
        self.cmb_gender.current(0)
        self.entry_remarks.delete(0, END)
        self.lbl_file.configure(text="")
        self.lbl_img.image = None
        self.lbl_search_msg.configure(text="")
        self.btn_browse.configure(state="disabled")
        self.btn_confirm.configure(state="disabled")
        self.btn_delete.configure(state="disabled")
        # search and obtain result
        try:
            name = self.entry_search.get().strip()
            if name:
                res = self.db.search_identity(name)
                self.id, name, gender, self.encoding, remark = res[0][0], res[0][1], res[0][2], res[0][3], res[0][4]
                self.entry_name.insert(0,name)
                self.cmb_gender.set(gender)
                self.entry_remarks.insert(0,remark)
                self.lbl_search_msg.configure(text="Identity found!",fg="black")
                # enable browse, confirm and delete button
                self.btn_browse.configure(state="normal")
                self.btn_confirm.configure(state="normal")
                self.btn_delete.configure(state="normal")
                # clear search entry
                self.entry_search.delete(0,END)
            else:
                self.lbl_search_msg.configure(text="Empty input!",fg="red")
        except:
            self.entry_name.configure(state="normal")
            self.entry_name.delete(0, END)
            self.lbl_search_msg.configure(text="Identity cannot be found!",fg="red")

    # function for edit identity
    def edit_identity(self):
        name = self.entry_name.get().strip()
        gender = self.cmb_gender.get()
        remarks = self.entry_remarks.get().strip()

        # check if name contains only alphabet and not empty
        if name and all(n.isalpha() or n.isspace() for n in name):
            # check if new image uploaded
            if self.lbl_img.image is not None:
                # face bounding box
                x1,y1,x2,y2 = self.detected[0][0],self.detected[0][1],self.detected[0][2],self.detected[0][3]
                # crop
                crop_face = self.resized_cv_img[y1:y2, x1:x2]
                # obtain encoding
                encoding = self.face_recognition.encoding(crop_face)
                # store serialized encoding in BLOB datatype with pickle
                self.encoding = pickle.dumps(encoding)
            try:
                # modify identity replacing existing encoding
                self.db.edit_identity(self.id, name, gender, self.encoding, remarks)
                # train nearest neighbor
                self.face_recognition.nn_train()
                # success messagebox
                messagebox.showinfo("Info","Identity modified successfully!")
                self.top_window.destroy()
                self.search_identity_window()
            except:
                messagebox.showerror("Error","Existing name!")
        else:
            messagebox.showerror("Error","Invalid name input!")

    # function for delete identity
    def delete_identity(self):
        prompt = messagebox.askyesno("Delete Identity", "Are you sure you want to delete this identity?")
        if prompt == True:
            # call database query function
            self.db.delete_identity(self.id)
            # train nearest neighbor
            self.face_recognition.nn_train()
            messagebox.showinfo("Info","Identity deleted successfully!")
            # revert default values
            self.entry_name.delete(0, END)
            self.cmb_gender.current(0)
            self.entry_remarks.delete(0, END)
            self.lbl_file.configure(text="")
            self.lbl_img.image = None
            self.lbl_search_msg.configure(text="")
            self.entry_search.delete(0, END)
            self.btn_browse.configure(state="disabled")
            self.btn_confirm.configure(state="disabled")
            self.btn_delete.configure(state="disabled")

    # function for display recognition result in main window
    def disp_recog_results(self,face,name,distance,timestamp):
        # process data
        format = "%Y-%m-%d %H:%M:%S"
        timestamp = datetime.strftime(timestamp,format)
        face_img = Image.fromarray(cv2.cvtColor(face, cv2.COLOR_BGR2RGB))
        face_imgtk = ImageTk.PhotoImage(image=face_img)
        
        # ensure max limit of 8 element
        if len(self.result_limit) < 8:
            # insert data to head
            self.result_limit.insert(0,[face_imgtk,name,distance,timestamp])
        else:
            # remove last item and insert new to head
            self.result_limit.pop()
            self.result_limit.insert(0,[face_imgtk,name,distance,timestamp])

        for cnt,r in enumerate(self.result_limit,1):
            if r[1] == "Unknown":
                self.widgets[(cnt,0)].configure(image=r[0], text=r[3]+"\n"+r[1]+","+str(r[2]),bg="#f09090")
            else:
                self.widgets[(cnt,0)].configure(image=r[0], text=r[3]+"\n"+r[1]+","+str(r[2]),bg=self.default_color)
            # self.widgets[(cnt,0)].configure(image=r[0], text=r[3]+"\n"+r[1]+","+str(r[2]))
            # anchor image to the object
            self.widgets[(cnt,0)].photo = face_imgtk
