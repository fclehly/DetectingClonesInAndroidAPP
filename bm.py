#encoding=utf-8
import os
import xml.sax
import sys
import tap
import time


components = ['textview', 'edittext', 'button', 'checkbox', 'bar', 'switch', 'spinner', 'view', 'layout']
useful_attrs = ['checkable', 'checked', 'clickable', 'enabled', 'focusable', 'focused','scrollable', 'long-clickable', 'password', 'selected']

class ManifestHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.activities = []
        self.package_name = ''

    def startElement(self, name, attrs):
        if name == 'manifest':
            self.package_name = attrs['package']
        elif name == 'activity':
            self.activities.append(attrs['android:name'])
    def getAll(self):
        return self.package_name, self.activities

class DumpFilterHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.map = {}

    def startElement(self, name, attrs):
        if name == 'node':
            k = ''
            subkey = 0
            for s in components:
                if s in attrs['class'].lower():
                    k = s
                    break
            for s in useful_attrs:
                subkey += (1 if attrs[s] == 'true' else 0) << useful_attrs.index(s)
            if k != '':
                if k in self.map.keys():
                    array = self.map[k]
                else:
                    array = [0 for x in range(0, 1024)]
                array[subkey] += 1
                self.map[k] = array
    def getMap(self):
        return self.map


def parse_manifest(manifest_filename):
    #解析AndroidManifest.xml，获得packageName和activities
    manifest_handler = ManifestHandler()
    xml.sax.parse(manifest_filename, manifest_handler)
    return manifest_handler.getAll()

#1.start activity
#2.dump activity
#3.stop activity
#4.pull dumpfile from emulator to host
#当activity启动失败时，把当前activity从activities_list中剔除，并点击跳出来的'Unfortunely, xxx has stop.'的messagebox的'OK'按钮
def dump_acitvities(emulator_device, package_name, activities, activities_dump_folder):
    if not os.path.exists(activities_dump_folder):
        os.mkdir(activities_dump_folder)
    waste_activities = []
    for acitivity in activities:
        # if not package_name in acitivity:
        #     waste_activities.append(acitivity)
        #     continue
        print('Debug:', 'Dumping:', acitivity)
        if emulator_device is None or emulator_device == '':
            os.system('adb shell am start -n ' + package_name + '/' + acitivity)
            time.sleep(1.5)
            os.system('adb shell uiautomator dump /sdcard/' + acitivity + 'Dump.xml')
            os.system('adb shell am force-stop ' + package_name)
            os.system('adb pull /sdcard/' + acitivity + 'Dump.xml ' + activities_dump_folder + '/' + acitivity + 'Dump.xml')
            os.system('adb shell rm /sdcard/' + acitivity + 'Dump.xml')
        else:
            os.system('adb -s ' + emulator_device + ' shell am start -n ' + package_name + '/' + acitivity)
            time.sleep(1.5)
            os.system('adb -s ' + emulator_device + ' shell uiautomator dump /sdcard/' + acitivity + 'Dump.xml')
            os.system('adb -s ' + emulator_device + ' shell am force-stop ' + package_name)
            os.system('adb -s ' + emulator_device + ' pull /sdcard/' + acitivity + 'Dump.xml ' + activities_dump_folder + '/' + acitivity + 'Dump.xml')
            os.system('adb -s ' + emulator_device + ' shell rm /sdcard/' + acitivity + 'Dump.xml')
        if os.path.exists(activities_dump_folder + '/' + acitivity + 'Dump.xml'):
            #activity 启动失败
            element = tap.Element(activities_dump_folder + '/' + acitivity + 'Dump.xml')
            e1 = element.findElementByName('has stopped.')
            if not e1 is None:
                waste_activities.append(acitivity)
                print('Info: ', acitivity, 'has stopped...')
                event = tap.Event()
                e2 = element.findElementByName('OK')
                event.touch(emulator_device, e2[0], e2[1])
                # time.sleep(0.5)
        
    for activity in waste_activities:
        activities.remove(activity)
    return waste_activities

