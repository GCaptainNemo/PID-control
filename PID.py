from tkinter import * 						#导入Tkinter模块
import tkinter.colorchooser
import tkinter.messagebox as messagebox
import threading 
import datetime
import time
import math
import random
import sys
sys.setrecursionlimit(100000)					#设置递归深度

root=Tk()
root.title("PID Simulator")					#生成一个主窗口对象
root.geometry("885x550")
root.resizable(0,0)
#root.iconbitmap(".\\tk.ico")

MaxOutPut=65							#最大输出值
Timer_Flag=False
Timer_Itv=1
Adjust_Flag=False
Err_Accumulation=0.0
N_Cycle = 500
N_Tolerance = 0.05
N_Optimize_Cycle = 100
Data=[]
Kp_Min=[]
Kp_Max=[]
KKp=0
KKi=0

def Data_Init(flag):
	global Data
	global Err_Accumulation
	global Kp_Min
	global Kp_Max
	global KKp
	global Optimize_Cycle
	if flag==0:
		Err_Accumulation=0.0
		Data.clear()
		Data=[[0] * 100, [ 0 ] * 100, [0] * 100, [0]*100, [0]*100, [0]*100, [0]*100]
	elif flag == 1:
		Kp_Min.clear()
		Kp_Min = [0]*100
		Kp_Max.clear()
		Kp_Max = [0]*100
		Kp_Max[-1] = 10
		Kp_Min[-1] = 0
		KKp = Kp_Max[-1]
		Optimize_Cycle=0

# 坐标转换
X_C = lambda x: x * 5 + 50
Y_C = lambda y: (4000 - 25 * y) / 11

# 数据输入块
SetInput = [50, 0, 0, 0, 1]					#存储设定值,频率,输入类型,当前周期,增长模式
frmInput = Frame(root) 					#bd=2, relief=RIDGE,bg='yellow')
frmInput.grid(row=0, column=0, rowspan=2, padx=5, pady=5)


def Mysel():							#控制频率设置滑块
	if SetInput[2] != Inputvar.get():
		SetInput[2] = Inputvar.get()
		Data_Init(0)
	if Inputvar.get() == 0:
		scaleSetF.set(0)
		scaleSetF.config(state=DISABLED)
	else:
		scaleSetF.config(state=NORMAL)


dic = {0: '手  动 ', 1: '矩形波 ', 2: '三角波 ', 3: '正弦波 '}
Inputvar = IntVar()
Inputvar.set(0)

for i,j in dic.items():
	RB=Radiobutton(frmInput,text=j,variable=Inputvar,value=i,command=Mysel)
	RB.grid(row=i,column=0,padx=1,pady=1,sticky=W)

for i,j in {0:'S P :',1:'周期:'}.items():
	Label(root,text=j).grid(row=i,column=1,padx=3,pady=3)

def SetP_Change(tt):					        #取设定值（幅值）
	SetInput[0]=int(tt)

def SetF_Change(tt):					        #取频率
	SetInput[1]=int(tt)

SetP=IntVar()							#设定值，波形幅值
scaleSetP=Scale(root,orient=HORIZONTAL,variable=SetP,command=SetP_Change,
	from_=0,to=100,resolution=5)
scaleSetP.set(SetInput[0])
scaleSetP.grid(row=0,column=2)	
SetF=IntVar()							#波形频率
scaleSetF=Scale(root,orient=HORIZONTAL,variable=SetF,command=SetF_Change,
	from_=0,to=20.0,resolution=2,state=DISABLED)
scaleSetF.set(SetInput[1])
scaleSetF.grid(row=1,column=2)	

#PID参数设置块
SetPara=[0.6,0.3,0.1] 					        #存储Kp,Ki,Kd 的值
frmParameter=Frame()
frmParameter.grid(row=3,column=0,columnspan=3,padx=3,pady=1)

def Para_Set(tt,i):						#取Kp，Ki，Kd的值
	SetPara[i]=float(tt)

dic = {0:'Kp: ',1:'Ki: ',2:'Kd: '}
ScalePID=[]
for i,j in dic.items():
	Label(frmParameter,text=j).grid(row=i,column=1,padx=8,pady=3)
	Entry(frmParameter,width=12,textvariable=SetPara[i]
		).grid(row=i,column=2,padx=10,pady=3)
	SC=Scale(frmParameter,orient=HORIZONTAL,variable=SetPara[i],
		command=lambda i=i,j=i:Para_Set(i,j),from_=0,to=10.0,resolution=0.05)
	SC.set(SetPara[i])
	ScalePID.append(SC)
	SC.grid(row=i,column=3,padx=1,pady=1)

