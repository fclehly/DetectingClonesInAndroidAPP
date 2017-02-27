#encoding=utf-8
import os
import sys

radius = 6.5
threshold = 0.76

#计算similarity index
def calc_si(file1_name, file2_name, e2lsh_result_filename, h_input_filename):
    num1 = -1
    for num1, line in enumerate(open(file1_name, 'rU')):
        pass
    num1 += 1

    num2 = -1
    for num2, line in enumerate(open(file2_name, 'rU')):
        pass
    num2 += 1
    print(num1, num2)
    row_max = min(num1, num2)
    col_max = max(num1, num2)
    #调用lsh算法：reference:http://www.mit.edu/~andoni/LSH/
    # file3_name = 'e2lsh_result.txt'
    if num1 >= num2:
        os.system('./bin/lsh ' + str(radius) + ' ' + file1_name + ' ' + file2_name + ' > ' +  e2lsh_result_filename)
    else:
        os.system('./bin/lsh ' + str(radius) + ' ' + file2_name + ' ' + file1_name + ' > ' +  e2lsh_result_filename)

    #生成hungarian method的输入文件：矩阵行数一定要不大于列数
    # file4_name = 'hungarian_input.txt'

    file3 = open(e2lsh_result_filename, 'r')
    file4 = open(h_input_filename, 'w')
    lines = file3.readlines()
    for i in range(0, len(lines)):
        if 'Query point' in lines[i]:
            if 'no NNs found' in lines[i]:
                for x in range(0, col_max):
                    file4.write('999999 ') 
                file4.write('\n')
            else:
                i += 1
                row = {}
                while 'Distance' in lines[i]:
                    col = int(lines[i][0:lines[i].find('\t')])
                    row[col] = int(float(lines[i][lines[i].find(':') + 1:-1]) * 100)
                    i += 1
                for j in range(0, col_max):
                    if j in row.keys():
                        file4.write(str(row[j]) + ' ')
                    else:
                        file4.write('999999 ')
                file4.write('\n')
                row.clear()
    file4.close()
    #调用hungarian method, referece: https://github.com/maandree/hungarian-algorithm-n3
    os.system('./hungarian-algorithm-n3/hungarian ' + str(row_max) + ' ' + str(col_max) + ' < ' + h_input_filename + ' > hungarian_result.txt')
    file5 = open('hungarian_result.txt', 'r')
    str_count = file5.readlines()[-1]
    file5.close()
    #计算结果
    pairs = float(str_count[len('Count: '):-1])
    si = pairs / max(col_max, row_max)
    return si

#usage:
#python calc_si.py {[option] [name]}
#example1: python calc_si.py -f birthmark_folder -o result.txt
#example2: python calc_si.py -b birthmark1.txt birthmark2.txt -o result.txt
#[-f birthmark_folder]
#[-b birthmarkfile1 birthmarkfile2]
#[-o result_file]
if __name__ == '__main__':
    bm_filename_list = []
    obj_filename = ''
    e2lsh_result_folder = 'e2lsh_result'
    h_input_folder = 'h_input'
    #定义输入参数
    if '-f' in sys.argv:
        bm_folder = sys.argv[sys.argv.index('-f') + 1]
        if not os.path.exists(bm_folder):
            print('folder not exist --- ' + bm_folder)
            exit()
        else:
            h_input_folder = 'h_' + bm_folder
            e2lsh_result_folder = 'e_' + bm_folder
            obj_filename = bm_folder + '_result.txt'
            for f in os.listdir(bm_folder):
                if '.txt' == f[-4:len(f)]:
                    bm_filename_list.append(bm_folder + '/' + f) 
    if '-o' in sys.argv:
        obj_filename = sys.argv[sys.argv.index('-o') + 1]
    if '-b' in sys.argv:
        f1 = sys.argv[sys.argv.index('-b') + 1]
        f2 = sys.argv[sys.argv.index('-b') + 2]
        if not os.path.exists(f1):
            print('file not exist --- ' + f1)
            exit()
        elif not os.path.exists(f2):
            print('file not exist --- ' + f2)
            exit()
        else:
            bm_filename_list.append(f1)
            bm_filename_list.append(f2)
    if '-e' in sys.argv:
        e2lsh_result_folder = sys.argv[sys.argv.index('-e') + 1]
    if not os.path.exists(e2lsh_result_folder):
        os.mkdir(e2lsh_result_folder)
    if '-h' in sys.argv:
        h_input_folder = sys.argv[sys.argv.index('-h') + 1]
    if not os.path.exists(h_input_folder):
        os.mkdir(h_input_folder)
    result_set = {}
    
    #计算列表中每一对的相似度
    clone_cluster = []
    for i in range(0, len(bm_filename_list)):
        for j in range(i + 1, len(bm_filename_list)):
            print('Seq:', i, j)
            si = calc_si(bm_filename_list[i], bm_filename_list[j], e2lsh_result_folder + '/e_' + str(i) + '_' + str(j) + '.txt', h_input_folder + '/h_' + str(i) + '_' + str(j) + '.txt')
            result_set[(bm_filename_list[i], bm_filename_list[j])] = si
            print('similarity', i, j, ':', si)
            if si >= threshold:
                a, b = bm_filename_list[i], bm_filename_list[j]
                flag = False
                for c in clone_cluster:
                    if a in c or b in c:
                        c.add(a)
                        c.add(b)
                        flag = True
                        break
                if not flag:
                    clone_cluster.append({a, b})
    #输出结果到shell
    for item in result_set:
        print(item, result_set[item])
    print(clone_cluster)
    
    for f in bm_filename_list:
        print(f)

    #输出结果到文件
    if  obj_filename != '':
        obj_file = open(obj_filename, 'w')
        for item in result_set:
            obj_file.write(str(item))
            obj_file.write(': ')
            obj_file.write(str(result_set[item]))
            obj_file.write('\n')
        for s in clone_cluster:
            obj_file.write(str(s))
            obj_file.write('\n')
        obj_file.close()
