# DetectingClonesInAndroidAPP
Edited by python, based on the PAPER:Detecting Clones in Android Applications through Analyzing User Interfaces-Camera Ready  
这是一个本人写的检测Android APP UI相似度的Python程序  
是这篇论文的Python代码实现：Charlie Soh,Yauhen Arnatovich,"Detecting Clones in Android Applications through Analyzing User Interfaces-Camera Ready", 2015.5  
其中的LSH算法的实现采用了：http://www.mit.edu/~andoni/LSH/ 的C代码；      
匈牙利算法的实现采用了：https://github.com/maandree/hungarian-algorithm-n3;     
我已经测试了120个apk之间相互之间的相似度，代码应该没什么问题；      
不过时间比较少，代码中可能有bug；

### Usage:
#### 环境准备：
Android环境的安装：  
你需要安装android sdk，下载和安装都可以在`Android Developer`上找到，这里直接给出[下载链接](https://developer.android.com/studio/index.html)。  
安装完成后,在shell中(windows是powershell或cmd)输入adb， 如果能出现如下信息则说明安装成功  
  
![adb](/img/adb.PNG)
  
>注意：在windows中可能需要额外配置adb的环境变量

Android虚拟机的安装：  
这里我个人推荐[Genymotion虚拟机](https://www.genymotion.com/)  
安装完后启动genymotion  
![genymotion](/img/genymotion.PNG)
点击左上角的add添加android虚拟机，添加完后启动虚拟机查看是否正常运行  
![androidDevice](/img/androidDevice.PNG)

Apktool的安装：  
下载及安装说明点击[这里](https://ibotpeaches.github.io/Apktool/install/)  
安装完成后,在shell中(windows是powershell或cmd)输入apktool， 如果能出现如下信息则说明安装成功  
  
![apktool](/img/apktool.PNG)
>注意：在windows中可能需要额外配置apktool的环境变量

Python的安装：  
下载及安装说明点击[这里](https://www.python.org/downloads/)  

#### 开始运行
##### 1.生成Birthmarks
工程目录的结构结构如下所示：  
```
root ------ bm.py  //生成birthmarks的代码
       |
       ---- tap.py  //模拟点击的代码
       |
       ---- apk_set //包含目标apk的文件夹
       |
       ---- birthmarks  //保存各个app生成生成的birthmark的文件夹
```
>注意：apk_set里的apk不宜过多，因为虚拟机不稳定，可能会导致批处理崩溃