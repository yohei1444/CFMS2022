import threading
import time
import datetime
import pickle
import os
import tkinter as tk
from tkinter import *
from tkinter import messagebox
import tkinter.simpledialog as simpledialog
import tkinter.ttk as ttk
import unicodedata
from math import  ceil
import sys
import tkmacosx as mtk

BASE_H = 2
info_list = {1: "一般商品（予約不可）",2:"予約可能商品",3:"例外在庫商品"}

def pickle_dump(obj, path):             #  rdata  書き込み
    try:
        with open(path,"wb") as f:
            pickle.dump(obj,f)
    except EOFError or TypeError:
        pass 

def pickle_load(path):                  #  rdata  読み込み
    
    try:
        with open(path,"rb") as f:
            data = pickle.load(f)
            return data
    except EOFError or TypeError:
        pass

def temp_path(relative_path):
    try:
        #Retrieve Temp Path
        base_path = sys._MEIPASS
    except Exception:
        #Retrieve Current Path Then Error 
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

logo=temp_path('test_icon.ico')

class Images:
    
    def __init__(self) -> None:
        
        self.image_lists = {}
        self.path = os.getcwd()
        #print(self.path,"イメージ")
        for image_name in os.listdir(self.path+"./images"):
            self.image_lists[image_name] = (tk.PhotoImage(file=self.path+"./images/"+ image_name))
    
    def image(self, name: str) -> tk.PhotoImage:
        
        return self.image_lists[name+".png"]

    def re_load(self):
        
        self.image_lists = {}
        
        for image_name in os.listdir("./images"):
            self.image_lists[image_name] = (tk.PhotoImage(file=self.path+"./images/"+ image_name))

#システム内関連class-----------------------------------------------------------------------------------------------------------------#

class CFMS_file:                    #ローカルデータ管理

    def __init__(self, txt_name : str) -> None:

        self.txt_name = txt_name  #使用する.txt名
        
        self.file_name = self.txt_name

        self.file_pass = "./cfms_shop_data.pickle"    #参照するファイルパス

        self.dict           = {}                #return用辞書

        self.list           = []                #return用リスト


    def data_dump(self,listname): #通常時データ保存

        pickle_dump(listname,self.file_pass)


    def dict_data_load(self): #通常時データ読み込み

        try:
            self.dict.update(pickle_load(self.file_pass))

            return self.dict
        except:
            print(f"data not found {type(self).__name__}")
            return {}

class CFMS_data:

    def __init__(self) -> None:
        
        self.data = {}
    
    def hq_entry(self,data_name,data):

        self.data[data_name] = data
        
        hq_files.data_dump(self.data)
    
    def hq_revert(self):
        self.data = hq_files.dict_data_load()

        if len(self.data) == 0:
            return False
        
        else:
            return True
    
    def shop_entry(self,data_name,data):

        self.data[data_name] = data
        
        shop_files.data_dump(self.data)
    
    def shop_revert(self):
        self.data = shop_files.dict_data_load()

        if len(self.data) == 0:
            return False
        
        else:
            return True
    
    
    def revert_data(self,data_name):
        if data_name in self.data.keys():
            return self.data[data_name]
        else:
            return {}

class CFMS_sale:
    
    def __init__(self,sale_list,cash) -> None:
        self.sale_data = sale_list
        self.datetime = datetime.datetime.now()
        self.cash = cash
    
    def create_dict(self):
        self.data = {}
        for i in self.sale_data:
            if i[-1] not in self.data.keys():
                self.data[i[-1]] = len(i)
            else:
                self.data[i[-1]] += len(i)
        
        return self.data
    
    def prev_data(self):
        return self.sale_date

class CFMS_all_sale_data:
    
    def __init__(self) -> None:
        self.sale_datas = []
    
    def entry(self,sale_data:CFMS_sale):
        self.sale_datas.append(sale_data)

        datas.shop_entry(type(self).__name__,self.sale_datas)
        
    def prev_all_data(self):
        self.data = {}
        for i in self.sale_datas:
            for k,v in i.create_dict().items():
                if k not in self.data.keys():
                    self.data[k] = v
                
                else:
                    self.data[k] += v
                    
        
        return self.data

    def revert(self,data):

        self.sale_datas = data
        if len(self.sale_datas) == 0:
            self.sale_datas = []
    
    def reset(self):
        self.sale_datas.clear()
        datas.shop_entry(type(self).__name__,self.sale_datas)

class CFMS_prod_info:               #個別商品情報
    
    def __init__(self, name :str, number :str, price :int) -> None:

        self.name = name
        self.number = number
        self.price = int(price)
    
    def prev_name(self) -> str: #商品名を返す
        return self.name
    
    def prev_number(self) -> str: #商品番号を返す
        return self.number
    
    def prev_price(self) -> int: #値段を返す
        return self.price
    
    def change_name(self, new_name : str) -> None : #商品名を変更する

        self.name = new_name
        datas.shop_entry(type(self).__name__,all_prod_info.prod_dict)
        
    
    def change_number(self, new_number : str) -> None: #商品番号を変更する
        if all_prod_info.unique_check(new_number):
            all_prod_info.drop(self)
            self.number = new_number
            datas.shop_entry(type(self).__name__,all_prod_info.prod_dict)

        
        else:
            if messagebox.askyesno("既に存在する商品番号","既に存在する商品番号です、上書きしますか？"):
                self.number = new_number
                datas.shop_entry(type(self).__name__,all_prod_info.prod_dict)
                
    
    def change_price(self, new_price : int) -> None: #値段を変更する
        
        self.price = int(new_price)
        datas.shop_entry(type(self).__name__,all_prod_info.prod_dict)

class CFMS_all_prod_info:           #商品情報一括管理

    def __init__(self) -> None:
        
        self.prod_dict = {}
    
    def entry(self,prod_info:CFMS_prod_info):
        
        self.prod_dict[prod_info.prev_number()] = prod_info
        
        datas.shop_entry(type(self).__name__,self.prod_dict)

    def drop(self,prod_info:CFMS_prod_info):
        self.prod_dict.pop(prod_info.prev_number())
        datas.shop_entry(type(self).__name__,self.prod_dict)


    def infomation(self,prod_number):
        if prod_number in self.prod_dict.keys():
            return self.prod_dict[prod_number]
        else:
            return False
    
    def unique_check(self,prod_number):
        return not prod_number in self.prod_dict.keys()
    
    def return_info_dict(self):
        return self.prod_dict
    
    def revert(self,data):

        self.prod_dict = data
    
    def reset(self):

        self.prod_dict.clear()
        
        datas.shop_entry(type(self).__name__,self.prod_dict)

