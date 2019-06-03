# -*- coding: utf-8 -*-


import tkinter as tk
from tkinter import font
import csv
from tkinter import filedialog
import re
from configparser import ConfigParser
import json
import xml.etree.ElementTree as ET
import lxml
import lxml.builder
import lxml.etree



class annotatorApp(tk.Tk):
    
    wordList = []
    relationDict = {}
    
    def __init__(self, *args, **kwargs):
        
        self.setting = ConfigParser()
        self.setting.read('config.ini')
        self.language=self.setting.get('general','language')
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("800x500+20+20")    
        self.grid()
        
        self.currentFamily = ''

        self.root = lxml.etree.Element("root")
        lxml.etree.SubElement(self.root, "head")
        lxml.etree.SubElement(self.root, "tags")
        lxml.etree.SubElement(self.root, "fulltext")
        
    
        self.textBoxMain = tk.Text()
        self.textBoxMain.grid(sticky ="nswe", column=0, row =1)
        self.textBoxMain.config(state="disabled")
        
        self.textBoxAnn = tk.Text(width = 8)
        self.textBoxAnn.grid(sticky ="nswe", column=1, row =1)
        self.textBoxAnn.config(state="disabled")
        
        self.opisBox = tk.Text(wrap="word")
        self.opisBox.grid(sticky ="nswe", column = 0, row = 2)
        self.opisBox.config(state = "disabled")
        
        self.family=True
        self.tags = ET.parse(self.setting.get(self.language,'tag_set_path')) 
        if  self.tags.find('family') is not None:
            names = [events.attrib['name'] for events in  self.tags.findall('family')]
            self.tagNameList = names
            self.tagList = tk.Listbox(width = 20, selectmode = "SINGLE", exportselection= False)
            for j in range(len(self.tagNameList)):
                self.tagList.insert(j, self.tagNameList[j])
            self.tagList.grid(row=1, column = 2, sticky = "wn")
            self.tagList.bind("<Double-Button-1>", self.taglist_callback)
        
        self.opisBox = tk.Text(wrap="word")
        self.opisBox.grid(sticky ="nswe", column = 0, row = 2)
        self.opisBox.config(state = "disabled")
        button_newAnn = tk.Button(text = self.setting.get(self.language,'new_annotation') , command = lambda: self.annotate(self.tagList.get(self.tagList.curselection()), \
        self.tags.find('./family[@name="'+ self.currentFamily +'"]/tag[name="'+self.tagList.get(self.tagList.curselection()) +'"]/tag_name').text, \
        self.tags.find('./family[@name="'+ self.currentFamily +'"]/tag[name="'+self.tagList.get(self.tagList.curselection()) +'"]/relation').attrib['type']))

        button_newAnn.grid(row=2, column = 2)
        
        menuBar = tk.Menu(self)   
        menuFile = tk.Menu(menuBar, tearoff = 0)
 #       menulanguage = tk.Menu(menuBar, tearoff = 1)

        menuBar.add_cascade(label =self.setting.get(self.language,'file'), menu = menuFile)
        menuFile.add_command(label=self.setting.get(self.language,'load'), command = lambda: self.load_file(self.wordList))
        menuFile.add_command(label=self.setting.get(self.language,'save'), command = lambda: self.save_file(self.root))      
    
# Jakbyśmy chcieli się powbawić w zmanę języka
#        menuBar.add_cascade(label = setting.get(language,'language') ,menu = menulanguage )
#        langueges_list = json.loads(setting.get(language,"languages"))
#        for key in langueges_list.keys():
#            if isinstance(langueges_list[key], dict)== False:
#                menulanguage.add_command(label = key, command= change_language(key)  )
       
       
        self.config(menu = menuBar)
        self.bind("<Delete>", lambda event: self.deletetag())
