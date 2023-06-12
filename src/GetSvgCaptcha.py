#-*- coding:utf-8 -*-
from re import compile
#使用decimal,将数字类型储存为无限精度的小数,更加保险,也可以使用float来获取更高性能
from decimal import Decimal as ToNumber
#ToNumber=float

#这是一些对path中数字(浮点数,必选的整数部分,和可选的小数点加数字部分)进行分析的函数
#提取所有数字,返回一个可迭代对象
rawInt=fr"[0-9]{{1,}}"
reInt=compile(rawInt)
rawFloat=fr"{rawInt}(?:\.{rawInt}){{0,1}}"
reFloat=compile(rawFloat)
def GetAllNumber(path):
    for path in reFloat.finditer(path):
        yield ToNumber(path.group())
#获取第一个数字(必然是x座标)
def GetFirstNumber(path):
    return ToNumber(reFloat.search(path).group())
#分析所有数字,返回(first,minx,maxx,miny,maxy),节省遍历次数
def UnpackAllNumber(path):
    a=GetAllNumber(path)
    b=True
    #取前两个值作为min/maxx和min/maxy
    first=minx=maxx=next(a)
    miny=maxy=next(a)
    for path in a:
        #这个值是否是x座标(偶数下标是x,奇数下标是y)
        if b:
            if path<minx:
                minx=path
            else:
                maxx=path
            b=False
        else:
            if path<miny:
                miny=path
            else:
                maxy=path
            b=True
    return first,minx,maxx,miny,maxy

#这是一些对svg/path进行解析的函数
#解析出svg中所有的path的d部分(d="<catch this>"),返回一个可迭代对象
rawPath=fr"d=\x22([^\x22]{{1,}})\x22"
rePath=compile(rawPath)
def GetAllPath(svg):
    for svg in rePath.finditer(svg):
        yield svg.group(1)
#获取第一个move指令(m/M<x> <y(catch this)>)中的y座标
rawMoveY=fr"[Mm]{rawFloat}\x20({rawFloat})"
reMoveY=compile(rawMoveY)
def GetFirstMoveY(path):
    return ToNumber(reMoveY.search(path).group(1))

#这是匹配字符的表,默认字体,其他字体需要改表改函数,https://github.com/haua/svg-captcha-recognize
#path长度唯一的字符
MapOfPathLength={
    998:"1",
    1081:"1",
    1082:"v",
    1130:"Y",
    1134:"Y",
    1172:"v",
    1224:"Y",
    1298:"V",
    1311:"V",
    1360:"i",
    1406:"V",
    1473:"i",
    1478:"T",
    1491:"r",
    1601:"T",
    1604:"X",
    1613:"x",
    1614:"N",
    1616:"N",
    1617:"N",
    1618:"N",
    1634:"k",
    1637:"k",
    1706:"K",
    1709:"K",
    1754:"F",
    1770:"k",
    1838:"u",
    1840:"A",
    1844:"A",
    1848:"K",
    1850:"Z",
    1853:"Z",
    1886:"h",
    1900:"F",
    1922:"H",
    1928:"H",
    1960:"P",
    1991:"u",
    1993:"A",
    1996:"D",
    2004:"Z",
    2018:"w",
    2035:"w",
    2042:"7",
    2043:"h",
    2080:"j",
    2082:"H",
    2104:"R",
    2107:"R",
    2123:"P",
    2140:"4",
    2162:"D",
    2164:"O",
    2183:"w",
    2199:"C",
    2200:"C",
    2201:"C",
    2202:"C",
    2210:"f",
    2212:"7",
    2246:"E",
    2253:"j",
    2260:"o",
    2272:"d",
    2282:"M",
    2294:"U",
    2301:"U",
    2310:"W",
    2321:"M",
    2332:"a",
    2344:"O",
    2345:"W",
    2346:"W",
    2366:"s",
    2380:"b",
    2382:"0",
    2394:"f",
    2433:"E",
    2448:"o",
    2461:"d",
    2464:"p",
    2466:"M",
    2485:"U",
    2498:"c",
    2501:"e",
    2503:"W",
    2512:"q",
    2526:"a",
    2546:"2",
    2563:"s",
    2578:"b",
    2580:"0",
    2606:"5",
    2632:"6",
    2669:"p",
    2706:"c",
    2709:"e",
    2721:"q",
    2758:"2",
    2800:"9",
    2823:"5",
    2851:"6",
    3033:"9",
    3038:"S",
    3054:"B",
    3160:"g",
    3244:"Q",
    3254:"Q",
    3266:"G",
    3291:"S",
    3308:"B",
    3414:"8",
    3423:"g",
    3514:"Q",
    3538:"G",
    3663:"m",
    3667:"m",
    3698:"8",
    3878:"3",
    3968:"m",
    4201:"3"
}
#多个字符path长度相等,这里获取的对象要进行函数调用,传入最小y,返回对应字符
MapOfInputMinY={
    986:  (lambda y:"I" if 13<y else "l"),
    1068: (lambda y:"I" if 13<y else "l"),
    1610: (lambda y:"x" if 19<y else "J"),
    1744: (lambda y:"x" if 19<y else "J"),
    1615: (lambda y:"r" if 18<y else "N"),
    2198: (lambda y:"n" if 19<y else "C"),
    2381: (lambda y:"n" if 19<y else "C"),
    1598: (lambda y:"X" if 13<y else "N"),
    1731: (lambda y:"X" if 13<y else "N"),
    1694: (lambda y:"z" if 22<y else "t"),
    1835: (lambda y:"z" if 22<y else "t"),
    2279: (lambda y:"R" if 13<y else "M")
}

#将map转换为tuple来加快取值(因为键都是数字,没有的索引用None填充)
def compile(map):
    #取最大的长度键作为tuple长度
    temp=[None]*(max(map)+1)
    for length in map:
        temp[length]=map[length]
    #还返回一个所有有效索引的集合
    return frozenset(map),tuple(temp)
#执行
SetOfPathLength,MapOfPathLength=compile(MapOfPathLength)
SetOfInputMinY,MapOfInputMinY=compile(MapOfInputMinY)
#所有有效值的集合,用来剔除噪点
SetOfAll=frozenset({2318,1274,1380}|SetOfPathLength|SetOfInputMinY)

#获取验证码的接口
def GetSvgCaptcha(svg):
    #值储存了每个解析的字符,键是它的FirstNumber(因为字符没有重叠的x座标部分,所以随便一个x座标就可以)
    chars={}
    for path in GetAllPath(svg):
        svg=len(path)
        #没找到,视作噪点
        if svg not in SetOfAll:
            continue
        #去每个表里找对应长度(元素极少的不用表了)
        if svg in SetOfPathLength:
            #这个表不需要遍历数字
            chars[GetFirstNumber(path)] = MapOfPathLength[svg]
            continue
        if svg==1274 or svg==1380:
            #GetFirstMoveY(放在前面,不需要遍历所有数字)
            chars[GetFirstNumber(path)]="y" if 30<GetFirstMoveY(path) else "L"
            continue
        #剩下的需要分析所有数字
        first,minx,maxx,miny,maxy=UnpackAllNumber(path)
        if svg in SetOfInputMinY:
            #最小y座标
            chars[first] = MapOfInputMinY[svg](miny)
        if svg==2318:
            #字符宽度
            chars[first]="W" if 30<maxx-minx else "4"
    #排序字符
    return "".join(chars[svg] for svg in sorted(chars))

del compile,rawInt,rawFloat,rawPath,rawMoveY