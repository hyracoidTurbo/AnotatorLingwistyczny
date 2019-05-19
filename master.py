# -*- coding: utf-8 -*-


import tkinter as tk
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
        
        setting = ConfigParser()
        setting.read('config.ini')
        language=setting.get('general','language')
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("800x500+20+20")    
        self.grid()
        
        self.textBoxMain = tk.Text()
        self.textBoxMain.grid(sticky ="nswe", column=0, row =1)
        self.textBoxMain.config(state="disabled")
        
        self.textBoxAnn = tk.Text(width = 8)
        self.textBoxAnn.grid(sticky ="nswe", column=1, row =1)
        self.textBoxAnn.config(state="disabled")
        
        tags = ET.parse(setting.get(language,'tag_set_path'))
        if tags.find('tag/name') is not None:
            names = [events.text for events in tags.findall('tag/name')]
        self.tagNameList = names

        self.tagList = tk.Listbox(width = 20, selectmode = "SINGLE", exportselection= False)
        for j in range(len(self.tagNameList)):
            self.tagList.insert(j, self.tagNameList[j])
            
        self.tagList.grid(row=1, column = 2, sticky = "wn")
        
        button_newAnn = tk.Button(text = setting.get(language,'new_annotation') , command = lambda: self.new_annatation())
        button_newAnn.grid(row=2, column = 2)
        
        menuBar = tk.Menu(self)   
        menuFile = tk.Menu(menuBar, tearoff = 0)
 #       menulanguage = tk.Menu(menuBar, tearoff = 1)

        menuBar.add_cascade(label =setting.get(language,'file'), menu = menuFile)
        menuFile.add_command(label=setting.get(language,'load'), command = lambda: self.load_file(self.wordList))   
    
# Jakbyśmy chcieli się powbawić w zmanę języka
#        menuBar.add_cascade(label = setting.get(language,'language') ,menu = menulanguage )
#        langueges_list = json.loads(setting.get(language,"languages"))
#        for key in langueges_list.keys():
#            if isinstance(langueges_list[key], dict)== False:
#                menulanguage.add_command(label = key, command= change_language(key)  )
       
       
        self.config(menu = menuBar)
#    def change_language(self, key):
#        return

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
        self.wordList2 = lxml.builder.ElementMaker()
        root = self.wordList2.root
        word = self.wordList2.word
        the_doc = root(word())
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
            the_doc.append(word(words, beginning=str(poczatek), end=str(poczatek + len(words)),lenght=str(len(words))))
       
        print(lxml.etree.tostring(the_doc, pretty_print=True))
               
        
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
        
    def new_annatation(self, *args):
        print(self.tagList.curselection())

  #      selectedText = self.textBoxMain.selection_get()
        
        selectionStart = self.textBoxMain.index("sel.first")
        selectionEnd = self.textBoxMain.index("sel.last")
        print("SelStart:" + str(selectionStart))
        print("SelEnd:" + str(selectionEnd))
        
        
        rowLenList = []
        with open(self.textDir) as f:
            for row in f:
               rowLenList.append(len(row)) 
        
       
        selectionStartIdx = 0

        for row in range(int(selectionStart[0])):
            if row == int(selectionStart[0]) - 1:
                selectionStartIdx += int(selectionStart[2:])
            else:
                selectionStartIdx += rowLenList[row]
            
        print("selectionStartIdx "+ str(selectionStartIdx))
                
        
        
        
        
        selectionEndIdx = 0
        
        for row in range(int(selectionEnd[0])):
            if row == int(selectionEnd[0]) - 1:
                selectionEndIdx += int(selectionEnd[2:])
            else:
                selectionEndIdx += rowLenList[row]
                
        selectionEndIdx -= 1
        
        
        
        print("selectionEndIdx "+ str(selectionEndIdx))
     
       
        startFound = 0
        lookAtWord = 0
        while startFound == 0:   
            if selectionStartIdx >= self.wordList2[lookAtWord][1] and selectionStartIdx <= self.wordList2[lookAtWord][2]:
                print(self.wordList2[lookAtWord][0])
                startFound = 1
            lookAtWord += 1
            
        endFound = 0
        lookAtWord = 0
        while endFound == 0:   
            if selectionEndIdx >= self.wordList2[lookAtWord][1] and selectionEndIdx <= self.wordList2[lookAtWord][2]:
                print(self.wordList2[lookAtWord][0])
                endFound = 1
         #   if 
            lookAtWord += 1
                
                
     #   self.text.tag_add("sel", "1.7", "1.12")
      #  self.text.focus_force()
        

        
        
        
        
    
        
        #bierze wybraną annotację z listy tagów
          #  s = self.tagList.get(self.tagList.curselection())

   #     self.textBoxMain.tag_add("one", "1.0", "1.0 wordend")
    #    self.textBoxMain.tag_config("one", foreground="red")
        

        
        
app = annotatorApp()
app.mainloop()