#运行参数与颜色设置块
def Myclick(tt):
	TakeCol = tkinter.colorchooser.askcolor()		        #取颜色
	#Buttons1[tt]['bg']=TakeCol[1]					#按键赋新背景色
	Buttons1[tt].config(bg=TakeCol[1])				#按键赋新背景色
	CurveCol[tt]=TakeCol[1]						#更新颜色列表

CurveName=['Up:','Ui:','Ud:','OP:','PV:','E :']
CurveVal=[StringVar(),StringVar(),StringVar(),StringVar(),StringVar(),StringVar()]
CurveCol=['#ffffff','#ffffff','#ffffff','#0000ff','#ff0000','#00ff00','#000000']
frmCurve=Frame()	
frmCurve.grid(row=4,column=0,columnspan=3,padx=3,pady=3)
Buttons1=[]
for i in CurveName:
	j=CurveName.index(i)
	if j<3:
		k=j
		l=0
	else:
		k=j-3
		l=3
	Label(frmCurve,text=i).grid(row=k,column=l,padx=8,pady=3,sticky=W)
	CurveVal[j].set('0.0000')
	Label(frmCurve,width=10,textvariable=CurveVal[j],relief=SUNKEN
		).grid(row=k,column=l+1,padx=3,pady=3)
	BT=Button(frmCurve,width=3,command=lambda j=j:Myclick(j),bg=CurveCol[j])
	BT.grid(row=k,column=l+2,padx=1,pady=1)
	Buttons1.append(BT)

#系统参数设置块
SystemVar=['速度:','干扰:','惯性:','滞后:']
SystemVal=[11,0,6,6]					#初始值
Down_Level=[1,0,1,1]					#下限值
Up_Level=[20,10,10,10]					#上限值
frmSystem=Frame()
frmSystem.grid(row=5,column=0,columnspan=3,padx=1,pady=1)

def Sys_Set(tt,i):
	global SystemVal
	global Timer_Itv
	SystemVal[i]=int(tt)
	if i==0:
		Timer_Itv=2.1-SystemVal[0]/10