#    def change_language(self, key):
#        return
    def deletetag(self):
        if self.family or self.root.find('./head/tag[@name="'+self.tagList.get(self.tagList.curselection())+'"]') is None:
            return
        index = self.get_selected()
        self.textBoxMain.tag_remove(self.tags.find('family[@name="'+ self.currentFamily +'"]/tag[name="'+self.tagList.get(self.tagList.curselection())+'"]/tag_name').text,index[2],index[3])
        listOfEle= []
       
        for element in self.root.findall('./tags/tag[@name="'+self.tagList.get(self.tagList.curselection())+'"]'):
           if int(element.attrib['beginning'])<=index[0]:
               listOfEle.append(element)
        for tag in listOfEle:
            if int(tag.attrib['end'])>=index[1]:
                self.root.find('./tags').remove(tag)
                if int(self.root.find('./head/tag[@name="'+self.tagList.get(self.tagList.curselection())+'"]').attrib["amount"]) > 1:
                    self.root.find('./head/tag[@name="'+self.tagList.get(self.tagList.curselection())+'"]').attrib["amount"]=str(int(self.root.find('./head/tag[@name="'+self.tagList.get(self.tagList.curselection())+'"]').attrib["amount"])-1)
                else:
                    self.root.find('./head').remove(self.root.find('./head/tag[@name="'+self.tagList.get(self.tagList.curselection())+'"]'))
        
        
    def displey_tag(self,tag):
        for name in self.textBoxMain.tag_names():
            self.textBoxMain.tag_config(name , underline=0)
        self.textBoxMain.tag_config(self.tags.find('family[@name="'+ self.currentFamily +'"]/tag[name="'+tag+'"]/tag_name').text, underline=1)
            


    def taglist_callback(self, event):
        if(self.family):
            self.family=False
            name = self.tagList.get(self.tagList.curselection())
            self.tagList.delete(0,'end')
            self.tagList.insert(0,self.setting.get(self.language,'back'))
            self.currentFamily = name
            if self.tags.find('family[@name="'+ name +'"]/tag') is not None:
                names = [events for events in self.tags.findall('family[@name="'+ name +'"]/tag/name')]
                for j in range(len(names)):
                    self.tagList.insert(j+1, names[j].text)
            
        else:
            if self.tagList.curselection()[0]==0:
                self.family=True
                self.tagList.delete(0,'end')
                for j in range(len(self.tagNameList)):
                    self.tagList.insert(j, self.tagNameList[j])
            else:
                self.opisBox.config(state = "normal")
                opis = self.tags.find('./family[@name="'+ self.currentFamily +'"]/tag[name="'+self.tagList.get(self.tagList.curselection()) +'"]/description').text
                opis += "\n"
                opis += self.tags.find('./family[@name="'+ self.currentFamily +'"]/tag[name="'+self.tagList.get(self.tagList.curselection()) +'"]/literature').text
                self.opisBox.delete('1.0', "end")
                self.opisBox.insert(tk.END, opis)
                self.opisBox.config(state = "disabled")   

    def save_file(self, root):
        f = filedialog.asksaveasfile(mode='a', defaultextension=".xml")
        if f is None: 
            return
        if root.find('./head/tag') is not None:
            tree = lxml.etree.ElementTree()
            tree._setroot(root)
            tree.write(f.name)
            
  
    def load_file(self, wordList):
        
        self.textDir = filedialog.askopenfilename()
        annotatorApp.wordList = []
        
        if not self.textDir.endswith('.txt'):
            print("Error-Error\nPlik musi mieć format '.txt'")
            pass

        with open(self.textDir) as f:
            for line in f:
                for word in line.split():
                    w = re.sub('[^A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż]', '', word)
                    annotatorApp.wordList.append(w)
  #      print(annotatorApp.wordList)
        
        # tworzenie wordList2
        fullText = ""
        with open(self.textDir) as f:
            for row in f:
                fullText += row
     #   print(fullText)
        poczatek = 0
        niepasuje = 0
        charIdx = 0

        
        
        for words in  annotatorApp.wordList:
            nextWord = 0
            while nextWord == 0:
                niepasuje = 0
                poczatek = charIdx
                for letter in range(len(words)):
                    if words[letter] != fullText[charIdx + letter]:
                        niepasuje = 1
                charIdx += 1
                if niepasuje == 0:
                    nextWord = 1
                
                #jak tu jesteś to znaczy że znaleziono kolejne całe słowo
            charIdx += len(words)
            
            neww = lxml.etree.Element ("word") 
            neww.text = words 
            neww.attrib["beginning"]=str(poczatek)
            neww.attrib["end"]=str(poczatek + len(words))
            neww.attrib["lenght"]=str(len(words))
            self.root.find("./fulltext").append(neww) 
            
       
        print(lxml.etree.tostring(self.root, pretty_print=True))
               
        
        annotatorApp.refresh(self)
        
    def refresh(self, *args):
        
        self.textBoxMain.config(state="normal")
        self.textBoxAnn.config(state="normal")
        
        
