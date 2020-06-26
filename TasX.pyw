import time
from win10toast import ToastNotifier 
import pandas as pd
import threading
from tkinter import *
from PIL import Image, ImageTk
import tkinter.font as font
import pyttsx3
import speech_recognition as sr
import pywhatkit as kit
import ttk as ttk
import math

phone_number="+919687869541"

######GUI######
root=Tk()
root.title("TasX")
root.geometry("636x400")
root.resizable(width=False, height=False)
root.configure(background="black")
root.iconbitmap("All_Data\\assistant_icon.ico")
topFont = font.Font(family='Times', size=20, weight='bold')
buttonFont = font.Font(family='verdana', size=12, weight='normal')

######GIF FRAMES HANDLING######

class MyLabel(Label):
	def __init__(self, master, filename):
		im = Image.open(filename)
		seq =  []
		try:
			while 1:
				seq.append(im.copy())
				im.seek(len(seq))
				# skip to next frame
		except EOFError:
			pass 
		try:
			self.delay = im.info['duration']
		except KeyError:
			self.delay = 100
		first = seq[0].convert('RGBA')
		self.frames = [ImageTk.PhotoImage(first)]
		Label.__init__(self, master, image=self.frames[0])
		temp = seq[0]
		for image in seq[1:]:
			temp.paste(image)
			frame = temp.convert('RGBA')
			self.frames.append(ImageTk.PhotoImage(frame))
		self.idx = 0
		self.cancel = self.after(self.delay, self.play)

	def play(self):
		self.config(image=self.frames[self.idx])
		self.idx += 1
		if self.idx == len(self.frames):
			self.idx = 0
		self.cancel = self.after(self.delay, self.play)        
anim = MyLabel(root, 'All_data\\loop.gif')
anim.place(x=0,y=0,relwidth=1, relheight=1)

############

######TOP CLOCK######
def tick():
    time_now = time.strftime('%I:%M:%p')
    clock.config(text=time_now)
    clock.after(2000, tick)
clock = Label(root,fg="white",bg='#262626',font=topFont)
clock.place(x=265,y=10)
tick()

############

def time_minutes():
	return time.strftime("%M")

def time_hour():
	return time.strftime("%H")

def normalize_time(s):
	minutes=s[3:5]
	hours=s[0:2]
	if int(minutes)<=3:
		minutes=str(60+int(minutes)-3)
		hours=str(int(hours)-1)
		if int(hours)<0:
			hours=str(int(hours)+24)
	else:
		minutes=str(int(minutes)-3)
	if len(minutes)<2:
		minutes='0'+minutes
	if len(hours)<2:
		hours='0'+hours
	return (hours+':'+minutes)
	
def check_nan(l):
	c=0
	for k in l:
		if type(k)!=str:
			if math.isnan(k)==True:
				c=1
				break
	return c

def load_sorted_dataset():
	tasks_Data=pd.read_csv("All_data\\reminder.csv")
	task_time=list(tasks_Data['time'])
	tasks= list(tasks_Data['task'])
	
	if check_nan(task_time)==1:
		task_time.pop(0)
	if check_nan(tasks)==1:
		tasks.pop(0)
	if len(task_time)>0 and len(tasks)>0:
		temp_time=task_time.copy()
		time_diff=[]
		for k in task_time:
			diff_index=(int(k[0:2])-int(time_hour()))+(int(k[3:5])-int(time_minutes()))/60
			if diff_index<0:
				diff_index+=24
			time_diff.append(diff_index)
		time_diff_copy=time_diff.copy()
		time_diff.sort()
		all_tasks=[tasks[time_diff_copy.index(i)] for i in time_diff]
		task_time=[normalize_time(temp_time[time_diff_copy.index(i)]) for i in time_diff]
		return [all_tasks,task_time]
	else :
		return [0,0]

global tasks
global task_time
global tasks_Data
global all_tasks
l=load_sorted_dataset()
task_time = l[1]
all_tasks = l[0]
############

