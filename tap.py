#coding=utf-8  
  
import tempfile  
import os  
import re  
import time  
import xml.etree.cElementTree as ET  
  
class Element(object):  
    """ 
    通过元素定位,需要Android 4.0以上 
    """  
    def __init__(self, xml_filename):  
        """ 
        初始化，获取系统临时文件存储目录，定义匹配数字模式 
        """  
        # self.tempFile = tempfile.gettempdir() 
        self.tempFile = xml_filename
        self.pattern = re.compile(r"\d+")  
  
    def __uidump(self):  
        """ 
        获取当前Activity控件树 
        """  
        os.system("adb shell uiautomator dump --compressed /sdcard/uidump.xml")  
        os.system("adb pull /sdcard/uidump.xml " + self.tempFile)  
  
    def __element(self, attrib, name):  
        """ 
        同属性单个元素，返回单个坐标元组 
        """  
        # self.__uidump()  
        tree = ET.ElementTree(file=self.tempFile)  
        treeIter = tree.iter(tag="node")  
        for elem in treeIter:  
            if name in elem.attrib[attrib]:  
                bounds = elem.attrib["bounds"]  
                coord = self.pattern.findall(bounds)  
                Xpoint = (int(coord[2]) - int(coord[0])) / 2.0 + int(coord[0])  
                Ypoint = (int(coord[3]) - int(coord[1])) / 2.0 + int(coord[1])  
  
                return Xpoint, Ypoint  
  
  
    def __elements(self, attrib, name):  
        """ 
        同属性多个元素，返回坐标元组列表 
        """  
        list = []  
        # self.__uidump()  
        tree = ET.ElementTree(file=self.tempFile)  
        treeIter = tree.iter(tag="node")  
        for elem in treeIter:  
            if name in elem.attrib[attrib]:  
                bounds = elem.attrib["bounds"]  
                coord = self.pattern.findall(bounds)  
                Xpoint = (int(coord[2]) - int(coord[0])) / 2.0 + int(coord[0])  
                Ypoint = (int(coord[3]) - int(coord[1])) / 2.0 + int(coord[1])  
                list.append((Xpoint, Ypoint))  
        return list  
  
    def findElementByName(self, name):  
        """ 
        通过元素名称定位 
        usage: findElementByName(u"设置") 
        """  
        return self.__element("text", name)  
  
    def findElementsByName(self, name):  
        return self.__elements("text", name)  
  
    def findElementByClass(self, className):  
        """ 
        通过元素类名定位 
        usage: findElementByClass("android.widget.TextView") 
        """  
        return self.__element("class", className)  
  
    def findElementsByClass(self, className):  
        return self.__elements("class", className)  
  
    def findElementById(self, id):  
        """ 
        通过元素的resource-id定位 
        usage: findElementsById("com.android.deskclock:id/imageview") 
        """  
        return self.__element("resource-id",id)  
  
    def findElementsById(self, id):  
        return self.__elements("resource-id",id)  
  
class Event(object):  
    # def __init__(self):  
    #     os.popen("adb wait-for-device ")  
  
    def touch(self, device, dx, dy):  
        """ 
        触摸事件 
        usage: touch(500, 500) 
        """  
        if device == '':
            # print("adb shell input tap " + str(dx) + " " + str(dy))
            os.system("adb shell input tap " + str(dx) + " " + str(dy))  
        else:
            # print("adb -s " + device + " shell input tap " + str(dx) + " " + str(dy))
            os.system("adb -s " + device + " shell input tap " + str(dx) + " " + str(dy))  

        time.sleep(0.5)  
  
def test():  
    element = Element('uidump.xml')  
    e1 = element.findElementByName('has stopped.')
    print(e1)
    if not e1 is None:
        event = Event()
        print('1')
        e2 = element.findElementByName('OK')
        print('2')
        event.touch('192.168.53.101:5555', e2[0], e2[1])
        print('3')
        time.sleep(1) 


if __name__ == '__main__':
    test()