class CFMS_pos:
    
    def __init__(self,page_window) -> None:
        self.show_info_list = []
        self.main_info = Main_info() #実態生成 画面生成
        self.page_frame = Page_frame(page_window.mainframe) #実態生成 画面生成
        self.cache_frame = Cache_frame() #実態生成 画面生成
        self.latest_page = 0
        
        self.oazukarien = tk.Entry(self.cache_frame.cache_frame,font=("HG創英角ｺﾞｼｯｸUB",25),width=10,justify=tk.CENTER)
        self.oazukarien.grid(row=1,column=1,padx=3)
        self.oazukarien["state"] = DISABLED

        self.oazukarien.bind("<Return>",self.change)

    def __call__(self,prod_number):
        
        if all_prod_info.infomation(prod_number) != False:
            self.prod_info = all_prod_info.infomation(prod_number)
            
            if len(self.show_info_list) == 0 or self.show_info_list[-1][-1].prev_number() != prod_number:
                self.show_info_list.append([self.prod_info])
            
            elif self.show_info_list[-1][-1].prev_number() == prod_number:
                self.show_info_list[-1].append(self.prod_info)

            bt_frame.sub_bt_frame_bt_list1[0]["state"] = NORMAL #取り消しボタン    有効化
            bt_frame.sub_bt_frame_bt_list1[1]["state"] = NORMAL #キャンセルボタン　有効化
            bt_frame.sub_bt_frame_bt_list1[1]["command"] = self.reset_bt
            bt_frame.sub_bt_frame_bt_list1[0]["command"] = lambda:[drop_sale_prod_window()]

            for i in bt_frame.bt_frame_bt_list:
                i["state"] = DISABLED
            
            bt_frame.sub_bt_frame_bt_list2[4]["state"] = DISABLED

            self.oazukarien["state"] = NORMAL
            self.page_frame.page_bt_dw["state"] = DISABLED



        
        else:
            messagebox.showerror("未登録","未登録の商品番号です。")
        
        
        self.show_update()
        self.cash()
    
    def show_update(self):
        self.main_info.reset()
        self.page_frame.page_bt_up["state"] = DISABLED
        
        if (len(self.show_info_list) / 7)-0.1 > len(self.show_info_list) // 7:
            self.latest_page = len(self.show_info_list) // 7
        
        else:
            self.latest_page = max(0,(len(self.show_info_list) // 7) -1) 
        
        for i in range(7*self.latest_page,min(7*(self.latest_page+1),len(self.show_info_list))):
            self.main_info.info_input(i%7,i+1,self.show_info_list[i][-1].prev_name(),self.show_info_list[i][-1].prev_price(),len(self.show_info_list[i]),self.show_info_list[i][-1].prev_price()*len(self.show_info_list[i]))
        
        
        
        if len(self.show_info_list)/7-0.1 > len(self.show_info_list)//7 and 0 < len(self.show_info_list)//7:
            self.page_frame.page_bt_up["fg"] = "#228b22"
            self.page_frame.page_bt_up["state"] = NORMAL
            self.page_frame.pagelbl["text"] = str(self.latest_page+1) + "/" + str(self.latest_page+1)
            self.page_frame.page_bt_up["command"] = lambda:[self.page_up(self.latest_page-1)]
        
        else:
            self.page_frame.pagelbl["text"] = str(self.latest_page+1) + "/" + str(self.latest_page+1)
        
            
        if len(self.show_info_list) == 0:
            self.reset()
    
    def cash(self):
        self.sums = 0
        for i in self.show_info_list:
            self.sums += len(i)*i[-1].prev_price()
        
        self.cache_frame.show_price(self.sums)
        self.cache_frame.change_reset()
        
    
    def change(self,event):
        
        self.change_price = int(self.oazukarien.get()) - self.sums
        
        if self.change_price >= 0:
            
        
            self.cache_frame.show_change(self.change_price)
            all_sale_data.entry(CFMS_sale(self.show_info_list,int(self.oazukarien.get())))
            self.reset()
        
        else:
            messagebox.showerror("残高不足","預り金が不足しています")
    
    def page_up(self,page):
        self.main_info.reset()
        for i in range(7*page,7*(page+1)):
            self.main_info.info_input(i%7,i+1,self.show_info_list[i][-1].prev_name(),self.show_info_list[i][-1].prev_price(),len(self.show_info_list[i]),self.show_info_list[i][-1].prev_price()*len(self.show_info_list[i]))

        self.page_frame.pagelbl["text"] = str(page+1) + "/" + str(self.latest_page+1)
        
        self.page_frame.page_bt_dw["command"] =  lambda:[self.page_down(page+1)] 
        self.page_frame.page_bt_dw["fg"] = "#228b22"
        self.page_frame.page_bt_dw["state"] = NORMAL


        
        if page <= 0:
            self.page_frame.page_bt_up["fg"] = "#000000"
            self.page_frame.page_bt_up["state"] = DISABLED
        
        else:
            self.page_frame.page_bt_up["command"] =  lambda:[self.page_up(page-1)] 
            self.page_frame.page_bt_up["fg"] = "#228b22"
    
    def page_down(self,page):
        self.main_info.reset()
        
        for i in range(7*page,min(7*(page+1),len(self.show_info_list))):
            self.main_info.info_input(i%7,i+1,self.show_info_list[i][-1].prev_name(),self.show_info_list[i][-1].prev_price(),len(self.show_info_list[i]),self.show_info_list[i][-1].prev_price()*len(self.show_info_list[i]))

        self.page_frame.pagelbl["text"] = str(page+1) + "/" + str(self.latest_page+1)
        
        self.page_frame.page_bt_up["command"] = lambda:[self.page_up(page-1)] 
        self.page_frame.page_bt_up["fg"] = "#228b22"
        self.page_frame.page_bt_up["state"] = NORMAL


        
        if page == self.latest_page:
            self.page_frame.page_bt_dw["fg"] = "#000000"
            self.page_frame.page_bt_dw["state"] = DISABLED
        
        else:
            self.page_frame.page_bt_dw["command"] =  lambda:[self.page_down(page+1)]  
            self.page_frame.page_bt_dw["fg"] = "#228b22"


    def reset(self):
        self.latest_page = 0
        self.page_frame.page_bt_dw["state"] = DISABLED
        self.page_frame.page_bt_up["state"] = DISABLED
        self.page_frame.pagelbl["text"] = "1" + "/" + "1"
        self.cache_frame.price_reset()
        self.oazukarien.delete(0,"end")
        self.main_info.reset()
        self.sums = 0
        self.show_info_list = []
        home_top_gui.entry_focus()
        self.oazukarien["state"] = DISABLED
        bt_frame.sub_bt_frame_bt_list1[0]["state"] = DISABLED #取り消しボタン    有効化
        bt_frame.sub_bt_frame_bt_list1[1]["state"] = DISABLED
        for i in bt_frame.bt_frame_bt_list:
                i["state"] = NORMAL
        bt_frame.sub_bt_frame_bt_list2[4]["state"] = NORMAL
    
    def reset_bt(self):
        if messagebox.askyesno("確認","本当に一括取消を行いますか？"):
            self.reset()

class CFMS_inserter:

    def __init__(self,none,select_window) -> None:
        self.window = select_window
    
    def __call__(self, **kwargs):
        self.prod_info = kwargs["pr"]
        pos(self.prod_info.prev_number())
        self.window.window.destroy()

#------------------------------------------------------------------------------------------------------------------------------------#
#ウィンドウ関連class-----------------------------------------------------------------------------------------------------------------#

class Cfms_defalut_window:                               #テンプレートウィンドウ
    
    def __init__(self,title) -> None:
        self.titles = title
        self.window = None
    
    def __call__(self,**kwargs):
        self.kwargs = kwargs
        self.win_check(kwargs)
    
    def fixe(self):
        self.window.resizable(False, False)
    
    def win_check(self,kwargs):   #サブウィンドウ重複チェック
        
        if self.window == None or not self.window.winfo_exists():
                
                self.create(kwargs) #ウィンドウが生成されていない場合ウィンドウを生成する
                
                if self.window != None and self.window.winfo_exists():
                    self.fixe()
            
        elif self.window.winfo_exists():
            self.window.destroy()
            self.create(kwargs)
            self.fixe()

    def activate(self):
        self.window.focus_force()

class Cfms_defalut_TinT_window:

    def __init__(self,title,base_window_class) -> None:
        self.titles = title
        self.window = None
        self.base_window_class = base_window_class
    
    def __call__(self,**kwargs):
        self.kwargs = kwargs
        self.win_check()

    def win_check(self):
        if self.window == None or not self.window.winfo_exists():
            self.create()
            if self.window != None and self.window.winfo_exists():
                self.fixe()
        elif self.window.winfo_exists():
            self.window.destroy()
            self.create()
            self.fixe()

    def fixe(self):
        self.window.resizable(False, False)
    
    def activate(self):
        self.window.focus_force()

class Cfms_defalut_selecter_from_prod_number(Cfms_defalut_window):
    
    def __init__(self, title, info, tint_class, tint_info, category:str, color:str,) -> None:
        super().__init__(title)
        self.NUMBER = 6
        self.info = info
        self.cmd = tint_class(tint_info,self)
        self.category = category
        self.color = color

    def create(self,kwargs):
        
        self.info_dict = self.info.return_info_dict()

        if len(self.info_dict) >= 1:
            self.window = Toplevel()
            self.window.title(self.titles)
            
            self.title = Cfms_title_label(self.window,self.titles,4)
            self.title()

            self.main_farame = Frame(self.window)
            self.main_farame.grid(row=1,column=1,rowspan=int(self.NUMBER/2),columnspan=2)
            self.bt_create()
        
        else:
            messagebox.showerror("未登録",f"{self.category}情報がないため閲覧できません。")

    def bt_create(self):

        self.bg = self.color
        self.bt_list = []
        
        self.list_update(0)
        
        for i in range(len(self.info_list)):
            
            if i == 0:
                self.bt0 = Button(self.main_farame,text=self.info_list[0].prev_name(),font=("HG創英角ｺﾞｼｯｸUB",15),height=5,width=30,command=lambda:[self.cmd(pr=self.info_list[0])],bg=self.bg,fg="#000000",bd=5)
                self.bt0.grid(row=i//2,column=i%2, padx=5, pady=5)
                self.bt_list.append(self.bt0)
            elif i == 1:
                self.bt1 = Button(self.main_farame,text=self.info_list[1].prev_name(),font=("HG創英角ｺﾞｼｯｸUB",15),height=5,width=30,command=lambda:[self.cmd(pr=self.info_list[1])],bg=self.bg,fg="#000000",bd=5)
                self.bt1.grid(row=i//2,column=i%2, padx=5, pady=5)
                self.bt_list.append(self.bt1)
                
            elif i == 2:
                self.bt2 = Button(self.main_farame,text=self.info_list[2].prev_name(),font=("HG創英角ｺﾞｼｯｸUB",15),height=5,width=30,command=lambda:[self.cmd(pr=self.info_list[2])],bg=self.bg,fg="#000000",bd=5)
                self.bt2.grid(row=i//2,column=i%2, padx=5, pady=5)
                self.bt_list.append(self.bt2)
                
            elif i == 3:
                self.bt3 = Button(self.main_farame,text=self.info_list[3].prev_name(),font=("HG創英角ｺﾞｼｯｸUB",15),height=5,width=30,command=lambda:[self.cmd(pr=self.info_list[3])],bg=self.bg,fg="#000000",bd=5)
                self.bt3.grid(row=i//2,column=i%2, padx=5, pady=5)
                self.bt_list.append(self.bt3)
                
            elif i == 4:
                self.bt4 = Button(self.main_farame,text=self.info_list[4].prev_name(),font=("HG創英角ｺﾞｼｯｸUB",15),height=5,width=30,command=lambda:[self.cmd(pr=self.info_list[4])],bg=self.bg,fg="#000000",bd=5)
                self.bt4.grid(row=i//2,column=i%2, padx=5, pady=5) 
                self.bt_list.append(self.bt4)
            elif i == 5:
                self.bt5 = Button(self.main_farame,text=self.info_list[5].prev_name(),font=("HG創英角ｺﾞｼｯｸUB",15),height=5,width=30,command=lambda:[self.cmd(pr=self.info_list[5])],bg=self.bg,fg="#000000",bd=5)
                self.bt5.grid(row=i//2,column=i%2, padx=5, pady=5)
                self.bt_list.append(self.bt5)
                

            
        self.left_button = Button(self.window,text="◀",height=10,width=5,state=DISABLED,bd=5)
        self.left_button.grid(row=1,column=0,rowspan=3, padx=5, pady=5)
        if len(self.info_dict) > self.NUMBER:
            self.right_button = Button(self.window,text="▶",height=10,width=5,command=lambda:[self.right_bt(1)],bd=5)
            self.right_button.grid(row=1,column=3,rowspan=4, padx=5, pady=5)
            self.right_button["fg"] = "#32cd32"
            
            self.left_button.destroy()
            self.left_button = Button(self.window,text="◀",height=10,width=5,state=DISABLED,bd=5)
            self.left_button.grid(row=1,column=0,rowspan=4, padx=5, pady=5)
            self.page_frame = Frame(self.main_farame)
            self.page_frame.grid(row=4,column=0,columnspan=2, padx=5, pady=5)
            self.page_entry = Entry(self.page_frame,font=("HG創英角ｺﾞｼｯｸUB",20),width=3,justify="center")
            self.page_entry.grid(row=0,column=0, padx=5, pady=5,sticky=E)
            self.page_entry.bind("<Return>",self.page_move)
            self.page_label = Label(self.page_frame,text=f"/ {ceil(len(self.info_dict)/self.NUMBER)}",font=("HG創英角ｺﾞｼｯｸUB",20))
            self.page_label.grid(row=0,column=1, padx=5, pady=5,sticky=W)
            self.page_entry.delete("0","end")
            self.page_entry.insert("0",str(self.page+1))
            
        else:
            self.right_button = Button(self.window,text="▶",height=10,width=5,state=DISABLED,bd=5)
            self.right_button.grid(row=1,column=3,rowspan=3)
            self.right_button["fg"] = "#000000"

    def right_bt(self,page):

        self.list_update(page)

        for i in self.bt_list:
            i["text"] = ""
            i["state"] = DISABLED

        for i in range(len(self.info_list)):
            
            if i == 0:
                self.bt0["state"] = NORMAL
                self.bt0["text"] = self.info_list[0].prev_name()
                self.bt0["command"] = lambda:[self.cmd(pr=self.info_list[0])]
            elif i == 1:
                self.bt1["state"] = NORMAL
                self.bt1["text"] = self.info_list[1].prev_name()
                self.bt1["command"] = lambda:[self.cmd(pr=self.info_list[1])]
            elif i == 2:
                self.bt2["state"] = NORMAL
                self.bt2["text"] = self.info_list[2].prev_name()
                self.bt2["command"] = lambda:[self.cmd(pr=self.info_list[2])]
            elif i == 3:
                self.bt3["state"] = NORMAL
                self.bt3["text"] = self.info_list[3].prev_name()
                self.bt3["command"] = lambda:[self.cmd(pr=self.info_list[3])]
            elif i == 4:
                self.bt4["state"] = NORMAL
                self.bt4["text"] = self.info_list[4].prev_name()
                self.bt4["command"] = lambda:[self.cmd(pr=self.info_list[4])]      
            elif i == 5:
                self.bt5["state"] = NORMAL
                self.bt5["text"] = self.info_list[5].prev_name()
                self.bt5["command"] = lambda:[self.cmd(pr=self.info_list[5])]
        
        self.left_button["command"]= lambda:[self.left_bt(page-1)]
        self.left_button["fg"] = "#32cd32"
        self.left_button["state"]=NORMAL

        if len(self.info_dict) > self.NUMBER * (page+1):
            self.right_button["command"]=lambda:[self.right_bt(page+1)]
            self.right_button["fg"] = "#32cd32"
            self.right_button["state"] = NORMAL
        

        else:
            self.right_button["state"]=DISABLED
            self.right_button["fg"] = "#000000"
        
        self.page_entry.delete("0","end")
        self.page_entry.insert("0",str(self.page+1))

    def left_bt(self,page):

        self.list_update(page)

        for i in self.bt_list:
            i["text"] = ""
            i["state"] = NORMAL

        for i in range(len(self.info_list)):
            
            if i == 0:
                self.bt0["text"] = self.info_list[0].prev_name()
                self.bt0["command"] = lambda:[self.cmd(pr=self.info_list[0])]
            elif i == 1:
                self.bt1["text"] = self.info_list[1].prev_name()
                self.bt1["command"] = lambda:[self.cmd(pr=self.info_list[1])]
            elif i == 2:
                self.bt2["text"] = self.info_list[2].prev_name()
                self.bt2["command"] = lambda:[self.cmd(pr=self.info_list[2])]
            elif i == 3:
                self.bt3["text"] = self.info_list[3].prev_name()
                self.bt3["command"] = lambda:[self.cmd(pr=self.info_list[3])]
            elif i == 4:
                self.bt4["text"] = self.info_list[4].prev_name()
                self.bt4["command"] = lambda:[self.cmd(pr=self.info_list[4])]      
            elif i == 5:
                self.bt5["text"] = self.info_list[5].prev_name()
                self.bt5["command"] = lambda:[self.cmd(pr=self.info_list[5])]
        
        self.right_button["command"]=lambda:[self.right_bt(page+1)]
        self.right_button["fg"] = "#32cd32"
        self.right_button["state"]=NORMAL
        
        if page > 0:
            self.left_button["command"]=lambda:[self.left_bt(page-1)]
            self.left_button["fg"] = "#32cd32"
            self.left_button["state"]=NORMAL


        else:
            self.left_button["state"]=DISABLED
            self.left_button["fg"] = "#000000"
        
        self.page_entry.delete("0","end")
        self.page_entry.insert("0",str(self.page+1))

    def list_update(self,page):
        self.page = page 
        self.info_dict = self.info.return_info_dict()
        self.info_list = []
        for i in range(page*self.NUMBER,min((page+1)*self.NUMBER+1,len(self.info_dict.keys()))):
            self.info_list.append(self.info_dict[list(self.info_dict.keys())[i]])

    def page_move(self,event):
        self.page = min(max(int(self.page_entry.get()),1),ceil(len(self.info_dict)/self.NUMBER)) - 1 

        self.list_update(self.page)

        
        for i in self.bt_list:
            i["text"] = ""
            i["state"] = DISABLED

        for i in range(len(self.info_list)):
            
            if i == 0:
                self.bt0["state"] = NORMAL
                self.bt0["text"] = self.info_list[0].prev_name()
                self.bt0["command"] = lambda:[self.cmd(pr=self.info_list[0])]
            elif i == 1:
                self.bt1["state"] = NORMAL
                self.bt1["text"] = self.info_list[1].prev_name()
                self.bt1["command"] = lambda:[self.cmd(pr=self.info_list[1])]
            elif i == 2:
                self.bt2["state"] = NORMAL
                self.bt2["text"] = self.info_list[2].prev_name()
                self.bt2["command"] = lambda:[self.cmd(pr=self.info_list[2])]
            elif i == 3:
                self.bt3["state"] = NORMAL
                self.bt3["text"] = self.info_list[3].prev_name()
                self.bt3["command"] = lambda:[self.cmd(pr=self.info_list[3])]
            elif i == 4:
                self.bt4["state"] = NORMAL
                self.bt4["text"] = self.info_list[4].prev_name()
                self.bt4["command"] = lambda:[self.cmd(pr=self.info_list[4])]      
            elif i == 5:
                self.bt5["state"] = NORMAL
                self.bt5["text"] = self.info_list[5].prev_name()
                self.bt5["command"] = lambda:[self.cmd(pr=self.info_list[5])]
        

        
        if self.page > 0:
            self.left_button["command"]=lambda:[self.left_bt(self.page-1)]
            self.left_button["fg"] = "#32cd32"
            self.left_button["state"]=NORMAL


        else:
            self.left_button["state"]=DISABLED
            self.left_button["fg"] = "#000000"

        if len(self.info_dict) > self.NUMBER * (self.page+1):
            self.right_button["command"]=lambda:[self.right_bt(self.page+1)]
            self.right_button["fg"] = "#32cd32"
            self.right_button["state"] = NORMAL
        

        else:
            self.right_button["state"]=DISABLED
            self.right_button["fg"] = "#000000"

        self.page_entry.delete("0","end")
        self.page_entry.insert("0",str(self.page+1))

class Cfms_title_label:
    def __init__(self,window,title,span=2) -> None:
        self.window = window
        self.title = title
        self.span = span
    
    def __call__ (self):
        Label(self.window,text=f"～{self.title}～",font=("HG創英角ｺﾞｼｯｸUB",20)).grid(row=0,column=0,columnspan=self.span,padx=5, pady=5,ipadx=10,ipady=10)

class Cfms_shop_prod_entry_register_window(Cfms_defalut_TinT_window):

    def __init__(self, title, base_window_class) -> None:
        super().__init__(title, base_window_class)
        
    def create(self):
        self.br_prod_name   = self.base_window_class.prod_name_entry.get()
        self.br_prod_number = unicodedata.normalize("NFKC",self.base_window_class.prod_number_entry.get())
        self.br_prod_price  = unicodedata.normalize("NFKC",self.base_window_class.prod_price_entry.get())

        self.window = Toplevel()
        self.window.title(self.titles)

        self.check_title_lbl = Label(self.window,text="～登録前確認画面～",font=("HG創英角ｺﾞｼｯｸUB",20))
        self.check_title_lbl.grid(row=0,column=0,columnspan=3,padx=5, pady=5,ipadx=10,ipady=10)

        self.check_name_lbl = Label(self.window,text='商品名　',font=("HG創英角ｺﾞｼｯｸUB",15))
        self.check_name_lbl.grid(row=1, column=0, padx=5, pady=5,ipadx=10,ipady=10,sticky=W)    
        self.check_name_lbl2 = Label(self.window,text=self.br_prod_name,font=("HG創英角ｺﾞｼｯｸUB",15))
        self.check_name_lbl2.grid(row=1, column=1, padx=5, pady=5,ipadx=10,ipady=10,sticky=W)   

        self.check_num_lbl = Label(self.window,text='商品番号',font=("HG創英角ｺﾞｼｯｸUB",15))
        self.check_num_lbl.grid(row=2, column=0, padx=5, pady=5,ipadx=10,ipady=10,sticky=W)
        self.check_num_lbl2 = Label(self.window,text=self.br_prod_number,font=("HG創英角ｺﾞｼｯｸUB",15))
        self.check_num_lbl2.grid(row=2, column=1, padx=5, pady=5,ipadx=10,ipady=10,sticky=W)

        self.check_price_lbl = Label(self.window,text='価格　　',font=("HG創英角ｺﾞｼｯｸUB",15))
        self.check_price_lbl.grid(row=3, column=0, padx=5, pady=5,ipadx=10,ipady=10,sticky=W)
        self.check_price_lbl = Label(self.window,text=f"{self.br_prod_price} 円",font=("HG創英角ｺﾞｼｯｸUB",15))
        self.check_price_lbl.grid(row=3, column=1, padx=5, pady=5,ipadx=10,ipady=10,sticky=W)

        self.check_bt_frame = Frame(self.window)
        self.check_bt_frame.grid(row=6, column=0,columnspan=2)

        self.check_enter_bt = Button(self.check_bt_frame,text='登録',font=("HG創英角ｺﾞｼｯｸUB",15),bd=3,command=self.register)
        self.check_enter_bt.grid(row=1, column=0, padx=20, pady=10,ipadx=10,ipady=10,)

        self.check_back_bt = Button(self.check_bt_frame,text='戻る',font=("HG創英角ｺﾞｼｯｸUB",15),bd=3,command=self.window.destroy)
        self.check_back_bt.grid(row=1, column=1, padx=20, pady=10,ipadx=10,ipady=10,)
    
    def register(self):

        if all_prod_info.unique_check(self.br_prod_number):
            all_prod_info.entry(CFMS_prod_info(
                self.br_prod_name,
                self.br_prod_number,
                self.br_prod_price,
            ))
            messagebox.showinfo("登録完了","商品が登録されました")
            self.base_window_class.window.destroy()
            self.window.destroy()
        
        else:
            messagebox.showerror("すでに登録されている商品番号","商品番号は一意の必要があります")
            self.base_window_class.activate()
            self.window.destroy()

class Cfms_shop_prod_entry(Cfms_defalut_window):

    def __init__(self, title) -> None:
        super().__init__(title)

        self.prod_check_win = Cfms_shop_prod_entry_register_window("確認画面",self)
    
    def create(self,kwargs):

        
        self.window = Toplevel()
        self.window.title(self.titles)

        self.title = Cfms_title_label(self.window,"商品情報登録画面",3)
        self.title()
        
        self.prod_name_lbl = Label(self.window,text='商品名　',font=("HG創英角ｺﾞｼｯｸUB",15))
        self.prod_name_lbl.grid(row=1, column=0, padx=5, pady=5,ipadx=10,ipady=10)
        self.prod_name_entry = Entry(self.window,width=30,font=("HG創英角ｺﾞｼｯｸUB",15))
        self.prod_name_entry.grid(row=1, column=1, padx=5, pady=5,ipadx=10,ipady=10)

        self.prod_number_lbl = Label(self.window,text='商品番号',font=("HG創英角ｺﾞｼｯｸUB",15))
        self.prod_number_lbl.grid(row=2, column=0, padx=5, pady=5,ipadx=10,ipady=10)
        self.prod_number_entry = Entry(self.window,width=30,font=("HG創英角ｺﾞｼｯｸUB",15))
        self.prod_number_entry.grid(row=2, column=1, padx=5, pady=5,ipadx=10,ipady=10)

        self.prod_price_lbl = Label(self.window,text='価格　　',font=("HG創英角ｺﾞｼｯｸUB",15))
        self.prod_price_lbl.grid(row=3, column=0, padx=5, pady=5,ipadx=10,ipady=10)
        self.prod_price_entry = Entry(self.window,width=30,font=("HG創英角ｺﾞｼｯｸUB",15))
        self.prod_price_entry.grid(row=3, column=1, padx=5, pady=5,ipadx=10,ipady=10)

        self.prod_price_lbl2 = Label(self.window,text='円',font=("HG創英角ｺﾞｼｯｸUB",15))
        self.prod_price_lbl2.grid(row=3, column=2, padx=5, pady=5,ipadx=10,ipady=10,sticky=W)

        self.prod_info_enter_bt = Button(self.window,text = '登録',font=("HG創英角ｺﾞｼｯｸUB",15),command=lambda:[self.prod_befor_register()],bd=3)
        self.prod_info_enter_bt.grid(row=5, column=2, padx=5, pady=5,ipadx=10,ipady=10,rowspan=3)

    
    def prod_befor_register(self):
        self.prod_check_win()

class Cfms_prod_info_view(Cfms_defalut_TinT_window):

    def __init__(self, title, base_window_class) -> None:
        super().__init__(title, base_window_class)

    def create(self):

        self.window = Toplevel()
        self.window.title(self.titles)

        self.prod_info = self.kwargs["pr"]

        self.title = Cfms_title_label(self.window,self.prod_info.prev_name(),3)
        self.title()

        self.prev()

    def prev(self):
        
        self.prod_name_lbl = Label(self.window,text='商品名　',font=("HG創英角ｺﾞｼｯｸUB",15))
        self.prod_name_lbl.grid(row=1, column=0, padx=5, pady=5,ipadx=10,ipady=10)
        self.prod_name_lbl2 = Label(self.window,text=self.prod_info.prev_name(),font=("HG創英角ｺﾞｼｯｸUB",15))
        self.prod_name_lbl2.grid(row=1, column=1, padx=5, pady=5,ipadx=10,ipady=10)

        self.prod_number_lbl = Label(self.window,text='商品番号',font=("HG創英角ｺﾞｼｯｸUB",15))
        self.prod_number_lbl.grid(row=2, column=0, padx=5, pady=5,ipadx=10,ipady=10)
        self.prod_number_lbl2 = Label(self.window,text=self.prod_info.prev_number(),width=20,font=("HG創英角ｺﾞｼｯｸUB",15))
        self.prod_number_lbl2.grid(row=2, column=1, padx=5, pady=5,ipadx=10,ipady=10)

        self.prod_price_lbl = Label(self.window,text='価格　　',font=("HG創英角ｺﾞｼｯｸUB",15))
        self.prod_price_lbl.grid(row=3, column=0, padx=5, pady=5,ipadx=10,ipady=10)
        self.prod_price_lbl2 = Label(self.window,text=self.prod_info.prev_price(),width=20,font=("HG創英角ｺﾞｼｯｸUB",15))
        self.prod_price_lbl2.grid(row=3, column=1, padx=5, pady=5,ipadx=10,ipady=10)

        self.prod_price_lbl3 = Label(self.window,text='円',font=("HG創英角ｺﾞｼｯｸUB",15))
        self.prod_price_lbl3.grid(row=3, column=2, padx=5, pady=5,ipadx=10,ipady=10,sticky=W)

        self.prod_info_enter_bt = Button(self.window,text = '編集',font=("HG創英角ｺﾞｼｯｸUB",15),command=self.edit,bd=3)
        self.prod_info_enter_bt.grid(row=5, column=2, padx=5, pady=5,ipadx=10,ipady=10)
        
        self.prod_info_delete_bt = Button(self.window,text = '削除',font=("HG創英角ｺﾞｼｯｸUB",15),command=self.drop_info,bd=3)
        self.prod_info_delete_bt.grid(row=5, column=0, padx=5, pady=5,ipadx=10,ipady=10)

    def edit(self):
        self.window.destroy()
        self.window = Toplevel()
        self.window.title(self.titles)

        self.title = Cfms_title_label(self.window,self.prod_info.prev_name(),3)
        self.title()

        self.prod_name_lbl = Label(self.window,text='商品名　',font=("HG創英角ｺﾞｼｯｸUB",15))
        self.prod_name_lbl.grid(row=1, column=0, padx=5, pady=5,ipadx=10,ipady=10)
        self.prod_name_entry = Entry(self.window,width=30,font=("HG創英角ｺﾞｼｯｸUB",15))
        self.prod_name_entry.grid(row=1, column=1, padx=5, pady=5,ipadx=10,ipady=10)
        self.prod_name_entry.insert(0,self.prod_info.prev_name())

        self.prod_number_lbl = Label(self.window,text='商品番号',font=("HG創英角ｺﾞｼｯｸUB",15))
        self.prod_number_lbl.grid(row=2, column=0, padx=5, pady=5,ipadx=10,ipady=10)
        self.prod_number_entry = Entry(self.window,width=30,font=("HG創英角ｺﾞｼｯｸUB",15))
        self.prod_number_entry.grid(row=2, column=1, padx=5, pady=5,ipadx=10,ipady=10)
        self.prod_number_entry.insert(0,self.prod_info.prev_number())

        self.prod_price_lbl = Label(self.window,text='価格　　',font=("HG創英角ｺﾞｼｯｸUB",15))
        self.prod_price_lbl.grid(row=3, column=0, padx=5, pady=5,ipadx=10,ipady=10)
        self.prod_price_entry = Entry(self.window,width=30,font=("HG創英角ｺﾞｼｯｸUB",15))
        self.prod_price_entry.grid(row=3, column=1, padx=5, pady=5,ipadx=10,ipady=10)
        self.prod_price_entry.insert(0,self.prod_info.prev_price())


        self.prod_price_lbl2 = Label(self.window,text='円',font=("HG創英角ｺﾞｼｯｸUB",15))
        self.prod_price_lbl2.grid(row=3, column=2, padx=5, pady=5,ipadx=10,ipady=10,sticky=W)
        

        self.prod_info_enter_bt = Button(self.window,text = '変更',font=("HG創英角ｺﾞｼｯｸUB",15),command=lambda:[self.register()],bd=3)
        self.prod_info_enter_bt.grid(row=5, column=2, padx=5, pady=5,ipadx=10,ipady=10,rowspan=3)


    def register(self):
        
        self.prod_info.change_name(self.prod_name_entry.get())
        self.prod_info.change_price(int(unicodedata.normalize("NFKC",(self.prod_price_entry.get()))))
        self.prod_info.change_number(unicodedata.normalize("NFKC",self.prod_number_entry.get()))
        
        all_prod_info.entry(self.prod_info)
        
        self.window.destroy()
        
        self.base_window_class.window.destroy()
        self.base_window_class.create(self.base_window_class.kwargs)
    
    def drop_info(self):
        
        if messagebox.askokcancel("確認","本当に商品情報を削除してもよろしいですか？"):
            all_prod_info.drop(self.prod_info)
            self.window.destroy()
            self.base_window_class.window.destroy()

class Cfms_prod_info_select(Cfms_defalut_selecter_from_prod_number):

    def __init__(self, title, info_dict: dict, tint_class, tint_info, category: str, color: str) -> None:
        super().__init__(title, info_dict, tint_class, tint_info, category, color)

class Cfms_prod_select(Cfms_defalut_selecter_from_prod_number):

    def __init__(self, title, info, tint_class, tint_info, category: str, color: str) -> None:
        super().__init__(title, info, tint_class, tint_info, category, color)

class Cfms_drop_sale_prod(Cfms_defalut_window):

    def __init__(self, title) -> None:
        super().__init__(title)
    
    def create(self,kwargs):
        
        #列見出し
        self.lists = pos.show_info_list

        self.window = Toplevel()
        self.window.title(self.titles)
        self.page_button = Page_frame(self.window)
        self.main_frame_main_info_list = []

        self.main_frame_main_info_defalut_info = {"font":("HG創英角ｺﾞｼｯｸUB",15), "height":BASE_H, "borderwidth" : 1, "relief":"sunken", "bg":"#add8e6","disabledforeground":"#000000"}

        self.main_frame_main_info_width_list = [
                                            {"width" : 7},
                                            {"width" : 45},
                                            {"width" : 20},
                                            {"width" : 10},
                                            {"width" : 20},
                                            {"width" : 12},
                                        ]

        self.main_frame_main_info_text_list = [
                                            {"text" : "行","state":DISABLED},
                                            {"text" : "商品名","state":DISABLED},
                                            {"text" : "単価","state":DISABLED},
                                            {"text" : "数量","state":DISABLED},
                                            {"text" : "金額","state":DISABLED},
                                            {"text" : "","state":DISABLED},                                    
                                        ]

        NUMBER = 6

        for i in range(NUMBER):
            cnf = {}
            cnf.update(self.main_frame_main_info_defalut_info)
            cnf.update(self.main_frame_main_info_width_list[i])
            cnf.update(self.main_frame_main_info_text_list[i])
            
            self.main_frame_main_info_list.append(Button(self.window,cnf = cnf))

        for i in range(NUMBER):
            self.main_frame_main_info_list[i].grid(row=0,column=i,sticky=W)
            

        
        
        #商品情報表示label基本情報

        mainframe_lbl_defalut_info = {"font":("HG創英角ｺﾞｼｯｸUB",15), "height":BASE_H, "borderwidth" : 1, "relief":"sunken"}

        self.CULOMNS_NUMBER = 7 #段数
        ##行

        self.gyou_info = {"width":7}
        self.gyou_info.update(mainframe_lbl_defalut_info)
        self.mainframe_gyou_list =[]

        for i in range(self.CULOMNS_NUMBER):
            self.mainframe_gyou_list.append(Button(self.window,cnf=self.gyou_info))



        ##商品名

        self.name_info = {"width":45}
        self.name_info.update(mainframe_lbl_defalut_info)
        self.mainframe_name_list =[]

        for i in range(self.CULOMNS_NUMBER):
            self.mainframe_name_list.append(Button(self.window,cnf=self.name_info))


        ##単価

        self.tanka_info = {"width":20}
        self.tanka_info.update(mainframe_lbl_defalut_info)
        self.mainframe_tanka_list =[]


        for i in range(self.CULOMNS_NUMBER):
            self.mainframe_tanka_list.append(Button(self.window,cnf=self.tanka_info))

        ##個数

        self.kos_info = {"width":10}
        self.kos_info.update(mainframe_lbl_defalut_info)
        self.mainframe_kos_list =[]


        for i in range(self.CULOMNS_NUMBER):
            self.mainframe_kos_list.append(Button(self.window,cnf=self.kos_info))

        ##金額

        self.kingaku_info = {"width":20}
        self.kingaku_info.update(mainframe_lbl_defalut_info)
        self.mainframe_kingaku_list =[]

        for i in range(self.CULOMNS_NUMBER):
            self.mainframe_kingaku_list.append(Button(self.window,cnf=self.kingaku_info))

        ###生成

        for i in range(self.CULOMNS_NUMBER):
            
            self.mainframe_gyou_list[i].grid(row= 1 + i, column= 0, sticky=W)
            self.mainframe_name_list[i].grid(row= 1 + i, column= 1, sticky=W)
            self.mainframe_tanka_list[i].grid(row= 1 + i, column= 2, sticky=W)
            self.mainframe_kos_list[i].grid(row= 1 + i, column= 3, sticky=W)
            self.mainframe_kingaku_list[i].grid(row= 1 + i, column= 4, sticky=W)
        
        if len(self.lists) / 7-0.1 > len(self.lists) // 7:
            self.latest_page = len(self.lists) // 7
        
        else:
            self.latest_page = max(0,(len(self.lists) // 7) -1) 

        self.show_update(self.latest_page)
        self.page = self.latest_page
        
        self.page_button.page_bt_dw["state"] = DISABLED
        self.page_button.page_bt_up["state"] = DISABLED

        if self.latest_page >= 1 :
            self.page_button.page_bt_up["state"] = NORMAL
            self.page_button.page_bt_up["fg"] = "#228b22"
            self.page_button.page_bt_up["command"] = lambda:[self.page_up(self.latest_page-1)]
    
    def reset(self):
        
        for i in range(self.CULOMNS_NUMBER):
            self.mainframe_gyou_list[i]["text"] = ""
            self.mainframe_name_list[i]["text"] = ""
            self.mainframe_tanka_list[i]["text"] = ""
            self.mainframe_kos_list[i]["text"] = ""
            self.mainframe_kingaku_list[i]["text"] = ""
            
            self.mainframe_gyou_list[i]["command"] =    None
            self.mainframe_name_list[i]["command"] =    None
            self.mainframe_tanka_list[i]["command"] =   None
            self.mainframe_kos_list[i]["command"] =     None
            self.mainframe_kingaku_list[i]["command"] = None
            
    
    def info_input(self, culomn:int, gyou:int, name:str, tanka:int, kos:int, kingaku:int):
        
        self.mainframe_gyou_list[culomn]["text"] = gyou
        self.mainframe_name_list[culomn]["text"] = name
        self.mainframe_tanka_list[culomn]["text"] = tanka
        self.mainframe_kos_list[culomn]["text"] = kos
        self.mainframe_kingaku_list[culomn]["text"] = kingaku

        
        
        if culomn%7 == 0:
            command = lambda:[self.lists.pop(0+self.page*7),self.window.destroy(),pos.show_update(),pos.cash()]
            self.mainframe_gyou_list[culomn]["command"] =   command
            self.mainframe_name_list[culomn]["command"] =   command
            self.mainframe_tanka_list[culomn]["command"] =  command
            self.mainframe_kos_list[culomn]["command"] =    command
            self.mainframe_kingaku_list[culomn]["command"] =command
        
        elif culomn%7 == 1:
            command = lambda:[self.lists.pop(1+self.page*7),self.window.destroy(),pos.show_update(),pos.cash()]
            self.mainframe_gyou_list[culomn]["command"] =   command
            self.mainframe_name_list[culomn]["command"] =   command
            self.mainframe_tanka_list[culomn]["command"] =  command
            self.mainframe_kos_list[culomn]["command"] =    command
            self.mainframe_kingaku_list[culomn]["command"] =command
        
        elif culomn%7 == 2:
            command = lambda:[self.lists.pop(2+self.page*7),self.window.destroy(),pos.show_update(),pos.cash()]
            self.mainframe_gyou_list[culomn]["command"] =   command
            self.mainframe_name_list[culomn]["command"] =   command
            self.mainframe_tanka_list[culomn]["command"] =  command
            self.mainframe_kos_list[culomn]["command"] =    command
            self.mainframe_kingaku_list[culomn]["command"] =command
        
        elif culomn%7 == 3:
            command = lambda:[self.lists.pop(3+self.page*7),self.window.destroy(),pos.show_update(),pos.cash()]
            self.mainframe_gyou_list[culomn]["command"] =   command
            self.mainframe_name_list[culomn]["command"] =   command
            self.mainframe_tanka_list[culomn]["command"] =  command
            self.mainframe_kos_list[culomn]["command"] =    command
            self.mainframe_kingaku_list[culomn]["command"] =command
        
        elif culomn%7 == 4:
            command = lambda:[self.lists.pop(4+self.page*7),self.window.destroy(),pos.show_update(),pos.cash()]
            self.mainframe_gyou_list[culomn]["command"] =   command
            self.mainframe_name_list[culomn]["command"] =   command
            self.mainframe_tanka_list[culomn]["command"] =  command
            self.mainframe_kos_list[culomn]["command"] =    command
            self.mainframe_kingaku_list[culomn]["command"] =command
        
        elif culomn%7 == 5:
            command = lambda:[self.lists.pop(5+self.page*7),self.window.destroy(),pos.show_update(),pos.cash()]
            self.mainframe_gyou_list[culomn]["command"] =   command
            self.mainframe_name_list[culomn]["command"] =   command
            self.mainframe_tanka_list[culomn]["command"] =  command
            self.mainframe_kos_list[culomn]["command"] =    command
            self.mainframe_kingaku_list[culomn]["command"] =command
        
        elif culomn%7 == 6:
            command = lambda:[self.lists.pop(6+self.page*7),self.window.destroy(),pos.show_update(),pos.cash()]
            self.mainframe_gyou_list[culomn]["command"] =   command
            self.mainframe_name_list[culomn]["command"] =   command
            self.mainframe_tanka_list[culomn]["command"] =  command
            self.mainframe_kos_list[culomn]["command"] =    command
            self.mainframe_kingaku_list[culomn]["command"] =command
        
    def show_update(self,page):
        self.reset()
        self.lists = pos.show_info_list
        for i in range(7*page,min(7*(page+1),len(self.lists))):
            prod_info = self.lists[i][-1]
            self.info_input(i%7,i+1,prod_info.prev_name(),prod_info.prev_price(),len(self.lists[i]),prod_info.prev_price()*len(self.lists[i]))
        self.page_button.pagelbl["text"] = str(self.latest_page+1) + "/" + str(self.latest_page+1)
        
    def page_up(self,page):
        self.page = page
        self.show_update(page)
        
        if page == 0:
            self.page_button.page_bt_up["state"] = DISABLED
        else:
            self.page_button.page_bt_up["state"] = NORMAL
            self.page_button.page_bt_up["fg"] = "#228b22"
            self.page_button.page_bt_up["command"] = lambda:[self.page_up(page-1)]
        
        self.page_button.page_bt_dw["state"] = NORMAL
        self.page_button.page_bt_dw["fg"] = "#228b22"
        self.page_button.page_bt_dw["command"] = lambda:[self.page_dw(page+1)]
        
        self.page_button.pagelbl["text"] = str(page+1) + "/" + str(self.latest_page+1)
        
    
    def page_dw(self,page):
        self.page = page
        self.show_update(page)

        if page == self.latest_page:
            self.page_button.page_bt_dw["state"] = DISABLED
        else:
            self.page_button.page_bt_dw["state"] = NORMAL
            self.page_button.page_bt_dw["fg"] = "#228b22"
            self.page_button.page_bt_dw["command"] = lambda:[self.page_dw(page+1)]
        
        self.page_button.page_bt_up["state"] = NORMAL
        self.page_button.page_bt_up["fg"] = "#228b22"
        self.page_button.page_bt_up["command"] = lambda:[self.page_up(page-1)]
        
        self.page_button.pagelbl["text"] = str(page+1) + "/" + str(self.latest_page+1)

class Cfms_saleachieve(Cfms_defalut_window):
    def __init__(self, title) -> None:
        super().__init__(title)
    
    def create(self,kwargs):
        
        if len(all_sale_data.prev_all_data()) != 0:
            
            self.window = Toplevel()
            self.window.title(self.titles)
            
            self.title = Cfms_title_label(self.window,"販売実績",3)
            self.title()
            
            self.list1 = []
            self.list2 = []
            self.list3 = []
            
            self.sums = 0

            for i in range(len(all_sale_data.prev_all_data().keys())):
                if all_prod_info.infomation(list(all_sale_data.prev_all_data().keys())[i].prev_number()) != False and all_prod_info.infomation(list(all_sale_data.prev_all_data().keys())[i].prev_number()) == list(all_sale_data.prev_all_data().keys())[i]:
                    self.list1.append(Label(self.window,text=list(all_sale_data.prev_all_data().keys())[i].prev_name(),font=("HG創英角ｺﾞｼｯｸUB",17)))
                    self.list1[-1].grid(row=i+1,column=0, padx=5, pady=5,ipadx=7,ipady=7)
                else:
                    self.list1.append(Label(self.window,text=f"削除された商品 ( {list(all_sale_data.prev_all_data().keys())[i].prev_number()} )",font=("HG創英角ｺﾞｼｯｸUB",17),width=35))
                    self.list1[-1].grid(row=i+1,column=0, padx=5, pady=5,ipadx=7,ipady=7)
                
                self.qty = all_sale_data.prev_all_data()[list(all_sale_data.prev_all_data().keys())[i]]

                self.list2.append(Label(self.window,text=f"{self.qty} 個",font=("HG創英角ｺﾞｼｯｸUB",17),width=5))
                self.list2[-1].grid(row=i+1,column=1, padx=5, pady=5,ipadx=7,ipady=7)

                self.list2.append(Label(self.window,text=f"{self.qty*list(all_sale_data.prev_all_data().keys())[i].prev_price()} 円",font=("HG創英角ｺﾞｼｯｸUB",17),width=10))
                self.list2[-1].grid(row=i+1,column=2, padx=5, pady=5,ipadx=7,ipady=7)

                self.sums += self.qty*list(all_sale_data.prev_all_data().keys())[i].prev_price()
            
            self.sum_label = Label(self.window,text=f"合計 {self.sums} 円",font=("HG創英角ｺﾞｼｯｸUB",20),width=15)
            self.sum_label.grid(row=i+2,column=0,columnspan=3, padx=5, pady=5,ipadx=10,ipady=10)
        
        else:
            messagebox.showerror("未登録","販売実績がないため表示できません")

class Cfms_reseter(Cfms_defalut_window):

    def __init__(self, title) -> None:
        super().__init__(title)
    
    def create(self,kwargs):
        if simpledialog.askstring("リセット確認","続けるには「リセット」と入力して下さい。") == "リセット":
            self.window = Toplevel()
            self.window.title(self.titles)

            self.title = Cfms_title_label(self.window,"リセットオプション")
            self.title()

            self.reset_bt1 = Button(self.window,text="全リセット",font=("HG創英角ｺﾞｼｯｸUB",20),width=20,height=2,command=self.all_reset,bg="#ff0000",fg="#ffffff")
            self.reset_bt1.grid(row=1,column=0,padx=5,pady=5,ipadx=5,ipady=5)

            self.reset_bt2 = Button(self.window,text="販売情報リセット",font=("HG創英角ｺﾞｼｯｸUB",20),width=20,height=2,command=self.sale_reset,bg="#ff0000",fg="#ffffff")
            self.reset_bt2.grid(row=1,column=1,padx=5,pady=5,ipadx=5,ipady=5)
    
    def sale_reset(self):
        if messagebox.askyesno("最終確認","この操作は取り消せません。本当に続けますか？\n（販売実績がリセットされます）"):
            all_sale_data.reset()
            messagebox.showinfo("完了","販売実績をリセットしました。")
            self.window.destroy()
        else:
            self.window.destroy()
    def all_reset(self):
        if messagebox.askyesno("最終確認","この操作は取り消せません。本当に続けますか？\n（商品情報と販売実績がリセットされます）"):
            all_sale_data.reset()
            all_prod_info.reset()
            messagebox.showinfo("完了","すべてのデータをリセットしました。")
            self.window.destroy()
        else:
            self.window.destroy()

class Cfms_view_sale_history(Cfms_defalut_TinT_window):
    def __init__(self, title, base_window_class) -> None:
        super().__init__(title, base_window_class)
    
    def create(self):
        self.window = Toplevel()
        self.window.title(self.titles)
        
        self.data = self.kwargs["data"].sale_data
        self.info = self.kwargs["data"]
        
        
        
        self.list1 = []
        self.list2 = []
        self.list3 = []
        
        self.sums = 0

        for i,x in enumerate(all_sale_data.sale_datas):
            if x == self.info:
                self.index = i + 1
        
        self.title = Cfms_title_label(self.window,"販売実績 No. {:05}".format(self.index),3)
        self.title()



        for i in range(len(self.data)):
            if all_prod_info.infomation(self.data[i][-1].prev_number()) != False and all_prod_info.infomation(self.data[i][-1].prev_number()) == self.data[i][-1]:
                self.list1.append(Label(self.window,text=self.data[i][-1].prev_name(),font=("HG創英角ｺﾞｼｯｸUB",15)))
                self.list1[-1].grid(row=i+1,column=0, padx=5, pady=5,ipadx=5,ipady=5)
            else:
                self.list1.append(Label(self.window,text=f"削除された商品 ( {self.data[i][-1].prev_number()} )",font=("HG創英角ｺﾞｼｯｸUB",15),width=35))
                self.list1[-1].grid(row=i+1,column=0, padx=5, pady=5,ipadx=5)
            
            self.qty = len(self.data[i])

            self.list2.append(Label(self.window,text=f"{self.qty} 個",font=("HG創英角ｺﾞｼｯｸUB",17),width=5))
            self.list2[-1].grid(row=i+1,column=1, padx=5, pady=5,ipadx=5,ipady=5)

            self.list2.append(Label(self.window,text=f"{self.qty*self.data[i][-1].prev_price()} 円",font=("HG創英角ｺﾞｼｯｸUB",15),width=10))
            self.list2[-1].grid(row=i+1,column=2, padx=5, pady=5,ipadx=5,ipady=5)

            self.sums += self.qty*self.data[i][-1].prev_price()

        self.cach_frame = Frame(self.window)
        self.cach_frame.grid(row=i+2,column=0,columnspan=3, padx=5)
        
        self.sum_label = Label(self.cach_frame,text=f"合計 {self.sums} 円",font=("HG創英角ｺﾞｼｯｸUB",17),width=15,justify="center")
        self.sum_label.grid(row=0,column=0, padx=5, pady=5,ipadx=5,ipady=10)
        
        self.cash_label1 = Label(self.cach_frame,text=f"預金 {self.info.cash} 円",font=("HG創英角ｺﾞｼｯｸUB",17),width=20,justify="center")
        self.cash_label1.grid(row=0,column=1, padx=5, pady=5,ipadx=5,ipady=10)

        self.change_label1 = Label(self.cach_frame,text=f"釣銭 {self.info.cash-self.sums} 円",font=("HG創英角ｺﾞｼｯｸUB",17),width=20,justify="center")
        self.change_label1.grid(row=0,column=2, padx=5, pady=5,ipadx=5,ipady=10)


        times = self.info.datetime
        self.date_label1 = Label(self.window,text="日時 {:04}年 {:02}月{:02}日 {:02}時{:02}分".format(times.year,times.month,times.day,times.hour,times.minute),font=("HG創英角ｺﾞｼｯｸUB",13),width=30)
        self.date_label1.grid(row=i+3,column=0,columnspan=3, padx=5)

class Cfms_select_sale_history(Cfms_defalut_window):

    def __init__(self, title, info, tint_class, tint_info, category:str, color:str,) -> None:
        super().__init__(title)
        self.NUMBER = 6
        self.info = info
        self.category = category
        self.color = color
        self.cmd = tint_class(tint_info,self)
        
    
    def create(self,kwargs):
        
        if len(self.info.sale_datas) != 0:
            self.window = Toplevel()
            self.window.title(self.titles)

            self.title = Cfms_title_label(self.window,"販売履歴一覧",4)
            self.title()
            
            self.main_farame = Frame(self.window)
            self.main_farame.grid(row=1,column=1,rowspan=int(self.NUMBER/2),columnspan=2)
            self.bt_create()
        else:
            messagebox.showerror("未登録",f"{self.category}情報がないため表示できません。")

    def bt_create(self):
        self.page = 0
        self.bg = self.color
        self.bt_list = []
        
        self.list_update(self.page)
        
        for i in range(len(self.info_list)):
            
            if i%self.NUMBER == 0:
                self.bt0 = Button(self.main_farame,text="No. {:05}".format(i+1),font=("HG創英角ｺﾞｼｯｸUB",15),height=5,width=30,command=lambda:[self.cmd(data=self.info_list[0])],bg=self.bg,fg="#000000",bd=5)
                self.bt0.grid(row=i//2,column=i%2, padx=5, pady=5)
                self.bt_list.append(self.bt0)
            elif i%self.NUMBER == 1:
                self.bt1 = Button(self.main_farame,text="No. {:05}".format(i+1),font=("HG創英角ｺﾞｼｯｸUB",15),height=5,width=30,command=lambda:[self.cmd(data=self.info_list[1])],bg=self.bg,fg="#000000",bd=5)
                self.bt1.grid(row=i//2,column=i%2, padx=5, pady=5)
                self.bt_list.append(self.bt1)
                
            elif i%self.NUMBER == 2:
                self.bt2 = Button(self.main_farame,text="No. {:05}".format(i+1),font=("HG創英角ｺﾞｼｯｸUB",15),height=5,width=30,command=lambda:[self.cmd(data=self.info_list[2])],bg=self.bg,fg="#000000",bd=5)
                self.bt2.grid(row=i//2,column=i%2, padx=5, pady=5)
                self.bt_list.append(self.bt2)
                
            elif i%self.NUMBER == 3:
                self.bt3 = Button(self.main_farame,text="No. {:05}".format(i+1),font=("HG創英角ｺﾞｼｯｸUB",15),height=5,width=30,command=lambda:[self.cmd(data=self.info_list[3])],bg=self.bg,fg="#000000",bd=5)
                self.bt3.grid(row=i//2,column=i%2, padx=5, pady=5)
                self.bt_list.append(self.bt3)
                                
            elif i%self.NUMBER == 4:
                self.bt4 = Button(self.main_farame,text="No. {:05}".format(i+1),font=("HG創英角ｺﾞｼｯｸUB",15),height=5,width=30,command=lambda:[self.cmd(data=self.info_list[4])],bg=self.bg,fg="#000000",bd=5)
                self.bt4.grid(row=i//2,column=i%2, padx=5, pady=5) 
                self.bt_list.append(self.bt4)
                
            elif i%self.NUMBER == 5:
                self.bt5 = Button(self.main_farame,text="No. {:05}".format(i+1),font=("HG創英角ｺﾞｼｯｸUB",15),height=5,width=30,command=lambda:[self.cmd(data=self.info_list[5])],bg=self.bg,fg="#000000",bd=5)
                self.bt5.grid(row=i//2,column=i%2, padx=5, pady=5)
                self.bt_list.append(self.bt5)
                

            
        self.left_button = Button(self.window,text="◀",height=10,width=5,state=DISABLED,bd=5)
        self.left_button.grid(row=1,column=0,rowspan=3, padx=5, pady=5)
        if len(self.info.sale_datas) > self.NUMBER:
            for i,x in enumerate(self.info.sale_datas):
                print(i,x.cash)
            self.right_button = Button(self.window,text="▶",height=10,width=5,command=lambda:[self.right_bt(1)],bd=5)
            self.right_button.grid(row=1,column=3,rowspan=3, padx=5, pady=5)
            self.right_button["fg"] = "#32cd32"

            self.left_button.destroy()
            self.left_button = Button(self.window,text="◀",height=10,width=5,state=DISABLED,bd=5)
            self.left_button.grid(row=1,column=0,rowspan=4, padx=5, pady=5)
            self.page_frame = Frame(self.main_farame)
            self.page_frame.grid(row=4,column=0,columnspan=2, padx=5, pady=5)
            self.page_entry = Entry(self.page_frame,font=("HG創英角ｺﾞｼｯｸUB",20),width=3,justify="center")
            self.page_entry.grid(row=0,column=0, padx=5, pady=5,sticky=E)
            self.page_entry.bind("<Return>",self.page_move)
            self.page_label = Label(self.page_frame,text=f"/ {ceil(len(self.info.sale_datas)/self.NUMBER)}",font=("HG創英角ｺﾞｼｯｸUB",20))
            self.page_label.grid(row=0,column=1, padx=5, pady=5,sticky=W)
            self.page_entry.delete("0","end")
            self.page_entry.insert("0",str(self.page+1))

        else:
            self.right_button = Button(self.window,text="▶",height=10,width=5,state=DISABLED,bd=5)
            self.right_button.grid(row=1,column=3,rowspan=3)
            self.right_button["fg"] = "#000000"

    def right_bt(self,page):
        self.page = page
        self.list_update(page)

        for i in self.bt_list:
            i["text"] = ""
            i["state"] = DISABLED

        for i in range(len(self.info_list)):
            self.text = i+self.page*self.NUMBER+1
            if i%self.NUMBER == 0:
                self.bt0["state"] = NORMAL
                self.bt0["text"] = "No. {:05}".format(self.text)
                self.bt0["command"] = lambda:[self.cmd(data=self.info_list[0])]
            elif i%self.NUMBER == 1:
                self.bt1["state"] = NORMAL
                self.bt1["text"] = "No. {:05}".format(self.text)
                self.bt1["command"] = lambda:[self.cmd(data=self.info_list[1])]
            elif i%self.NUMBER == 2:
                self.bt2["state"] = NORMAL
                self.bt2["text"] = "No. {:05}".format(self.text)
                self.bt2["command"] = lambda:[self.cmd(data=self.info_list[2])]
            elif i%self.NUMBER == 3:
                self.bt3["state"] = NORMAL
                self.bt3["text"] = "No. {:05}".format(self.text)
                self.bt3["command"] = lambda:[self.cmd(data=self.info_list[3])]
            elif i%self.NUMBER == 4:
                self.bt4["state"] = NORMAL
                self.bt4["text"] = "No. {:05}".format(self.text)
                self.bt4["command"] = lambda:[self.cmd(data=self.info_list[4])]      
            elif i%self.NUMBER == 5:
                self.bt5["state"] = NORMAL
                self.bt5["text"] = "No. {:05}".format(self.text)
                self.bt5["command"] = lambda:[self.cmd(data=self.info_list[5])]
        
        self.left_button["command"]= lambda:[self.left_bt(page-1)]
        self.left_button["fg"] = "#32cd32"
        self.left_button["state"]=NORMAL

        if len(self.info.sale_datas) > self.NUMBER * (page+1):
            self.right_button["command"]=lambda:[self.right_bt(page+1)]
            self.right_button["fg"] = "#32cd32"
            self.right_button["state"]=NORMAL
        

        else:
            self.right_button["state"]=DISABLED
            self.right_button["fg"] = "#000000"

        self.page_entry.delete("0","end")
        self.page_entry.insert("0",str(self.page+1))

    def left_bt(self,page):
        self.page = page
        self.list_update(page)

        for i in self.bt_list:
            i["text"] = ""
            i["state"] = NORMAL

        for i in range(len(self.info_list)):
            self.text = i+self.page*self.NUMBER+1
            if i%self.NUMBER == 0:
                self.bt0["text"] = "No. {:05}".format(self.text)
                self.bt0["command"] = lambda:[self.cmd(data=self.info_list[0])]
            elif i%self.NUMBER == 1:
                self.bt1["text"] = "No. {:05}".format(self.text)
                self.bt1["command"] = lambda:[self.cmd(data=self.info_list[1])]
            elif i%self.NUMBER == 2:
                self.bt2["text"] = "No. {:05}".format(self.text)
                self.bt2["command"] = lambda:[self.cmd(data=self.info_list[2])]
            elif i%self.NUMBER == 3:
                self.bt3["text"] = "No. {:05}".format(self.text)
                self.bt3["command"] = lambda:[self.cmd(data=self.info_list[3])]
            elif i%self.NUMBER == 4:
                self.bt4["text"] = "No. {:05}".format(self.text)
                self.bt4["command"] = lambda:[self.cmd(data=self.info_list[4])]      
            elif i%self.NUMBER == 5:
                self.bt5["text"] = "No. {:05}".format(self.text)
                self.bt5["command"] = lambda:[self.cmd(data=self.info_list[5])]
        
        self.right_button["command"]=lambda:[self.right_bt(page+1)]
        self.right_button["fg"] = "#32cd32"
        self.right_button["state"]=NORMAL
        if page > 0:
            self.left_button["command"]=lambda:[self.left_bt(page-1)]
            self.left_button["fg"] = "#32cd32"
            self.left_button["state"]=NORMAL


        else:
            self.left_button["state"]=DISABLED
            self.left_button["fg"] = "#000000"
        
        self.page_entry.delete("0","end")
        self.page_entry.insert("0",str(self.page+1))


    def list_update(self,page):
        self.info_list = []
        for i in range(page*self.NUMBER,min((page+1)*self.NUMBER,len(self.info.sale_datas))):
            self.info_list.append(self.info.sale_datas[i])
    
    
    def page_move(self,event):
        self.page = min(max(int(self.page_entry.get()),1),ceil(len(self.info.sale_datas)/self.NUMBER)) - 1 

        self.list_update(self.page)

        for i in self.bt_list:
            i["text"] = ""
            i["state"] = DISABLED

        for i in range(len(self.info_list)):
            self.text = i+self.page*self.NUMBER+1
            if i%self.NUMBER == 0:
                self.bt0["state"] = NORMAL
                self.bt0["text"] = "No. {:05}".format(self.text)
                self.bt0["command"] = lambda:[self.cmd(data=self.info_list[0])]
            elif i%self.NUMBER == 1:
                self.bt1["state"] = NORMAL
                self.bt1["text"] = "No. {:05}".format(self.text)
                self.bt1["command"] = lambda:[self.cmd(data=self.info_list[1])]
            elif i%self.NUMBER == 2:
                self.bt2["state"] = NORMAL
                self.bt2["text"] = "No. {:05}".format(self.text)
                self.bt2["command"] = lambda:[self.cmd(data=self.info_list[2])]
            elif i%self.NUMBER == 3:
                self.bt3["state"] = NORMAL
                self.bt3["text"] = "No. {:05}".format(self.text)
                self.bt3["command"] = lambda:[self.cmd(data=self.info_list[3])]
            elif i%self.NUMBER == 4:
                self.bt4["state"] = NORMAL
                self.bt4["text"] = "No. {:05}".format(self.text)
                self.bt4["command"] = lambda:[self.cmd(data=self.info_list[4])]      
            elif i%self.NUMBER == 5:
                self.bt5["state"] = NORMAL
                self.bt5["text"] = "No. {:05}".format(self.text)
                self.bt5["command"] = lambda:[self.cmd(data=self.info_list[5])]
        
        if self.page > 0:
            self.left_button["command"]=lambda:[self.left_bt(self.page-1)]
            self.left_button["fg"] = "#32cd32"
            self.left_button["state"]=NORMAL


        else:
            self.left_button["state"]=DISABLED
            self.left_button["fg"] = "#000000"
        
        if len(self.info.sale_datas) > self.NUMBER * (self.page+1):
            self.right_button["command"]=lambda:[self.right_bt(self.page+1)]
            self.right_button["fg"] = "#32cd32"
            self.right_button["state"]=NORMAL
        

        else:
            self.right_button["state"]=DISABLED
            self.right_button["fg"] = "#000000"
        
        self.page_entry.delete("0","end")
        self.page_entry.insert("0",str(self.page+1))

#実体生成---------------------------------------------------------------------------------------------------------------------------#

shop_files = CFMS_file("cfms_shop.pickle")

hq_files = CFMS_file("cfms_hq.pickle")

#データ管理
datas = CFMS_data()

#商品情報管理
all_prod_info = CFMS_all_prod_info()

#販売実績
all_sale_data = CFMS_all_sale_data()

#商品情報入力
prod_info_entry_window = Cfms_shop_prod_entry("商品情報入力画面")

#商品情報閲覧画面
prod_info_prev_window = Cfms_prod_info_select("商品情報閲覧画面",all_prod_info,Cfms_prod_info_view,"商品情報","商品","#1e90ff")

#商品手動選択
prod_select_window = Cfms_prod_select("商品選択画面",all_prod_info,CFMS_inserter,None,"商品","#ffa500")

#商品訂正
drop_sale_prod_window = Cfms_drop_sale_prod("商品訂正画面")

#販売実績
sale_achieve_window = Cfms_saleachieve("販売実績画面")

#販売履歴
sale_history_window = Cfms_select_sale_history("販売履歴閲覧画面",all_sale_data,Cfms_view_sale_history,"販売詳細情報","販売実績","#c1ffc1")

#リセット
reseter = Cfms_reseter("リセット画面")

#復旧LIST
revert_data_list = [all_prod_info,all_sale_data]

#-----------------------------------------------------------------------------------------------------------------------------------#

#読み込み------------------------------------------------------------------------------------------------------------------------#


if datas.shop_revert(): #データ読み込み
    for i in revert_data_list:
        i.revert(datas.revert_data(type(i).__name__))
#-----------------------------------------------------------------------------------------------------------------------------------#

#メインウィンドウ生成-----------------------------------------------------------------------------------------------------------------#
logo=temp_path('CFMSicon.ico')
cfms_main_window = Tk()
cfms_main_window.title("CFMS-2022")
cfms_main_window.resizable(False, False)
# cfms_main_window.iconbitmap(default=logo)

#-----------------------------------------------------------------------------------------------------------------------------------#

#タイマー----------------------------------------------------------------------------------------------------------------------------#

class Timer:
    
    def __init__(self,cfms_main_window) -> None:

        timer_canvas = Canvas(master= cfms_main_window, width=130, height=80)
        timer_canvas.grid(row=0,column=0)

        def timer():
            while cfms_main_window.winfo_exists():
                    
                    ### 現在時刻取得
                
                    now = datetime.datetime.now()


                    ### 時刻設定
                    week = {0:"月",1:"火",2:"水",3:"木",4:"金",5:"土",6:"日"}
                    
                    tm = "{:02}月{:02}日\n({})\n{:02}:{:02}".format(now.month,now.day,week[now.weekday()],now.hour, now.minute)



                    ### キャンバス初期化

                    timer_canvas.delete("all")


                    ### キャンバスに時刻表示
                    timer_canvas.create_text(70,42, text=tm, font=("HG創英角ｺﾞｼｯｸUB",15),justify=tk.CENTER)

                    time.sleep(1)

        timer_thread = threading.Thread(target=timer,daemon=True)
        timer_thread.start()
timer = Timer(cfms_main_window)
#-----------------------------------------------------------------------------------------------------------------------------------#

#ホーム画面上部GUI-------------------------------------------------------------------------------------------------------------------#

class Home_top_gui(Frame):

    def __init__(self) -> None:
        super().__init__(master=None)
        
        self.vcmd = self.register(self.onValidate)

        #商品スキャン：
        self.main_Explanation_lbl_1 = Label(cfms_main_window, text="商品スキャン", font=("HG創英角ｺﾞｼｯｸUB", 20) )
        self.main_Explanation_lbl_1.grid(row= 0, column= 1)
        self.main_Explanation_lbl_1["fg"] = "#228b22"

        #スキャン用Entry
        self.main_Explanation_entry_1 = Entry(cfms_main_window, font=("HG創英角ｺﾞｼｯｸUB",25), validate="key", width=12, bd=3,validatecommand=(self.vcmd, '%S'), invalidcommand=self.invalidText)
        self.main_Explanation_entry_1.grid(row= 0, column=2)
        self.main_Explanation_entry_1.bind("<Return>",self.entry)
        self.main_Explanation_entry_1.focus_set()

        #説明用ラベル
        self.main_Explanation_lbl_2 = Label(cfms_main_window , text="左の入力ボックスを選択した状態で商品をスキャンしてください。\nお預かり金額を入力後会計ボタンを押してください。"
        ,font=("HG創英角ｺﾞｼｯｸUB",15),justify=tk.LEFT, width=60, height=3)
        self.main_Explanation_lbl_2.grid(row= 0, column=3)
        self.main_Explanation_lbl_2["bg"] = "#c9c9c9"

        #線
        self.style = ttk.Style()
        self.style.configure("red.TSeparator", background="red")
        self.style.configure("green.TSeparator", background="green")
        self.style.configure("orange.TSeparator", background="orange")

        SPAN = 5
        self.green1 = ttk.Separator(cfms_main_window , style="green.TSeparator" , orient = HORIZONTAL)
        self.green1.grid(row=1,column=0,columnspan=SPAN, pady=0 ,sticky="ew")
        self.green2 = ttk.Separator(cfms_main_window , style="green.TSeparator" , orient = HORIZONTAL)
        self.green2.grid(row=2,column=0,columnspan=SPAN, pady=0 ,sticky="ew")

        self.orange1 = ttk.Separator(cfms_main_window , style="orange.TSeparator" , orient = HORIZONTAL)
        self.orange1.grid(row=3,column=0,columnspan=SPAN , sticky="ew")
        self.orange2 = ttk.Separator(cfms_main_window , style="orange.TSeparator" , orient = HORIZONTAL)
        self.orange2.grid(row=4,column=0,columnspan=SPAN , sticky="ew")

    def entry_focus(self):

        self.main_Explanation_entry_1.focus_set()
    
    def entry_delete(self):

        self.main_Explanation_entry_1.delete(0,"end")
    
    def entry(self,event):
        
        self.prod_number = unicodedata.normalize("NFKC",self.main_Explanation_entry_1.get())
        self.main_Explanation_entry_1.delete(0,"end")
        pos(self.prod_number)
    
    def invalidText(self):
        messagebox.showwarning("入力値エラー","入力設定が全角になっています。\n半角入力に切り替えてください。")
        self.main_Explanation_entry_1.destroy()
        self.main_Explanation_entry_1 = Entry(cfms_main_window, font=("HG創英角ｺﾞｼｯｸUB",25), validate="key", width=12, bd=3,validatecommand=(self.vcmd, '%S'), invalidcommand=self.invalidText)
        self.main_Explanation_entry_1.grid(row= 0, column=2)
        self.main_Explanation_entry_1.bind("<Return>",self.entry)
        self.main_Explanation_entry_1.focus_set()
    
    def onValidate(self, S):
        try:
            ret = unicodedata.east_asian_width(S) 
        except:
            return True
        
        if ret == "F":
            return False
        else:
            return True
home_top_gui = Home_top_gui()#実態生成 画面生成

#-----------------------------------------------------------------------------------------------------------------------------------#

#レジ画面メインフレーム--------------------------------------------------------------------------------------------------------------#

class Mine_farme:
    def __init__(self) -> None:
        
        self.mainframe = Frame(cfms_main_window)
        self.mainframe.grid(row=5,column=0,rowspan=7,columnspan=5)

mainframe = Mine_farme() #実態生成

class Main_info:
    
    def __init__(self) -> None:


        #列見出し
        self.main_frame_main_info_list = []

        self.main_frame_main_info_defalut_info = {"font":("HG創英角ｺﾞｼｯｸUB",15), "height":BASE_H, "borderwidth" : 1, "relief":"sunken", "bg":"#c9c9c9"}

        self.main_frame_main_info_width_list = [
                                            {"width" : 7},
                                            {"width" : 45},
                                            {"width" : 20},
                                            {"width" : 10},
                                            {"width" : 20},
                                            {"width" : 10},
                                        ]

        self.main_frame_main_info_text_list = [
                                            {"text" : "行"},
                                            {"text" : "商品名"},
                                            {"text" : "単価"},
                                            {"text" : "数量"},
                                            {"text" : "金額"},
                                            {"text" : ""},                                    
                                        ]

        NUMBER = 6

        for i in range(NUMBER):
            cnf = {}
            cnf.update(self.main_frame_main_info_defalut_info)
            cnf.update(self.main_frame_main_info_width_list[i])
            cnf.update(self.main_frame_main_info_text_list[i])
            
            self.main_frame_main_info_list.append(Label(mainframe.mainframe,cnf = cnf))

        for i in range(NUMBER):
            self.main_frame_main_info_list[i].grid(row=0,column=i,sticky=W)


        #商品情報表示label基本情報

        mainframe_lbl_defalut_info = {"font":("HG創英角ｺﾞｼｯｸUB",15), "height":BASE_H, "borderwidth" : 1, "relief":"sunken"}

        self.CULOMNS_NUMBER = 7 #段数
        ##行

        self.gyou_info = {"width":7}
        self.gyou_info.update(mainframe_lbl_defalut_info)
        self.mainframe_gyou_list =[]

        for i in range(self.CULOMNS_NUMBER):
            self.mainframe_gyou_list.append(Label(mainframe.mainframe,cnf=self.gyou_info))



        ##商品名

        self.name_info = {"width":45}
        self.name_info.update(mainframe_lbl_defalut_info)
        self.mainframe_name_list =[]

        for i in range(self.CULOMNS_NUMBER):
            self.mainframe_name_list.append(Label(mainframe.mainframe,cnf=self.name_info))


        ##単価

        self.tanka_info = {"width":20}
        self.tanka_info.update(mainframe_lbl_defalut_info)
        self.mainframe_tanka_list =[]


        for i in range(self.CULOMNS_NUMBER):
            self.mainframe_tanka_list.append(Label(mainframe.mainframe,cnf=self.tanka_info))

        ##個数

        self.kos_info = {"width":10}
        self.kos_info.update(mainframe_lbl_defalut_info)
        self.mainframe_kos_list =[]


        for i in range(self.CULOMNS_NUMBER):
            self.mainframe_kos_list.append(Label(mainframe.mainframe,cnf=self.kos_info))

        ##金額

        self.kingaku_info = {"width":20}
        self.kingaku_info.update(mainframe_lbl_defalut_info)
        self.mainframe_kingaku_list =[]

        for i in range(self.CULOMNS_NUMBER):
            self.mainframe_kingaku_list.append(Label(mainframe.mainframe,cnf=self.kingaku_info))

        ###生成

        for i in range(self.CULOMNS_NUMBER):
            
            self.mainframe_gyou_list[i].grid(row= 1 + i, column= 0, sticky=W)
            self.mainframe_name_list[i].grid(row= 1 + i, column= 1, sticky=W)
            self.mainframe_tanka_list[i].grid(row= 1 + i, column= 2, sticky=W)
            self.mainframe_kos_list[i].grid(row= 1 + i, column= 3, sticky=W)
            self.mainframe_kingaku_list[i].grid(row= 1 + i, column= 4, sticky=W)
    
    def reset(self):
        
        for i in range(self.CULOMNS_NUMBER):
            self.mainframe_gyou_list[i]["text"] = ""
            self.mainframe_name_list[i]["text"] = ""
            self.mainframe_tanka_list[i]["text"] = ""
            self.mainframe_kos_list[i]["text"] = ""
            self.mainframe_kingaku_list[i]["text"] = ""
    
    def info_input(self, culomn:int, gyou:int, name:str, tanka:int, kos:int, kingaku:int):
        
        self.mainframe_gyou_list[culomn]["text"] = gyou
        self.mainframe_name_list[culomn]["text"] = name
        self.mainframe_tanka_list[culomn]["text"] = tanka
        self.mainframe_kos_list[culomn]["text"] = kos
        self.mainframe_kingaku_list[culomn]["text"] = kingaku
    
    def info_count_change(self, culomn:int, kos:int, kingaku:int):
        
        self.mainframe_kos_list[culomn]["text"] =  kos
        self.mainframe_kingaku_list[culomn]["text"] = kingaku*kos


#-----------------------------------------------------------------------------------------------------------------------------------#

#レジ画面ページフレーム--------------------------------------------------------------------------------------------------------------#

class Page_frame:
    
    def __init__(self,window):
        self.page_frame = Frame(window)
        self.page_frame.grid(row=1,column=5,rowspan=7)

        self.page_bt_up = Button(self.page_frame,text="▲",font=("HG創英角ｺﾞｼｯｸUB",20))
        self.page_bt_up.grid(row=0,column=0,rowspan=3)
        self.page_bt_up["state"] = DISABLED

        self.pagelbl = Label(self.page_frame,text="1/1",font=("HG創英角ｺﾞｼｯｸUB",20))
        self.pagelbl.grid(row=4,column=0)
        self.pagelbl["fg"] = "#228b22"

        self.page_bt_dw = Button(self.page_frame,text="▼",font=("HG創英角ｺﾞｼｯｸUB",20))
        self.page_bt_dw.grid(row=5,column=0,rowspan=3)
        self.page_bt_dw["state"] = DISABLED


#----------------------------------------------------------------------------------------------------------------------------------#

#サブフレーム-----------------------------------------------------------------------------------------------------------------------#

class Sub_frame:
    
    def __init__(self) -> None:
        
        self.subframe = Frame(cfms_main_window)
        self.subframe.grid(row=13,column=0,columnspan=5,sticky=EW)

subframe = Sub_frame() #実態生成 画面生成

#----------------------------------------------------------------------------------------------------------------------------------#
#会計フレーム-----------------------------------------------------------------------------------------------------------------------#

class Cache_frame:
    
    def __init__(self) -> None:
        
        self.cache_frame = Frame(subframe.subframe)
        self.cache_frame.grid(row=0,column=3,columnspan=2,rowspan=3,sticky=EW)
        
        self.cache_title_lbl_list = []

        self.cache_title_lbl_defalut_info = {"font":("HG創英角ｺﾞｼｯｸUB",20),"height":2,"width":10}

        self.cache_title_lbl_text_lists = [
                                        {"text":"合計"},
                                        {"text":"お預かり"},
                                        {"text":"お釣り"},
                                    ]

        NUMBER = 3

        for i in range(NUMBER):
            cnf = {}
            cnf.update(self.cache_title_lbl_defalut_info)
            cnf.update(self.cache_title_lbl_text_lists[i])
            self.cache_title_lbl_list.append(Label(self.cache_frame,cnf= cnf))

        for i in range(NUMBER):
            self.cache_title_lbl_list[i].grid(row=i,column=0,padx=3,sticky=E)



        self.cache_frame_total_lbl = Label(self.cache_frame,text="0    円",font=("HG創英角ｺﾞｼｯｸUB",25),height=1,width=10)
        self.cache_frame_total_lbl.grid(row=0,column=1,padx=3)


        

        self.cache_frame_change_lbl = Label(self.cache_frame,text="0    円",font=("HG創英角ｺﾞｼｯｸUB",25),height=1,width=10)
        self.cache_frame_change_lbl.grid(row=2,column=1,padx=3)

    def show_price(self,price):
        
        self.cache_frame_total_lbl["text"] = str(price) + " 円"
    
    def price_reset(self):
        
        self.cache_frame_total_lbl["text"]  = "0 円"
    
    def show_change(self,change):
        
        self.cache_frame_change_lbl["text"] = str(change) + " 円"
    
    def change_reset(self):
        
        self.cache_frame_change_lbl["text"] = "0 円"

#----------------------------------------------------------------------------------------------------------------------------------#
#ボタンフレーム---------------------------------------------------------------------------------------------------------------------#

class Bt_frame:
    
    def __init__(self) -> None:
        
        self.bt_frame = Frame(subframe.subframe)
        self.bt_frame.grid(row=0,column=0,columnspan=2)
        self.bt_frame["bg"] = "#e0ffff"

        #メインボタン

        self.bt_frame_bt_list = []

        self.bt_defalut_info = {"font":("HG創英角ｺﾞｼｯｸUB",20),"width":9,"height":2, "bg":"#66cd00", "fg":"#fffafa"}
        self.bt_text_list = [
                        {"text":"商品登録"}, 
                        {"text":"商品情報"}, 
                        {"text":"販売実績"}, 
                        {"text":"販売履歴"}, 
                        {"text":None,"state":DISABLED}, 
                        ]
        self.bt_command_list = [
                        {"command":lambda:[prod_info_entry_window()]}, 
                        {"command":lambda:[prod_info_prev_window()]}, 
                        {"command":lambda:[sale_achieve_window()]}, 
                        {"command":lambda:[sale_history_window()]}, 
                        {"command":None}, 
                        ]

        self.bt_image_list = [
                        {"image":None}, 
                        {"image":None}, 
                        {"image":None}, 
                        {"image":None}, 
                        {"image":None}, #{"image":images.image('イラスト'),"width":130,"height":70}, 
                        ]


        NUMBER = 5

        for i in range(NUMBER):
            cnf = {}
            cnf.update(self.bt_defalut_info)
            cnf.update(self.bt_text_list[i])
            cnf.update(self.bt_command_list[i])
            cnf.update(self.bt_image_list[i])
            self.bt_frame_bt_list.append(Button(self.bt_frame,cnf=cnf))

        ##生成
        for i in range(0,10,2):
            self.bt_frame_bt_list[int(i/2)].grid(row=0,column=i,columnspan=2,padx=2,pady=2)
            self.bt_frame_bt_list[int(i/2)].config(bg="#fffafa")


        #サブボタン上段

        self.sub_bt_frame_bt_list1 = []

        #self.sub_bt_defalut_info1 = {"font":("HG創英角ｺﾞｼｯｸUB",12),"width":7,"height":3, "bg":"#ba55d3", "fg":"#fffafa"}
        self.sub_bt_defalut_info1 = {"font":("HG創英角ｺﾞｼｯｸUB",20),"width":9,"height":2, "bg":"#66cd00", "fg":"#fffafa"}
        
        self.sub_bt_text_list1 = [
                            {"text":"商品訂正","state":DISABLED}, 
                            {"text":"一括取消","state":DISABLED}, 
                            {"text":"商品選択",}, 
                            {"text":None,"state":DISABLED }, 
                            {"text":None,"state":DISABLED},  
                            # {"text":"キャンセル","font":("HG創英角ｺﾞｼｯｸUB",10),"width":8,"height":4,},  
                            # {"text":"呼出", "bg":"#ff0000", "state" : "disable"},  
                            # {"text":"", "state" : "disable"},  
                            # {"text":"", "state" : "disable"},  
                            # {"text":"", "state" : "disable"}, 
                            ]
        self.sub_bt_command_list1 = [
                            {"command":None}, #pos内でコマンド設定
                            {"command":None}, #pos内でコマンド設定
                            {"command":lambda:[prod_select_window()]}, 
                            {"command":None}, 
                            {"command":None}, 
                            # {"command":None}, 
                            # {"command":lambda:[checker(chanel, references, 0), calling()]}, #呼出し
                            # {"command":None}, 
                            # {"command":None}, 
                            # {"command":None}
                            ]
        #NUMBER = 10
        NUMBER = 5
        

        for i in range(NUMBER):
            cnf = {}
            cnf.update(self.sub_bt_defalut_info1)
            cnf.update(self.sub_bt_text_list1[i])
            cnf.update(self.sub_bt_command_list1[i])
            self.sub_bt_frame_bt_list1.append(Button(self.bt_frame,cnf=cnf))

        # for i in range(NUMBER):
        #     self.sub_bt_frame_bt_list1[i].grid(row=2,column=i,padx=1,pady=1)
        
                ##生成
        for i in range(0,10,2):
            self.sub_bt_frame_bt_list1[int(i/2)].grid(row=1,column=i,columnspan=2,padx=2,pady=2)

        #サブボタン下段

        self.sub_bt_frame_bt_list2 = []

        #self.sub_bt_defalut_info2 = {"font":("HG創英角ｺﾞｼｯｸUB",12),"width":7,"height":3, "bg":"#00bfff", "fg":"#fffafa"}
        self.sub_bt_defalut_info2 = {"font":("HG創英角ｺﾞｼｯｸUB",20),"width":9,"height":2, "bg":"#66cd00", "fg":"#fffafa"}
        
        self.sub_bt_text_list2 = [
                            {"text":None,"state":DISABLED}, 
                            {"text":None,"state":DISABLED}, 
                            {"text":None,"state":DISABLED}, 
                            {"text":None,"state":DISABLED}, 
                            {"text":"Reset","bg":"#ff4500"},  
                            # {"text":"Easy\nmode"},  
                            # {"text":"チャンネル", "font":("HG創英角ｺﾞｼｯｸUB",10),"width":8,"height":4,},  
                            # {"text":"", "state" : "disable"},  
                            # {"text":"", "state" : "disable"},  
                            # {"text":"", "state" : "disable"}, 
                            ]
        self.sub_bt_command_list2 = [
                            {"command":None}, 
                            {"command":None}, 
                            {"command":None}, 
                            {"command":None}, 
                            {"command":lambda:[reseter()]}, #LINE 
                            # {"command":None},#Easy mode 
                            # {"command":lambda:[chanel_window(cl=chanel,bt=self)]}, #チャンネル
                            # {"command":None}, 
                            # {"command":lambda:[server_window(cl=chanel, re=references)]}, 
                            # {"command":lambda:[line_window(cl=chanel, re=references)]}
                            ]

        #NUMBER = 10
        NUMBER = 5
        

        for i in range(NUMBER):
            cnf = {}
            cnf.update(self.sub_bt_defalut_info2)
            cnf.update(self.sub_bt_text_list2[i])
            cnf.update(self.sub_bt_command_list2[i])
            self.sub_bt_frame_bt_list2.append(Button(self.bt_frame,cnf=cnf))

        for i in range(0,10,2):
            self.sub_bt_frame_bt_list2[int(i/2)].grid(row=2,column=i,columnspan=2,padx=2,pady=2)
bt_frame = Bt_frame() #実態生成 画面生成

#----------------------------------------------------------------------------------------------------------------------------------#
copyrights = Label(subframe.subframe,text="©2022 Yohei Saito",font=("HG創英角ｺﾞｼｯｸUB",7))
copyrights.grid(row=0,column=6,sticky=SE)

pos = CFMS_pos(mainframe) #レジクラス生成 画面が生成された後じゃないと実体化できない為、生成後に実体生成
cfms_main_window.mainloop()