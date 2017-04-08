# DetectingClonesInAndroidAPP
Edited by python, based on the PAPER:Detecting Clones in Android Applications through Analyzing User Interfaces-Camera Ready  
这是一个本人写的检测Android APP UI相似度的Python程序  
是这篇论文的Python代码实现：Charlie Soh,Yauhen Arnatovich,"Detecting Clones in Android Applications through Analyzing User Interfaces-Camera Ready", 2015.5  
其中的LSH算法的实现采用了：http://www.mit.edu/~andoni/LSH/ 的C代码；      
匈牙利算法的实现采用了：https://github.com/maandree/hungarian-algorithm-n3;     
我已经测试了120多个apk之间相互之间的相似度，代码应该没什么问题；      
不过时间比较少，代码中可能有bug；

### Usage:
#### 环境准备：
**Android环境的安装**：  
你需要安装android sdk，下载和安装都可以在`Android Developer`上找到，这里直接给出[下载链接](https://developer.android.com/studio/index.html)。  
安装完成后,在shell中(windows是powershell或cmd)输入adb， 如果能出现如下信息则说明安装成功  
  
![adb](/img/adb.PNG)
  
>注意：在windows中可能需要额外配置adb的环境变量

**Android虚拟机的安装**：  
这里我个人推荐[Genymotion虚拟机](https://www.genymotion.com/)  
当然也可以使用其他虚拟机，但不能使用真机。  
安装完后启动genymotion  
![genymotion](/img/genymotion.PNG)  
点击左上角的add添加android虚拟机，添加完后启动虚拟机查看是否正常运行  
![androidDevice](/img/androidDevice.PNG)

**Apktool的安装**：  
下载及安装说明点击[这里](https://ibotpeaches.github.io/Apktool/install/)  
安装完成后,在shell中(windows是powershell或cmd)输入apktool， 如果能出现如下信息则说明安装成功  
  
![apktool](/img/apktool.PNG)
>注意：在windows中可能需要额外配置apktool的环境变量

**Python的安装**：  
下载及安装说明点击[这里](https://www.python.org/downloads/)  
建议使用python3  


##### Genymotion Problem
**请注意**：  
Genymotion一直有个问题，就是很多ARM的程序都没法安装(比如微信)，毕竟是用的vbox虚拟机，相当于在x86环境下运行的，限定ARM的程序自然是无法安装了，会提示"INSTALL_FAILED_CPU_ABI_INCOMPATIBLE"这个错误，无法向模拟器部署，如果直接安装APK则会提示与您的设备不兼容。  
解决方案：  
* [Android模拟器Genymotion添加ARM程序运行环境的方法](http://blog.csdn.net/arex_efan/article/details/20008001)
* [Genymotion | Installing ARM Translation and GApps](https://forum.xda-developers.com/showthread.php?t=2528952)

#### 开始运行
##### 1.生成Birthmarks
>这部分在linux或windows下进行都可以
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
>注意：apk_set里的apk不宜过多(建议不超过10个)，因为虚拟机不稳定及app兼容性等问题，可能会导致批处理崩溃  
>另外，必须保证apk_set中的所有apk都能安装到虚拟机上，否则必须剔除不能安装的apk或更换android版本或[增加arm支持](#genymotion-problem)  
  
下面我用一个示例来说明如何生成birthmarks  
>birthmark即apk的ui信息的一种表示，详细参考Charlie Soh,Yauhen Arnatovich,"Detecting Clones in Android Applications through Analyzing User Interfaces-Camera Ready", 2015.5  
  

**示例**：  
>我的系统是windows10, 虚拟机android版本是4.2.2  
  
首先启动genymotion虚拟机，初始时我的机器上文件结构如下：  
![step1](/img/step1.PNG)  
  
我的apk_set文件夹中有两个apk  
![apks](/img/apks.PNG)  
  
打开shell，进入当前目录，输入`adb devices`,获取android虚拟机设备名  
![adbdevices](/img/adbDevices.PNG)
  
接着, 输入`python -s 192.168.1.101:5555 -f apk_set -o birthmarks`运行脚本  
这个命令表示在目标虚拟机上运行`apk_set`中的apk，并生成每个应用的birthmark到`birthmarks`文件夹中  
![bmrunning](/img/bmRunning.PNG)  
  
可以在虚拟机中看到每个app中的可启动的activity都被启动了  
![step2](/img/step2.PNG)  
  
运行结束后工程目录结构如下所示:  
![step3](/img/step3.PNG)  
多出的文件为代码生成的中间文件和日志信息  
  
>注意：可能在运行会遇到应用activity启动失败的问题导致应用被强制关闭的问题，如下所示，如果此时不消除这个对话框，则无法继续生成正确的ui信息，不过我已经处理了这个问题:当我检测到这个对话框时，我会调用tap.py里的函数来模拟点击ok按钮,并剔除这个activity的ui信息，以免其影响birthmark.  
  
![errorrunning](/img/errorRunning.PNG)

##### 2. 计算相似度
>这部分只能在linux下运行，这部分并不需要android环境，只需要python即可
工程目录的结构结构如下所示：  
  
```
root ------ calc_si.py  //计算相似度的代码
       |
       ---- bin  //文件夹中为LSH算法程序
       |
       ---- hungarian-algorithm-n3 //文件夹中为匈牙利算法程序
       |
       ---- birthmarks  //保存各个app生成生成的birthmark的文件夹
```
>注意：必须保证bin中所有文件和hungarian-algorithm-n3中的hungarian文件拥有可执行权限，否则使用chmod +x命令增加可执行权限  
  
**示例**
>我的系统是Linux x64(为了方便，我使用了[bash on ubuntu on windows](https://msdn.microsoft.com/en-us/commandline/wsl/about) 
  
初始时我的工程结构如下：  
![step4](/img/step4.PNG)
  
我们继续上面的示例，打开shell，进入工程目录，输入`python calc_si.py -f birthmarks -o result.txt` 
这个命令表示计算birthmarks中的每个应用的birthmark两两之间的相似度，并把结构保存至result.txt中
![calculating](/img/calculating.PNG)  
  
运行结束工程目录结构如下所示：  
![step5](/img/step5.PNG)  
多出来的文件为代码生成的中间文件和日志信息  
  
最终result.txt中的数据如下所示：  
![result](/img/resultExample.PNG)  
于是可以得到这两个app之间的相似度为0.381578947368