#wypełnia MainBox        
        
        
#        self.textBoxMain.delete('1.0', "end")
#        for word in annotatorApp.wordList:
#           self.textBoxMain.insert("end", word)
#           self.textBoxMain.insert("end", "\n")
           
           
#wypełnia AnnBox
           
           
   #     for row in range(10):
    #        self.textBoxAnn.insert("end", "aaaaaaaa\n")
            
        with open(self.textDir) as f:
            for row in f:
                self.textBoxMain.insert("end", str(row) + "\n")
            
        annDict = {"000001" : ["1.0", "2.3"]}
        for ann in annDict:
            self.textBoxAnn.tag_add(ann, annDict[ann][0], annDict[ann][1])
            self.textBoxAnn.tag_config(ann, foreground="red")
            
            
        self.textBoxMain.config(state="disabled")
        self.textBoxAnn.config(state="disabled")
    
    def get_selected(self):
        
        selectionStart = self.textBoxMain.index("sel.first")
        selectionEnd = self.textBoxMain.index("sel.last")    
        selectionStartIdx = 0
        rowLenList = []
        with open(self.textDir) as f:
            for row in f:
                rowLenList.append(len(row)) 
        for row in range(int(selectionStart[0])):
            if row == int(selectionStart[0]) - 1:
                selectionStartIdx += int(selectionStart[2:])
            else:
                selectionStartIdx += rowLenList[row]
        
        selectionEndIdx = 0
        
        for row in range(int(selectionEnd[0])):
            if row == int(selectionEnd[0]) - 1:
                selectionEndIdx += int(selectionEnd[2:])
            else:
                selectionEndIdx += rowLenList[row]
                
        selectionEndIdx -= 1
        index = [selectionStartIdx, selectionEndIdx, selectionStart,selectionEnd ]
        return index
       

    def annotate_base(self, tag, tag_name, comment=''):
        
        index = self.get_selected()
        self.textBoxMain.tag_add(tag_name,index[2], index[3])
        self.textBoxMain.tag_config(tag_name, underline=1 )
        #dodaję do meta danych inforacje o utworzeniu taga
        if self.root.find('./head/tag[@name="'+tag+'"]') is None:
            mtag = lxml.etree.Element("tag") 
            mtag.attrib["name"]=tag
            mtag.attrib["tag_name"]=tag_name
            mtag.attrib["amount"]="1"
            self.root.find("./head").append(mtag) 
        else:
            self.root.find('./head/tag[@name="'+tag+'"]').attrib["amount"]= str(int(self.root.find('./head/tag[@name="'+tag+'"]').attrib["amount"])+1)

        
        etag = lxml.etree.Element("tag") 
        etag.text = self.textBoxMain.selection_get()
        if comment:
            etag.attrib["comment"]=comment
        etag.attrib["name"]=tag
        etag.attrib['tag_name']=tag_name
        etag.attrib["beginning"]=str(index[0])
        etag.attrib["end"]=str(index[1])
        etag.attrib["lenght"]=str(index[1]-index[0])
        self.root.find("./tags").append(etag) 

    def annotate_note(self, tag, tag_name ):
        w=popupWindow(self,self.setting.get(self.language,'comment'))
        self.wait_window(w.top)
        self.annotate_base(tag, tag_name, w.value)

    def annotate(self, tag, tag_name, tag_type):
        if tag_type is None or tag is None:
            return
        switcher = {
            "base": self.annotate_base,    
            "note": self.annotate_note

        }
    
        func = switcher.get(tag_type, lambda y,x: print("Invalid type"))
        func(tag, tag_name)



class popupWindow(object):
    def __init__(self,master, lable):
        top=self.top=tk.Toplevel(master)
        self.l=tk.Label(top,text=lable)
        self.l.pack()
        self.e=tk.Entry(top, width=20)
        self.e.pack()
        self.b=tk.Button(top,text='Ok',command=self.cleanup)
        self.b.pack()
    def cleanup(self):
        self.value=self.e.get()
        self.top.destroy()




app = annotatorApp()
app.mainloop()