for i in SystemVar:
	j=SystemVar.index(i)
	Label(frmSystem,text=i).grid(row=j//2,column=j%2*2,padx=8,pady=3,sticky=W)
	SC=Scale(frmSystem,orient=HORIZONTAL,variable=SystemVar[j],
		command=lambda i=j,j=j:Sys_Set(i,j),from_=Down_Level[j],to=Up_Level[j])
	SC.set(SystemVal[j])
	SC.grid(row=j//2,column=j%2*2+1,padx=1,pady=1)

def Value_Test(content):				#校检最大输出值的有效性
	global MaxOutPut
	if content == "" :
		return True
	elif content.isdigit() :
		if float(content)>0 and float(content)<=100:
			MaxOutPut=float(content)
			return True
		else:
			return False
	else:
		return False

Label(root,text='最大输出:').grid(row=6,column=0,padx=8,pady=3,sticky=W)
Outputvar=StringVar()
Outputvar.set(str(MaxOutPut))	
Value_Test_cmd=root.register(Value_Test)		# 需要将函数包装一下，必要的
ET=Entry(root,width=12,textvariable=Outputvar,validate='key',validatecommand=(Value_Test_cmd,'%P'))
# %P表示 当输入框的值允许改变，该值有效。该值为当前文本框内容
ET.grid(row=6,column=1,padx=1,pady=1)

#设置绘图块
CV=Canvas(root,width=550,height=500,bg='white')
CV.grid(row=0,column=3,rowspan=6,columnspan=12,padx=3,pady=3,sticky=N)

def Draw_Canvas():
	CV.delete(ALL)
	CV.create_line(X_C(-5),Y_C(0),X_C(100),Y_C(0),fill='#888888',width=2)
	CV.create_line(X_C(0),Y_C(150),X_C(0),Y_C(-50),fill='#888888',width=3)
	CV.create_line(X_C(-1),Y_C(150),X_C(0),Y_C(150),fill='#888888',width=2)
	CV.create_line(X_C(-1),Y_C(100),X_C(0),Y_C(100),fill='#888888',width=2)
	CV.create_line(X_C(-1),Y_C(50),X_C(0),Y_C(50),fill='#888888',width=2)
	CV.create_line(X_C(-1),Y_C(-50),X_C(0),Y_C(-50),fill='#888888',width=2)
	CV.create_text(X_C(-4),Y_C(150),fill='#888888', text='150')
	CV.create_text(X_C(-4),Y_C(100),fill='#888888', text='100')
	CV.create_text(X_C(-3),Y_C(50),fill='#888888', text='50')
	CV.create_text(X_C(-4),Y_C(-50),fill='#888888', text='-50')
	
def Time_Itv():								#当在函数Time_Itv()的参数中包括一个线程实例时
	if Timer_Flag:
		#print("当前时间：%s" % time.ctime())
		Draw_Canvas()						#绘图
		if Adjust_Flag:
			PID_Adjust()
		else:
			Do_Cal()						#计算
		time.sleep(Timer_Itv) 				#睡眠2s
		Time_Itv()							#回调自己，新的计时开始

#设置功能按钮块
def ButtonClick(tt):
	#global Timer_Itv
	global Timer_Flag
	global Adjust_Flag

	if tt==0:								#模 拟
		Adjust_Flag=False
		if Timer_Flag:
			Timer_Flag=False
			Buttons2[0].config(text='模 拟')
		else:
			Timer_Flag=True
			Buttons2[0].config(text='暂 停')
			Data_Init(0)
			ta = threading.Thread(target=Time_Itv,args=())
			ta.start() 						#启动线程
	elif tt==1:								#复 位
		Data_Init(0)
		Data_Init(1)
		Draw_Canvas()
	elif tt==2:								#整 定
		Adjust_Flag=True
		Timer_Flag=True
		Buttons2[0].config(text='暂 停')
		Data_Init(1)
		ta = threading.Thread(target=Time_Itv,args=())
		ta.start() 							#启动线程
	elif tt==3:								#关 于
		messagebox.showinfo("关 于", "PID 仿真软件 V2.0\n\n"+
			"主要用于PID相关知识学习与模拟\n\n"+
			"Kp：增大，系统响应加快，静差缩小，但系统振荡增加，稳定性下降；\n"+
			"Ki：增大，加快消除系统静差，但系统超调增加，稳定性下降；\n"+
			"Kd：增大，系统灵敏度增加，系统振荡减弱，但系统对扰动的抑制能力减弱；\n\n"+
			"惯性越大，KpKiKd指数级上升；\n"+"滞后越大，Kp无影响，Ki指数级下降，Kd线性上升；\n\n"+
			"增量式PID算法\n系统定义：惯性+滞后\n\n参数自整定方法：4：1衰减法\n\n"+
			"Author：gzhstar\n2021-5"
			"")
	elif tt==4:								#退 出
		My_End()

ButtonName=['模 拟','复 位','整 定','关 于','退 出']
Buttons2=[]
for i in ButtonName:
	j=ButtonName.index(i)
	BT=Button(root,text=i,command=lambda j=j:ButtonClick(j))
	BT.grid(row=6,column=j+10,padx=1,pady=1)
	Buttons2.append(BT)
Buttons2[1].config(state=DISABLED)

Data_Init(0)
Draw_Canvas()

def Do_Cal():
	global Data
	global SetInput
	t=0									#计算设置值
	if SetInput[1]>0:						        #波形
		if SetInput[4]==1:					        #增长模式
			SetInput[3]+=1
			if SetInput[3]-SetInput[1]>=0:
				SetInput[3]=SetInput[1]
				SetInput[4]=0
		else:								#递减模式
			SetInput[3]-=1
			if SetInput[3]<=0:
				SetInput[3]=0
				SetInput[4]=1
		if SetInput[2]==1:					        #矩形波
			if SetInput[4]==1:
				t=SetInput[0]
			else:
				t=0
		elif SetInput[2]==2:				                #三角波
			t=SetInput[0]/SetInput[1]*SetInput[3]
		else:								#正弦波
			t=SetInput[0]*(math.sin((SetInput[1]/2-SetInput[3])/SetInput[1]*3.14)+1)/2
	else:									#设置值,手动
		t=SetInput[0]
	del Data[6][0]							        #删除第一个数据
	Data[6].append(t)						        #增加最后个数据
	Do_PID(SetPara[0],SetPara[1],SetPara[2],1)

	for i in range(len(CurveVal)):			                        #显示数据
		CurveVal[i].set(str(Data[i][-1])[0:8])
	for j in range(len(Data)):				                #绘制曲线
		#t=Data[j][99]+random.randint(-5,5)
		tmp=[]
		for i in range(100):
			tmp.append(X_C(i))
			tmp.append(Y_C(Data[j][i]))
		CV.create_line(tmp,fill=CurveCol[j])

def Do_PID(Kp,Ki,Kd,flag):		
	#['Up:','Ui:','Ud:','OP:','PV:','E :','SV']
	global Data
	global Err_Accumulation
	global SystemVal				#['速度:','干扰:','惯性:','滞后:']

	for i in range(len(Data)-1):
		del Data[i][0]
	Data[0].append(Kp*(Data[5][-1]-Data[5][-2]))					#Up
	Data[1].append(Ki*Data[5][-1])									#Ui
	Data[2].append(Kd*(Data[5][-1]+Data[5][-3]-2*Data[5][-2]))	    #Ud
	opv=Data[4][-1]+Data[0][-1]+Data[1][-1]+Data[2][-1]
	if opv>MaxOutPut:
		opv=MaxOutPut
	if opv<-MaxOutPut:
		opv=-MaxOutPut	
	Data[3].append(opv)						#OP
	if flag!=0:							#整定时去除干扰
		opv=opv+random.randint(-1.0,1.0)*SystemVal[1]/10 	#干扰
	opv=opv*(1-SystemVal[2]/11)+Data[4][-1]*SystemVal[2]/11 	#惯性
	Data[4].append(opv)						#PV
	Data[5].append(Data[6][-1]-Data[4][-SystemVal[3]])		#E（一阶滞后）

def PID_Adjust():							#PID整定
	global Timer_Flag
	global Kp_Min
	global Kp_Max
	global Optimize_Cycle
	global KKp
	global KKi
	global ScalePID
	global SetPara

	KKi_Cycle=0
	KKK=0
	Inflexion1,Inflexion2,Inflexion3=0.0,0.0,0.0
	Optimize_Cycle+=1
	if Optimize_Cycle>N_Optimize_Cycle:
		Adjust_Flag=False
		Timer_Flag=False
		messagebox.showinfo("信 息", "优化未成功。优化次数内，未找合适的参数。")
	flag=0 								#找波峰标志
	j=0
	Data_Init(0)							#复位数据
	Data[6][-1]=50

	while j<N_Cycle:
		j+=1
		#del Data[6][0]						#删除第一个数据
		#Data[6].append(SetInput[0])		                #增加最后个数据
		Do_PID(KKp,0,0,0)
		if flag==1:
			KKi_Cycle+=1
		if Data[5][-2]-Data[5][-1]>=0 and Data[5][-2]>Data[5][-3]:
			KKK=KKi_Cycle
			Inflexion2=Data[5][-2]	
		if Data[5][-1]-Data[5][-2]>=0 and Data[5][-3]-Data[5][-2]>0.0001 and j>SystemVal[3]:      #找波峰
			if flag==1:						                #第二个波峰
				KKi=KKi_Cycle				                        #第二个波峰与第一个之间的周期数
				Inflexion3=Data[5][-2]						#第二个波峰最大误差值
				break
			if flag==0:						                #第一个波峰
				flag=1
				KKi_Cycle=0
				Inflexion1=Data[5][-2]
		
	if j>=N_Cycle:
		Adjust_Flag=False
		Timer_Flag=False
		messagebox.showinfo("信 息", "优化未成功。未找到两个匹配波峰。")
	else:
		#缩小范围
		Tolerance=(Inflexion2-Inflexion1)-(Inflexion2-Inflexion3)*2
		if abs(Tolerance)<=N_Tolerance or Kp_Max[-1]-Kp_Min[-1]<=N_Tolerance/100:
			Adjust_Flag=False
			Timer_Flag=False
			SetPara[0]=0.6*KKp
			SetPara[1]=SetPara[0]/(0.18*KKi)
			SetPara[2]=SetPara[0]*(0.02*KKi)
			for k in range(3):
				ScalePID[k].set(SetPara[k])
			messagebox.showinfo("信 息","优化成功。"+"\n\n  Kp: "+str(SetPara[0])[0:4]+
				"\n  Ki:  "+str(SetPara[1])[0:4]+"\n  Kd: "+str(SetPara[2])[0:4])
		else:
			if Tolerance > 0:
				del Kp_Min[0]
				del Kp_Max[0]
				Kp_Min.append(KKp)
				Kp_Max.append(Kp_Max[-1])
				KKp +=(Kp_Max[-1] - Kp_Min[-1]) / 3
			else:
				del Kp_Min[0]
				del Kp_Max[0]
				Kp_Min.append(Kp_Min[-1])
				Kp_Max.append(KKp)
				KKp -= (Kp_Max[-1] - Kp_Min[-1]) / 3

	for i in range(100):
		if Kp_Min[i]+Kp_Max[i]>0:
			CV.create_rectangle(X_C(i),Y_C(Kp_Min[i]*10),
				X_C(i+1),Y_C(Kp_Max[i]*10),fill='#00ff00')

def My_End():
	global Timer_Flag
	Timer_Flag=False
	time.sleep(2)
	#messagebox.showinfo("退出","退出程序！")
	root.quit()
	#root.destroy()
	
root.protocol("WM_DELETE_WINDOW", My_End)
root.mainloop()

