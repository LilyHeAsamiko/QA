# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 13:46:39 2024

@author: Admin
"""

# -*- coding: utf-8 -*-
'''from __future__ import unicode_literals
import sys
import getpass, os, os.path, uno

class Session():
    @staticmethod
    def substitute(var_name):
        ctx = uno.getComponentContext()
        ps = ctx.getServiceManager().createInstanceWithContext(
            'com.sun.star.util.PathSubstitution', ctx)
        return ps.getSubstituteVariableValue(var_name)
    @staticmethod
    def Share():
        inst = uno.fileUrlToSystemPath(Session.substitute("$(prog)"))
        return os.path.normpath(inst.replace('program', "Share"))
    @staticmethod
    def SharedScripts():
        return ''.join([Session.Share(), os.sep, "Scripts"])
    @staticmethod
    def SharedPythonScripts():
        return ''.join([Session.SharedScripts(), os.sep, 'python'])
    @property  # alternative to '$(username)' variable
    def UserName(self): return getpass.getuser()
    @property
    def UserProfile(self):
        return uno.fileUrlToSystemPath(Session.substitute("$(user)"))
    @property
    def UserScripts(self):
        return ''.join([self.UserProfile, os.sep, 'Scripts'])
    @property
    def UserPythonScripts(self):
        return ''.join([self.UserScripts, os.sep, "python"])

user_lib = Session.UserPythonScripts  # User scripts location
if not user_lib in sys.path:
    sys.path.insert(0, user_lib)  # Add to search path
import screen_io as ui  # 'screen_io.py' module resides in user_lib directory
# Your code follows here'''

import unotools 
def main(): # 连接到LibreOffice实例 
    desktop = unotools.UnoService("com.sun.star.frame.Desktop") 
    doc = desktop.loadComponentFromURL("private:factory/swriter", "_blank", 0, ()) # 获取文档的文本控制器 
    text = doc.Text # 在文档中插入文本 
    cursor = text.createTextCursor() 
    text.insertString(cursor, "Hello World", False) # 保存文档 
    doc.storeToURL("file:///path/to/save/document.odt",()) 
    doc.dispose() 
if __name__ == "__main__": 
    main()

import subprocess

# 启动LibreOffice服务
subprocess.run(['soffice', '--headless', '--invisible', '--nodefault', '--nofirststartwizard', '--nologo', '--norestore'])

import uno

# 创建一个LibreOffice组件上下文
local_context = uno.getComponentContext()

# 创建一个服务管理器
resolver = local_context.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local_context)

# 连接到LibreOffice的服务
ctx = resolver.resolve("uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")

# 获取Root解析器
smgr = ctx.ServiceManager

# 创建一个新的Desktop组件
desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)

# 打开待转换的文件
doc = desktop.loadComponentFromURL(r"E:\AQF\AQF\05_QuantTrRC\PDValue.xlxm", "_blank", 0, ())

import time

# 转换文件
doc.refresh()
time.sleep(2)

# 关闭文档
doc.close(True)

import os

# 获取待转换文件的目录和文件名
file_dir = os.path.dirname(r"E:\AQF\AQF\05_QuantTrRC")
file_name = os.path.basename(r"PDValue.xlxm")

# 构造输出文件的路径和名称
output_file = os.path.join(file_dir, f"converted_{file_name}.pdf")

# 设置输出参数
output_props = (
    uno.createUnoStruct("com.sun.star.beans.PropertyValue"),
)
output_props[0].Name = "FilterName"
output_props[0].Value = "writer_pdf_Export"

# 设置转换后文件的输出路径和格式
doc.storeToURL(output_file, output_props)



import uno
import time
import os
import signal

class OfficeProcess(object):
    def __init__(self):
        self.p = 0
        subprocess.Popen('find /usr/share/fonts | xargs touch -m -t 201801010000.00', shell=True)

    def start_office(self):
        self.p = subprocess.Popen('soffice --pidfile=sof.pid --invisible --accept="socket,host=localhost,port=2002;urp;"', shell=True)
        while True:
            try:
                local_context = uno.getComponentContext()
                resolver = local_context.getServiceManager().createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver', local_context)
                resolver.resolve('uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext')
                return
            except:
                print( "wait for connecting soffice...")#ts(),
                time.sleep(1)
                continue

    def stop_office(self):
        with open("sof.pid", "rb") as f:
            try:
                os.kill(int(f.read()), signal.SIGTERM)
                self.p.wait()
            except:
                pass
