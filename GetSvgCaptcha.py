#-*- coding:utf-8 -*-
#验证码识别仅可用于默认字体,其他字体需要改表,https://github.com/haua/svg-captcha-recognize
from decimal import Decimal
from re import compile
#提取所有数字,返回一个可迭代对象
reGetAllNumber=compile(r"[0-9]{1,}(?:\.[0-9]{1,}){0,1}")
GetAllNumber=reGetAllNumber.finditer
#获取第一个move指令(m/M<x> <y>)中的y座标
reGetFirstMoveY=compile(r"[Mm][0-9]{1,}(?:\.[0-9]{1,}){0,1}\x20[0-9]{1,}(?:\.[0-9]{1,}){0,1}")
def GetFirstMoveY(path):
    return Decimal(reGetFirstMoveY.search(path).group().split(" ")[1])
#解析出svg中所有的path的d部分,返回一个可迭代对象
#正则:找到path中的 d="..." 部分([^"]代表除了双引号外的所有字符),然后去掉前3和后1字节
reGetAllPath=compile(r"d=\x22[^\x22]{1,}\x22")
def GetAllPath(svg):
    for path in reGetAllPath.finditer(svg):
        yield path.group()[3:-1:]
#获取所有数字中的第一个(必然是x座标)
def GetFirstNumber(path):
    return Decimal(reGetAllNumber.search(path).group())
#获取最小的y座标
def GetMinY(path):
    #代表当前数字是否是一个y座标(数字是成对出现的,下标为奇数的必然是y座标)
    flag=False
    nums=GetAllNumber(path)
    #跳过第一个数字(必然是x座标),flag=True
    nums.__next__()
    #取第二个数字(必然是y座标),flag=False
    y=Decimal(nums.__next__().group())
    #遍历所有数字
    for number in nums:
        #如果这个是y座标
        if flag:
            number=Decimal(number.group())
            #更新最小的y值
            if number<y:
                y=number
        flag=not flag
    return y
#获取字符宽度
def GetWidth(path):
    #代表当前数字是否是一个x座标
    flag=False
    nums=GetAllNumber(path)
    #最小和最大x值,两个相减就是宽度(这里只调用了一次next,所以flag的含义和GetMinY里的相反)
    minx=maxx=Decimal(nums.__next__().group())
    for number in nums:
        if flag:
            number=Decimal(number.group())
            #更新最小或最大x值
            if number<minx:
                minx=number
            elif maxx<number:
                maxx=number
        flag=not flag
    return maxx-minx
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
#上面找不到就来这里找,这里获取的对象要进行函数调用,传入path,返回对应字符
MapOfInputPath={
    #找最小的y座标
    986:  (lambda path:"I" if 13<GetMinY(path) else "l"),
    1068: (lambda path:"I" if 13<GetMinY(path) else "l"),
    1610: (lambda path:"x" if 19<GetMinY(path) else "J"),
    1744: (lambda path:"x" if 19<GetMinY(path) else "J"),
    1615: (lambda path:"r" if 18<GetMinY(path) else "N"),
    2198: (lambda path:"n" if 19<GetMinY(path) else "C"),
    2381: (lambda path:"n" if 19<GetMinY(path) else "C"),
    1598: (lambda path:"X" if 13<GetMinY(path) else "N"),
    1731: (lambda path:"X" if 13<GetMinY(path) else "N"),
    1694: (lambda path:"z" if 22<GetMinY(path) else "t"),
    1835: (lambda path:"z" if 22<GetMinY(path) else "t"),
    2279: (lambda path:"R" if 13<GetMinY(path) else "M"),

    #找第一个move指令的y座标
    1274: (lambda path:"y" if 30<GetFirstMoveY(path) else "L"),
    1380: (lambda path:"y" if 30<GetFirstMoveY(path) else "L"),

    #找宽度
    2318: (lambda path:"W" if 30<GetWidth(path) else "4")
}
#获取验证码的接口
def GetSvgCaptcha(svg):
    #值储存了每个解析的字符,键是它最左边的x座标
    chars={}
    for path in GetAllPath(svg):
        svg=len(path)
        #去每个表里找有没有这个字符
        if svg in MapOfPathLength:
            chars[GetFirstNumber(path)] = MapOfPathLength[svg]
        elif svg in MapOfInputPath:
            chars[GetFirstNumber(path)] = MapOfInputPath[svg](path)
        #没找到,视作噪点
    #用键(它最左边的x座标)对所有字符排序并组合
    return "".join(chars[path] for path in sorted(chars))