#生成birthmark文件
def generate_birthmark(acitivies_dump_holder, acitvities, birthmark_filename):
    birthmark_file = open(birthmark_filename, 'w')
    for acitivity in acitvities:
        if os.path.exists((acitivies_dump_holder + '/' + acitivity + 'Dump.xml')):
            filter_handler = DumpFilterHandler()
            xml.sax.parse(acitivies_dump_holder + '/' + acitivity + 'Dump.xml', filter_handler)
            map = filter_handler.getMap()
            for s in components:
                if s in map.keys():
                    for c in map[s]:
                        birthmark_file.write((str(c) + ' '))
                else:
                    for x in range(0, 1024):
                        birthmark_file.write('0 ')
            birthmark_file.write('\n')
            birthmark_file.flush()
    birthmark_file.close()

#usage:
#python bm.py [-option name]
#example1: python bm.py -s emulator_name -apk xxx.apk -o birthmark_folder
#example2: python bm.py -s emulator_name -f apk_folder -o birthmark_folder
#[-s emulator_name]
#[-f apk_folder]
#[-o folder]
if __name__ == '__main__':
    #定义命令行参数
    emulator_device = ''
    birthmark_folder = ''
    apk_folder = ''
    logcat_folder = 'mylogcat'
    if not os.path.exists(logcat_folder):
        os.mkdir(logcat_folder)
    apk_name_list = []
    if '-o' in sys.argv:
        birthmark_folder = sys.argv[sys.argv.index('-o') + 1]
        if not os.path.exists(birthmark_folder):
            os.mkdir(birthmark_folder)
    if '-s' in sys.argv:
        emulator_device = sys.argv[sys.argv.index('-s') + 1]
    if '-apk' in sys.argv:
        apk_name_list.append(sys.argv[sys.argv.index('-apk') + 1])
    if '-f' in sys.argv:
        apk_folder = sys.argv[sys.argv.index('-f') + 1]
        if not os.path.exists(apk_folder):
            print('folder not exist')
            exit()
        else:
            for f in os.listdir(apk_folder):
                if '.apk' in f:
                    apk_name_list.append(f)
    
    #1.安装app
    #2.用apktool获取apk的AndroidManifest.xml
    #3.解析AndroidManifest.xml
    #4.在虚拟机中依次启动activity并用uiautomator dump当前activity
    #5.根据每个dumpfile生成birthmark
    #6.卸载app
    #7.如果list中还有apk返回1
    for apk_name in apk_name_list:
        apk_filename = apk_name if apk_folder == '' else (apk_folder + '/' + apk_name)
        birthmark_filename = birthmark_folder + '/b_' + apk_name[:-4] + '.txt'
        manifest_folder = apk_name[:-4]
        manifest_filename = manifest_folder + '/AndroidManifest.xml'
        activities_dump_folder = 'a_' + apk_name[:-4]

        if emulator_device is '':
            os.system('adb install ' + apk_filename)
        else:
            os.system('adb -s ' + emulator_device + ' install ' + apk_filename)
        os.system('apktool d -s -f ' + apk_filename + ' -o ' + manifest_folder)
        
        package_name, activities = parse_manifest(manifest_filename)
        print('Debug: Package:', package_name)
        total_num = len(activities)
        print('Debug: Num of All Activities:', total_num)
        
        waste_activities = dump_acitvities(emulator_device, package_name, activities, activities_dump_folder)
        print('Debug: Num of Left Activities:', len(activities), '/', total_num)
        log_file = open(logcat_folder + '/' + package_name + '.txt', 'w')
        log_file.write('Debug: Num of Left Activities: ' + str(len(activities)) + '/' + str(total_num) + '\n')
        for a1 in activities:
            log_file.write('+' + a1 + '\n')
        for a2 in waste_activities:
            log_file.write('-' + a2 + '\n')
        log_file.close()
        
        #卸载app
        if emulator_device is '':
            os.system('adb uninstall ' + package_name)
        else:
            os.system('adb -s ' + emulator_device + ' uninstall ' + package_name)

        generate_birthmark(activities_dump_folder, activities, birthmark_filename)
       