#######ADD TASK BUTTON######
def add():
	newWindow = Toplevel(root)
	newWindow.title('Add task')
	newWindow.iconbitmap("All_Data\\assistant_icon.ico")
	newWindow.geometry("300x200")
	newWindow.config(background="#161616")
	newWindow.resizable(width=False, height=False)
	def listen():
		l=load_sorted_dataset()
		task_time = []
		all_tasks = []
		new_task=''
		new_time=''
		get_hour=str(h.get())
		get_min=str(m.get())
		if int(get_hour)<24 and int(get_min)<=59:
			if len(get_hour)==1:
				get_hour='0'+get_hour
			if len(get_min)==1:
				get_min='0'+get_min
			new_time=get_hour+':'+get_min
			engine=pyttsx3.init()
			engine.setProperty('rate', 170)
			engine.setProperty('volume',1.0)
			engine.say("what is the task")
			engine.runAndWait()
			r1=sr.Recognizer()
			with sr.Microphone() as source:
				try:
					audio = r1.listen(source)
					new_task = r1.recognize_google(audio)
					task_time.append(new_time)
					all_tasks.append(new_task)
					tasks_Data=pd.read_csv("All_data\\reminder.csv")
					tasks_Data=tasks_Data.append({'task':new_task,'time':new_time},ignore_index=True)
					tasks_Data=tasks_Data.drop_duplicates(subset=["task","time"],keep="first")
					tasks_Data.to_csv("All_data\\reminder.csv",index=False)
				except:
					engine.say("could not understand,please try again")
					engine.runAndWait()

		h.delete(0,END)
		m.delete(0,END)
		l=load_sorted_dataset()
		task_time = l[1]
		all_tasks = l[0]
		show_noti()
		
	Label(newWindow,text="Hour",fg="white",bg="#161616",font=('Times',10,'normal')).place(x=118,y=30)
	Label(newWindow,text="Minutes",fg="white",bg="#161616",font=('Times',10,'normal')).place(x=193,y=30)
	Label(newWindow,text="Time",fg="white",bg="#161616",font=('Times',20,'normal')).place(x=40,y=50)
	h=Spinbox(newWindow,width=4,bg="#565656",fg="white",font=('Times',18,'normal'),bd=1,from_=0,to=23)
	h.place(x=110,y=53)
	m=Spinbox(newWindow,width=4,bg="#565656",fg="white",font=('Times',18,'normal'),bd=1,from_=0,to=59)
	m.place(x=183,y=53)
	speak_button=Button(newWindow,command=listen,text="Speak task",font=('Times',15,'normal'),bd=1,fg="white",bg="#060606",activebackground="black",activeforeground="white")
	speak_button.place(x=100,y=120)
	
add_task_button=Button(root,command=add,font=buttonFont,activeforeground="white",width=16,activebackground="black",bd=1,justify="center",fg="white",bg="#0f0f0f",text="ADD NEW TASK")
add_task_button.place(x=140,y=350)
############

######VIEW TASK BUTTON######
def view():
	newWindow = Toplevel(root)
	newWindow.iconbitmap("All_Data\\assistant_icon.ico")
	newWindow.title('View task')
	newWindow.config(background="#161616")
	newWindow.geometry("280x500")
	newWindow.resizable(width=False, height=True)
	y_index=15
	l=load_sorted_dataset()
	task_time = l[1]
	all_tasks = l[0]
	show_noti()

	if all_tasks!=0:
		for k in range(len(all_tasks)):
			Label(newWindow,text="     "+all_tasks[k]+" "*abs(20-len(all_tasks[k]))+'|'+" "*(5)+(task_time[k][0:2])+':'+str(int(task_time[k][3:5])+3),fg="white",bg="#161616",bd=0,font=('Times',14,'normal'),justify="center").place(x=0,y=y_index)
			Label(newWindow,text="_"*70,fg="white",bg="#161616",bd=0).place(x=0,y=y_index+20)
			y_index=y_index+45
		def clear_tasks():
			tasks_Data=pd.read_csv("All_data\\reminder.csv")
			tasks_Data=tasks_Data.iloc[0:0]
			tasks_Data.to_csv("All_data\\reminder.csv",index=False)
			newWindow.destroy()
			
		Button(newWindow,command=clear_tasks,text='Clear all Tasks',fg="white",bg="red").place(x=101,y=470)
	else:
		Label(newWindow,text="No tasks to display",fg="white",bg="#161616",font=topFont).place(x=20,y=200)
view_task_button=Button(root,command=view,font=buttonFont,activeforeground="white",width=16,activebackground="black",bd=1,justify="center",fg="white",bg="#0f0f0f",text="VIEW ALL TASKS")
view_task_button.place(x=320,y=350)
############ 

######Notification function###
def show_noti():
	l=load_sorted_dataset()
	task_time = l[1]
	all_tasks = l[0]
	if all_tasks!=0 and task_time!=0 and len(all_tasks)>0 and len(task_time)>0:
		hour=time_hour()
		minute=time_minutes()
		if (hour==task_time[0][0:2]) and (minute==task_time[0][3:5]):
			notif = ToastNotifier()
			notif.show_toast("ASSISTANT",all_tasks[0]+' it is '+hour+':'+minute,duration=5)
			kit.sendwhatmsg(phone_number,all_tasks[0]+' it is '+hour+':'+minute,int(hour),int(minute)+2)
			all_tasks.pop(0)
			task_time.pop(0)
	rec=threading.Timer(60,show_noti)
	rec.start()
show_noti()
#############

root.mainloop()