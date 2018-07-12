
import openpyxl
import numpy as np
import math
import matplotlib.pyplot as plt

index=[]

def readxsl(path):
    index=[]
    wb = openpyxl.load_workbook(path)

    sheet = wb.get_sheet_by_name('Sheet1')  # 获取工作表

    for column in sheet.columns:
        for cell in column:

           index.append(cell.value)

    return index

def gaosi(a,b):

     o=a#标准差

     r=b#模糊半径

     sig=math.sqrt(o)

     arr=[]

     sum=0

     for x in range(0-r,r+1,1):

        y=np.exp(- (x ** 2 / (2 * sig ** 2))) / (math.sqrt(2 * math.pi) * sig)
        arr.append(y)

        sum=sum+y

     re=arr/sum#归一化

     return re

def dim(a,g):

    arr=a#被模糊的一维数组
    gao=g#高斯滤波器



    r=1#模糊半径

    re=[]

    sum=0

    for i in range(0,len(arr),1):
        #左边缘
        if i<r:
            for j in range(0,i+r+1):
                sum = sum + gao[r-i+j]*arr[j]
            for k in range(0,r-i):
                sum=sum+gao[k]*arr[0]
        #右边缘
        elif i>=len(arr)-r:
            for j in range(i-r,len(arr),1):
                sum= sum+gao[r-i+j]*arr[j]
            for k in range(len(arr)-i+r,2*r+1,1):
                sum= sum+gao[k]*arr[len(arr)-1]

        #非边缘
        elif r<=i<len(arr)-r:
            for j in range(i-r,i+r+1):
                sum=sum+gao[j-i+r]*arr[j]

        re.append(sum)

        sum=0

    return re

def get_gauss(path):
    # path='C:/Users/wzy/Desktop/暑期实训/1.xlsx'
    y = readxsl(path)
    g=gaosi(1,1)
    z=dim(y,g)

    x=np.arange(1,len(z)+1)

    plt.plot(x,y,'r',label='2')
    plt.plot(x,z,'b',label='1')

    plt.show()
    return x,z


if __name__=='__main__':
    get_gauss('C:/Users/wzy/Desktop/暑期实训/1.xlsx')