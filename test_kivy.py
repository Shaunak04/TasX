import time
# from win10toast import ToastNotifier 
import pandas as pd
# import threading
from tkinter import *
from PIL import Image, ImageTk
import tkinter.font as font
import pyttsx3
import speech_recognition as sr
# import pywhatkit as kit
import ttk as ttk

phone_number="+919687869541"

######GUI######
root=Tk()
root.title("Task Organizer")
root.geometry("636x400")
root.resizable(width=False, height=False)
root.configure(background="black")
topFont = font.Font(family='Times', size=20, weight='bold')
buttonFont = font.Font(family='verdana', size=12, weight='normal')

###### GIF FRAMES HANDLING######
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
def tick(time1=''):
    time_now = time.strftime('%I:%M:%p')
    clock.config(text=time_now)
    clock.after(2000, tick)
clock = Label(root,fg="white",bg='#262626',font=topFont)
clock.place(x=265,y=10)
tick()
############


global tasks
global task_time
global tasks_Data
tasks_Data=pd.read_csv("All_data\\reminder.csv")
task_time=list(tasks_Data['time'])
temp_time=task_time.copy()
tasks= list(tasks_Data['task'])
task_time.sort()
all_tasks=[tasks[temp_time.index(i)] for i in task_time]

# def show_noti():
# 	if len(all_tasks)>0 and len(task_time)>0:
# 	 	first_time=str(task_time[0])
# 	 	first_hour=str(first_time[0:2])
# 	 	first_minute=str(first_time[3:5])
# 	 	if int(first_minute)<=2:
# 	 		first_minute=str((first_minute-2)%60)
# 	 		first_hour=first_hour-1
# 	 	else:
# 	 		first_minute=str(int(first_minute)-2)
# 	  	time_string=time.strftime("%H:%M")
# 	  	hour=time_string[0:2]
# 	  	minute=time_string[3:5]
# 	  	if hour==first_hour and minute=first_minute:
# 	  		time_index=task_time.index(time_string)
# 	  		n = ToastNotifier()
# 	  		n.show_toast("ASSISTANT",tasks[time_index], duration = 20)
# 	  		kit.sendwhatmsg(phone_number,all_tasks[0],first_hour,first_minute)
# 			all_tasks.pop(0)
# 			task_time.pop(0)
# 	  	rec=threading.Timer(60,show_noti)
# 	  	rec.start()
# 	  	print(time_string)
# show_noti()
# s=input()


######ADD TASK BUTTON######
def add():
	newWindow = Toplevel(root)
	newWindow.title('Add task')
	newWindow.geometry("300x200")
	newWindow.config(background="#161616")
	newWindow.resizable(width=False, height=False)
	def listen():
		global new_time
		global new_task
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
			task_time.append(new_time)
			print("updated time list  ",task_time)

		h.delete(0,END)
		m.delete(0,END)
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
				all_tasks.append(new_task)
				tasks_Data['tasks']=all_tasks
				tasks_Data['time']=task_time
				print("updated tasks list  ",all_tasks)

			except:
				engine.say("could not understand,please try again")
				engine.runAndWait()
		tasks_Data.to_csv("E:\\Assisant\\All_data\\reminder.csv")
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
	newWindow.title('View task')
	newWindow.geometry("300x300")
	newWindow.config(background="#161616")
	newWindow.resizable(width=False, height=True)
	y_index=15
	for k in range(len(all_tasks)):
		Label(newWindow,text="     "+all_tasks[k]+' '*abs(27-len(all_tasks[k]))+'|'+" "*(5)+task_time[k],fg="white",bg="#161616",bd=0,font=('Times',14,'normal'),justify="center").place(x=0,y=y_index)
		Label(newWindow,text="_"*70,fg="white",bg="#161616",bd=0).place(x=0,y=y_index+17)
		y_index=y_index+43
view_task_button=Button(root,command=view,font=buttonFont,activeforeground="white",width=16,activebackground="black",bd=1,justify="center",fg="white",bg="#0f0f0f",text="VIEW ALL TASKS")
view_task_button.place(x=320,y=350)
############
root.mainloop()
