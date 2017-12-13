#!/usr/bin/env python3

import sqlite3
from pyDes import *
import os,sys
from itertools import *
import base64

con=sqlite3.connect('name_list')
c=con.cursor()
c.execute('create table info (seq text,test_id text,test_no text,regis_no text,card text,name text,sex text,age text,identity text,file_no text)')
for line in islice(open('name_list.txt'),1,None):
	line=line.rstrip().split('\t')
	personal=des("DESCRYPT", CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
	ep=personal.encrypt(line[-1])
	unit='00001'
	fd=str(base64.b64encode(ep),encoding='utf-8')
	file_no=unit+'_'+fd
	line.append(file_no)
	v=str(tuple(line))
	c.execute('insert into info values '+v)
	
con.commit()
con.close()
	