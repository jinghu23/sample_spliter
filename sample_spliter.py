#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import sqlite3
from functools import partial
import sys
from pyDes import *
import numpy as np
import pandas as pd

class table_page(QDialog):
	page=1
	def __init__(self):
		super().__init__()
		self.UI()
		
	def UI(self):
		barcode_pool=dict()
		
		grid=QGridLayout()
		grid.setVerticalSpacing(10)
		
		con=sqlite3.connect('blood_sample')
		c=con.cursor()
		try:
			#c.execute('create table blood_differ (barcode text primary key,bank text,BJ text,SH text);')
			#print('1')
			dt=c.execute('select * from blood_differ').fetchall()
		except sqlite3.OperationalError:
			dt=[]
			#dt=c.execute('select * from blood_differ').fetchall()
			
		#lb=QLabel('*泡沫垫子从左上角开始记录位置，位置记录形式为“泡沫垫编号_行数_列数”的方式，从左上角依次从左往右逐个摆放血管',self)
		#lb.setAlignment(Qt.AlignCenter)
		#grid.addWidget(lb,0,2)
		
		matrix_tp=QLabel('*请输入存放盒的规格',self)
		grid.addWidget(matrix_tp,1,0)
		r_l=QLabel('存放盒行数：',self)
		c_l=QLabel('存放盒列数：',self)
		
		
		self.row=QLineEdit('5',self) #default is 5
		self.row.setFixedWidth(50)
		self.column=QLineEdit('10',self) #default is 10
		self.column.setFixedWidth(50)
		grid.addWidget(r_l,2,0)
		grid.addWidget(self.row,2,1)
		grid.addWidget(c_l,3,0)
		grid.addWidget(self.column,3,1)
		r_num=int(self.row.text())
		c_num=int(self.column.text())
		self.row.textEdited.connect(partial(self.val,self.row,r_num))
		self.row.textEdited.connect(partial(self.val,self.column,c_num))

		self.tip=QLabel('*放置提示*',self)
		self.tip.setAlignment(Qt.AlignCenter)
		grid.addWidget(self.tip,4,2)
		
		sc_tp=QLabel('扫码区域',self)
		self.scan_reg=QLineEdit(self)
		self.scan_reg.setFixedWidth(150)
		self.scan_reg.setAlignment(Qt.AlignLeft)
		
		self.scan_reg.textEdited.connect(partial(self.data_rev,barcode_pool,self.tip,r_num,c_num,self.scan_reg))
		
		self.clr=QPushButton('清除',self)
		self.clr.clicked.connect(partial(self.del_,self.scan_reg))
		self.clr.setFixedSize(35,20)
		self.clr.setStyleSheet('color:black;')
		grid.addWidget(sc_tp,5,0)
		grid.addWidget(self.scan_reg,5,1)
		grid.addWidget(self.clr,5,2)
		
		
		#qv=QVBoxLayout()
		#qv.setSpacing(5)
		self.ex=QTableWidget(self)
		self.ex.setSelectionMode(QTableWidget.SingleSelection)
		self.ex.setMouseTracking(True)
		self.ex.setRowCount(1)
		self.ex.setColumnCount(8)
		self.ex.verticalHeader().setVisible(False)
		self.ex.horizontalHeader().setStretchLastSection(True)
		self.ex.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.ex.setSelectionBehavior(QTableWidget.SelectItems)
		headers=['条形码','档案编号','姓名','性别','年龄','备份(北京)','北京','上海']
		self.ex.setHorizontalHeaderLabels(headers)
		for i in range(self.ex.columnCount()):
			h=self.ex.horizontalHeaderItem(i)
			h.setFont(QFont('Helvetica Neue',13,QFont.Bold))
		#qv.addWidget(self.ex)
		#grid.addLayout(qv,6,0,1,5)
		grid.addWidget(self.ex,6,0,1,5)
		grid.setRowStretch(6,1)
		
		
		self.tb=QTableWidget(self)
		self.tb.setSelectionMode(QTableWidget.SingleSelection)
		self.tb.setMouseTracking(True)
		self.tb.setRowCount(20)
		self.tb.setColumnCount(8)
		self.tb.verticalHeader().setVisible(False)
		self.tb.horizontalHeader().setVisible(False)
		
			
		self.tb.horizontalHeader().setStretchLastSection(True)
		self.tb.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.tb.setSelectionBehavior(QTableWidget.SelectItems)
		
		self.tb.setEditTriggers(QTableWidget.NoEditTriggers)
		#self.tb.itemChanged.connect(partial(self.data_rev,barcode_pool,self.tip))
		
		if dt:
			table_page.fullview(self,table_page.page,20,dt)
		else:pass
		
		grid.addWidget(self.tb,7,0,10,5)
		grid.setRowStretch(7,20)
		#qv.addWidget(self.ex)
		#qv.addWidget(self.tb)
		#grid.addLayout(qv,6,0,6,5)
		
		self.bt1=QPushButton('上一页',self)
		self.bt2=QPushButton('下一页',self)
		self.bt1.clicked.connect(self.page_ba)
		self.bt2.clicked.connect(self.page_for)
		grid.addWidget(self.bt1,17,3)
		grid.addWidget(self.bt2,17,4)
		
		self.setLayout(grid)
		self.setWindowTitle('血样入库系统v0.1')
		self.setGeometry(300,300,900,800)
		self.show()
	
	def del_(self,bt):
		bt.setText('')	
	def val(self,txt,r_num):
		try:
			r_num=int(txt.text())
		except ValueError:pass
		#print(r_num)
		#return(r_num)
	def val2(self,txt,c_num):
		try:
			c_num=int(txt.text())
		except ValueError:pass
		
	def data_rev(self,bp,bt,r_num,c_num,ql):
		unit='00001'
		bar_info=sqlite3.connect('name_list')
		b=bar_info.cursor()
		
		con=sqlite3.connect('blood_sample')
		c=con.cursor()
		if len(ql.text())==10:
			try:
				c.execute('create table blood_differ (barcode text primary key,file_no text,name text,sex text,age text,bank text,BJ text,SH text)')
				accd_dt=b.execute('select * from info where regis_no = '+ql.text()).fetchone()
				#print(accd_dt)
				if accd_dt:
					v=str(tuple([ql.text(),accd_dt[-1],accd_dt[5],accd_dt[6],accd_dt[7],unit+'_'+'1_1_1','-','-']))
					c.execute('insert into blood_differ values '+v)
					con.commit()
				#print('2')
					self.ex.setItem(0,0,QTableWidgetItem(ql.text()))
					self.ex.setItem(0,1,QTableWidgetItem(accd_dt[-1]))
					self.ex.setItem(0,2,QTableWidgetItem(accd_dt[5]))
					self.ex.setItem(0,3,QTableWidgetItem(accd_dt[6]))
					self.ex.setItem(0,4,QTableWidgetItem(accd_dt[7]))
					self.ex.setItem(0,5,QTableWidgetItem(unit+'_'+'1_1_1'))
					self.ex.setItem(0,6,QTableWidgetItem('-'))
					self.ex.setItem(0,7,QTableWidgetItem('-'))
					new_dt=c.execute('select * from blood_differ').fetchall()
					#print(new_dt)
					table_page.fullview(self,1,20,new_dt)
				else:
					QMessageBox.about(self,'Title','数据库中不存在该条码，请核对后重新输入！')
		
			except sqlite3.OperationalError:
				accd_dt=b.execute('select * from info where regis_no = '+ql.text()).fetchone()
				if accd_dt:
					info=c.execute('select * from blood_differ where barcode = '+ql.text()).fetchone()
					#print(info)
					if info:
						self.ex.setItem(0,0,QTableWidgetItem(info[0]))
						self.ex.setItem(0,1,QTableWidgetItem(info[1]))
						self.ex.setItem(0,2,QTableWidgetItem(info[2]))
						self.ex.setItem(0,3,QTableWidgetItem(info[3]))
						self.ex.setItem(0,4,QTableWidgetItem(info[4]))
						self.ex.setItem(0,5,QTableWidgetItem(info[5])) #mark: BJ(bank)
						risker_list=[x.rstrip() for x in open('risker_list.txt').readlines()]
						if info[1] in risker_list:
							print('1')
							#nbj=c.execute('select BJ from blood_differ').fetchall()[-1][0]
							#print(nbj)
							comp='00001'
							nbj=c.execute('select BJ from blood_differ where BJ != "-"').fetchall()
							print('nbj:%s' % nbj)
							nbj2=[x[0].split('_')[1:] for x in nbj]
							dt=np.array(nbj2)
							df=pd.DataFrame(dt)
							#print(df)
							try:
								mc1=df[0].max()
								df2=df[df[0].isin([mc1])]
								mc2=df2[1].max()
								df3=df2[df2[1].isin([mc2])]
								mc3=df3[2].max()
								df4=df3[df3[2].isin([mc3])]
								npos=np.array(df4).tolist()[0]
							#try:
								box,r_pos,c_pos=npos
								print(box,r_pos,c_pos)
								if int(c_pos)+1<= c_num:
									self.ex.setItem(0,6,QTableWidgetItem(comp+'_'+box+'_'+r_pos+'_'+str(int(c_pos)+1)))
								elif int(c_pos)==c_num and int(r_pos)<r_num:
									self.ex.setItem(0,6,QTableWidgetItem(comp+'_'+box+'_'+str(int(r_pos)+1)+'_1'))
								elif int(r_pos)==r_num and int(c_pos)==c_num:
									self.ex.setItem(0,6,QTableWidgetItem(comp+'_'+str(int(box)+1)+'_1_1'))
								c.execute('update blood_differ set BJ = "%s" where barcode = %s' % (str(self.ex.item(0,6).text()),ql.text()))
								con.commit()
							except KeyError:
								comp='00001'
								self.ex.setItem(0,6,QTableWidgetItem(comp+'_'+'1_1_1'))
								c.execute('update blood_differ set BJ = "%s" where barcode = %s' % (str(self.ex.item(0,6).text()),ql.text()))
								con.commit()
							#except TypeError:
								
							#c.execute('update blood_differ set BJ = '+self.ex.item(0,6).text()+' where barcode = '+ql.text())
							
									
						else:
							comp='00001'
							nsh=c.execute('select SH from blood_differ where SH != "-"').fetchall()
							print('nsh:%s' % nsh)
							nsh2=[x[0].split('_')[1:] for x in nsh]
							dt=np.array(nsh2)
							df=pd.DataFrame(dt)
							#print(df)
							try:
								mc1=df[0].max()
								df2=df[df[0].isin([mc1])]
								mc2=df2[1].max()
								df3=df2[df2[1].isin([mc2])]
								mc3=df3[2].max()
								df4=df3[df3[2].isin([mc3])]
								npos=np.array(df4).tolist()[0]
							#print(nsh)
							#try:
								box,r_pos,c_pos=npos
								print(box,r_pos,c_pos)
								if int(c_pos)+1<= c_num:
									self.ex.setItem(0,7,QTableWidgetItem(comp+'_'+box+'_'+r_pos+'_'+str(int(c_pos)+1)))
								elif int(c_pos)==c_num and int(r_pos)<r_num:
									self.ex.setItem(0,7,QTableWidgetItem(comp+'_'+box+'_'+str(int(r_pos)+1)+'_1'))
								elif int(r_pos)==r_num and int(c_pos)==c_num:
									self.ex.setItem(0,7,QTableWidgetItem(comp+'_'+str(int(box)+1)+'_1_1'))
								c.execute('update blood_differ set SH = "%s" where barcode = %s' % (str(self.ex.item(0,7).text()),ql.text()))
								con.commit()
							except KeyError:
								comp='00001'
								self.ex.setItem(0,7,QTableWidgetItem(comp+'_'+'1_1_1'))
								c.execute('update blood_differ set SH = "%s" where barcode = %s' % (str(self.ex.item(0,7).text()),ql.text()))
								con.commit()
							#print(self.ex.item(0,7).text())
							
						#self.ex.setItem(0,2,QTableWidget(info[2]))  #ensure which column to write
						#self.ex.setItem(0,3,QTableWidget(info[3]))
						
						new_dt=c.execute('select * from blood_differ').fetchall()
						table_page.fullview(self,1,20,new_dt)
					else:
						try:
							#print(accd_dt)							
							#self.ex.setItem(0,0,QTableWidgetItem(ql.text()))
							#accd_dt=b.execute('select * from info where seq = '+ql.text()).fetchone()
							nb=c.execute('select bank from blood_differ').fetchall()[-1][0]
							self.ex.setItem(0,0,QTableWidgetItem(ql.text()))
							self.ex.setItem(0,1,QTableWidgetItem(accd_dt[-1]))
							self.ex.setItem(0,2,QTableWidgetItem(accd_dt[5]))
							self.ex.setItem(0,3,QTableWidgetItem(accd_dt[6]))
							self.ex.setItem(0,4,QTableWidgetItem(accd_dt[7]))
							#self.ex.setItem(0,5,QTableWidgetItem(unit+'_'+'1_1_1'))
							#self.ex.setItem(0,6,QTableWidgetItem('-'))
							#self.ex.setItem(0,7,QTableWidgetItem('-'))
							comp,box,r_pos,c_pos=nb.split('_')
							#print(box,r_pos,c_pos)
							if int(c_pos)+1<= c_num:
								self.ex.setItem(0,5,QTableWidgetItem(comp+'_'+box+'_'+r_pos+'_'+str(int(c_pos)+1)))
							elif int(c_pos)==c_num and int(r_pos)<r_num:
								self.ex.setItem(0,5,QTableWidgetItem(comp+'_'+box+'_'+str(int(r_pos)+1)+'_1'))
							elif int(r_pos)==r_num and int(c_pos)==c_num:
								self.ex.setItem(0,5,QTableWidgetItem(comp+'_'+str(int(box)+1)+'_1_1'))		
				
							self.ex.setItem(0,6,QTableWidgetItem('-'))
							self.ex.setItem(0,7,QTableWidgetItem('-'))
						#print('7')
							v=str(tuple([ql.text(),self.ex.item(0,1).text(),self.ex.item(0,2).text(),self.ex.item(0,3).text(),self.ex.item(0,4).text(),self.ex.item(0,5).text(),self.ex.item(0,6).text(),self.ex.item(0,7).text()]))
						#print('7-1')
							c.execute('insert into blood_differ values '+v)
							con.commit()
						#print('8')
							new_dt=c.execute('select * from blood_differ').fetchall()
							table_page.fullview(self,1,20,new_dt)
						except:pass
				else:
					QMessageBox.about(self,'Title','数据库中不存在该条码，请核对后重新输入！')
	
	def fullview(self,page,rownumber,dt):
		self.tb.clearContents()
		if page*rownumber <= len(dt):
			for r in range((page-1)*rownumber,page*rownumber):
				self.tb.setItem(r-(page-1)*rownumber,0,QTableWidgetItem(dt[r][0]))
				self.tb.setItem(r-(page-1)*rownumber,1,QTableWidgetItem(dt[r][1]))
				self.tb.setItem(r-(page-1)*rownumber,2,QTableWidgetItem(dt[r][2]))
				self.tb.setItem(r-(page-1)*rownumber,3,QTableWidgetItem(dt[r][3]))
				self.tb.setItem(r-(page-1)*rownumber,4,QTableWidgetItem(dt[r][4]))
				self.tb.setItem(r-(page-1)*rownumber,5,QTableWidgetItem(dt[r][5]))
				self.tb.setItem(r-(page-1)*rownumber,6,QTableWidgetItem(dt[r][6]))
				self.tb.setItem(r-(page-1)*rownumber,7,QTableWidgetItem(dt[r][7]))
		else:
			for r2 in range(rownumber*(page-1),len(dt)):
				self.tb.setItem(r2-rownumber*(page-1),0,QTableWidgetItem(dt[r2][0]))
				self.tb.setItem(r2-rownumber*(page-1),1,QTableWidgetItem(dt[r2][1]))
				self.tb.setItem(r2-rownumber*(page-1),2,QTableWidgetItem(dt[r2][2]))
				self.tb.setItem(r2-rownumber*(page-1),3,QTableWidgetItem(dt[r2][3]))
				self.tb.setItem(r2-rownumber*(page-1),4,QTableWidgetItem(dt[r2][4]))
				self.tb.setItem(r2-rownumber*(page-1),5,QTableWidgetItem(dt[r2][5]))
				self.tb.setItem(r2-rownumber*(page-1),6,QTableWidgetItem(dt[r2][6]))
				self.tb.setItem(r2-rownumber*(page-1),7,QTableWidgetItem(dt[r2][7]))
				
				
	def page_for(self):
		con=sqlite3.connect('blood_sample')
		c=con.cursor()
		dt=c.execute('select * from blood_differ').fetchall()
		if len(dt) <= self.tb.rowCount()*table_page.page:
			pass
		else:
			table_page.fullview(self,table_page.page+1,self.tb.rowCount(),dt)
			table_page.page+=1
	
	def page_ba(self):
		con=sqlite3.connect('blood_sample')
		c=con.cursor()
		dt=c.execute('select * from blood_differ').fetchall()
		if table_page.page==1:pass
		else:
			table_page.fullview(self,table_page.page-1,self.tb.rowCount(),dt)
			table_page.page-=1	
				
			
if __name__=='__main__':
	app=QApplication(sys.argv)
	ex=table_page()
	sys.exit(app.exec_())			
			
