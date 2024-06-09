#-*- coding:utf-8 -*-
#svg标准参考https://www.w3.org/TR/SVG11/paths.html
#我对svg解析进行了一些兼容性扩展,下面是兼容性扩展更改(逗号指comma_wsp):
#扩充空白字符(按常见度排序)为[ \n\r\t\f\v](无歧义为[\x20\x0A\x0D\x09\x0c\x0b])
#所有仅空白的位置都可以用逗号了,数字(float)的格式更加自由,第一个命令可以不是m了(初始0,0)
#这些兼容性扩展主要是为了降低解析复杂性,提高兼容性只是附带的好处
#标准的的整体格式是: [空白] ( (<Move命令>[空白])+ [空白] (<其他命令>[空白])* )* [空白]
#标准的一条命令格式是: <命令字符> [空白] (<参数1> [逗号] <参数2> [逗号] <参数3> ... )*
#需要注意的是A命令参数中第一个flag前的逗号是必须的,否则会因为贪婪匹配被粘到上一个signed中
#完全按照标准解析会极大的增加解析复杂度,而下面是经过扩展的格式(此处括号代表解析时的结构):
#( ([逗号]<任意命令字符>) ([逗号]<参数1>) ([逗号]<参数2>) ... )*

#此模块的错误基类
class SvgError(Exception):pass
#解析svg时的错误
class SvgParseError(SvgError):pass
#解析path的d属性时的错误
class SvgPathDParseError(SvgError):pass


from re import compile
#一位数
digit = fr"[0123456789]"
#符号(-+)
sign = fr"[\x2d\x2b]"
#小数部分有四种格式: 整数+小数点(\x2e)+小数 整数+小数点 小数点+小数 整数
fraction = fr"(?:(?:{digit}+\x2e{digit}*)|(?:\x2e?{digit}+))"
#指数部分(不分大小写的e+可选符号+至少一位数字)
exponent = fr"(?:[eE]{sign}?{digit}+)"
#signed(float)的正则(可选正负号+必选小数部分+可选指数部分)
reSigned = compile(fr"{sign}?{fraction}{exponent}?")
#(\s)空白(空格,\n,\r,横tab,换页(标准有,但bnf定义没有),竖tab(标准没有))
wsp = fr"[\x20\x0A\x0D\x09\x0c\x0b]"
#分割符,逗号(\x2c)前后任意数量空白,可以没有
reComma=compile(fr"{wsp}*\x2c?{wsp}*")
del digit,sign,fraction,exponent,wsp,compile


#命令的信息(新命令字符(统一到大写),原来是否为小写(相对坐标),形参序列)
mapCommandParams = {
    "M": ("M", False, "ss"),
    "m": ("M", True, "ss"),
    "L": ("L", False, "ss"),
    "l": ("L", True, "ss"),
    "H": ("H", False, "s"),
    "h": ("H", True, "s"),
    "V": ("V", False, "s"),
    "v": ("V", True, "s"),
    "C": ("C", False, "ssssss"),
    "c": ("C", True, "ssssss"),
    "S": ("S", False, "ssss"),
    "s": ("S", True, "ssss"),
    "Q": ("Q", False, "ssss"),
    "q": ("Q", True, "ssss"),
    "T": ("T", False, "ss"),
    "t": ("T", True, "ss"),
    "A": ("A", False, "uusffss"),
    "a": ("A", True, "uusffss"),
}


#解析d部分,提取所有(x,y)坐标
def ParsePathD(d, l):
    #每一个m命令代表一个"子路径",首个m命令不区分大小写(我们用初始值0,0来实现)
    #z命令是划线到当前子路径的起始点,而不是整个path的起始点,并且每个子路径中可以有多个z
    #每个m命令的序列第2项往后被视为l命令,但例如"M1,1 M2,2"这样的两个序列则是两个子路径
    sub_x = 0
    sub_y = 0
    now_x = 0
    now_y = 0
    #去除一个逗号,下一个字符应该是命令字符
    p = 0
    while p < l:
        #因为逗号可以没有,所以匹配应该总是成功(没有则匹配出空字符串)
        p = reComma.match(d, p, l).end()
        n = d[p]
        p += 1
        #z命令没有参数
        if n in "Zz":
            now_x, now_y = sub_x, sub_y
            yield now_x, now_y
            continue
        #提取命令字符对应的参数序列
        n, low, seq = mapCommandParams.get(n, (None, None, None))
        if not n:
            raise SvgPathDParseError(f"endpos {p}: not a command")
        args = []
        #解析对应的参数序列
        while True:
            arg = []
            for t in seq:
                #去除一个逗号,随后匹配一个数据类型
                p = reComma.match(d, p, l).end()
                #flag
                if t == "f":
                    if not p < l:
                        break
                    if (t := d[p]) == "0":
                        arg.append(False)
                    elif t == "1":
                        arg.append(True)
                else:
                    #signed/unsigned都先匹配一个signed
                    if not (m := reSigned.match(d, p, l)):
                        break
                    p = m.end()
                    m = float(m.group())
                    #unsigned不能小于0
                    if t == "u" and m < 0:
                        raise SvgPathDParseError(f"endpos {p}: unsigned must >= 0")
                    #除此之外和signed没区别(注:非f/u均视为signed)
                    arg.append(m)
            #这一组参数列表是完整的(无break),然后继续搜索下一组
            else:
                args.append(arg)
                continue
            #这一组是不完整的,某个参数没有匹配到,退出while循环
            break
        #只有第一个参数就没匹配到时,才是正常退出
        if arg:
            raise SvgPathDParseError(f"endpos {p}: wrong params count, need {len(seq)} but {len(arg)}")
        #0组参数序列
        if not args:
            raise SvgPathDParseError(f"endpos {p}: empty command params")
        #仅处理我们感兴趣的数据(坐标)
        for arg in args:
            if n == "H":
                if low:
                    arg[0] += now_x
                now_x = arg[0]
            elif n == "V":
                if low:
                    arg[0] += now_y
                now_y = arg[0]
            else:
                if low:
                    arg[-2] += now_x
                    arg[-1] += now_y
                now_x = arg[-2]
                now_y = arg[-1]
                if n == "M":
                    sub_x = now_x
                    sub_y = now_y
                    #move序列的第二项往后被视为l命令
                    n = "L"
            yield now_x, now_y


#这是匹配字符的表,其他字体需要改表改函数,https://github.com/haua/svg-captcha-recognize
MapOfLength = {
    998:  "1",
    1081: "1",
    1082: "v",
    1130: "Y",
    1134: "Y",
    1172: "v",
    1224: "Y",
    1298: "V",
    1311: "V",
    1360: "i",
    1406: "V",
    1473: "i",
    1478: "T",
    1491: "r",
    1601: "T",
    1604: "X",
    1613: "x",
    1614: "N",
    1616: "N",
    1617: "N",
    1618: "N",
    1634: "k",
    1637: "k",
    1706: "K",
    1709: "K",
    1754: "F",
    1770: "k",
    1838: "u",
    1840: "A",
    1844: "A",
    1848: "K",
    1850: "Z",
    1853: "Z",
    1886: "h",
    1900: "F",
    1922: "H",
    1928: "H",
    1960: "P",
    1991: "u",
    1993: "A",
    1996: "D",
    2004: "Z",
    2018: "w",
    2035: "w",
    2042: "7",
    2043: "h",
    2080: "j",
    2082: "H",
    2104: "R",
    2107: "R",
    2123: "P",
    2140: "4",
    2162: "D",
    2164: "O",
    2183: "w",
    2199: "C",
    2200: "C",
    2201: "C",
    2202: "C",
    2210: "f",
    2212: "7",
    2246: "E",
    2253: "j",
    2260: "o",
    2272: "d",
    2282: "M",
    2294: "U",
    2301: "U",
    2310: "W",
    2321: "M",
    2332: "a",
    2344: "O",
    2345: "W",
    2346: "W",
    2366: "s",
    2380: "b",
    2382: "0",
    2394: "f",
    2433: "E",
    2448: "o",
    2461: "d",
    2464: "p",
    2466: "M",
    2485: "U",
    2498: "c",
    2501: "e",
    2503: "W",
    2512: "q",
    2526: "a",
    2546: "2",
    2563: "s",
    2578: "b",
    2580: "0",
    2606: "5",
    2632: "6",
    2669: "p",
    2706: "c",
    2709: "e",
    2721: "q",
    2758: "2",
    2800: "9",
    2823: "5",
    2851: "6",
    3033: "9",
    3038: "S",
    3054: "B",
    3160: "g",
    3244: "Q",
    3254: "Q",
    3266: "G",
    3291: "S",
    3308: "B",
    3414: "8",
    3423: "g",
    3514: "Q",
    3538: "G",
    3663: "m",
    3667: "m",
    3698: "8",
    3878: "3",
    3968: "m",
    4201: "3"
}


#最小y坐标
MapOfMinY = {
    986:  (lambda y: "I" if 13<y else "l"),
    1068: (lambda y: "I" if 13<y else "l"),
    1610: (lambda y: "x" if 19<y else "J"),
    1744: (lambda y: "x" if 19<y else "J"),
    1615: (lambda y: "r" if 18<y else "N"),
    2198: (lambda y: "n" if 19<y else "C"),
    2381: (lambda y: "n" if 19<y else "C"),
    1598: (lambda y: "X" if 13<y else "N"),
    1731: (lambda y: "X" if 13<y else "N"),
    1694: (lambda y: "z" if 22<y else "t"),
    1835: (lambda y: "z" if 22<y else "t"),
    2279: (lambda y: "R" if 13<y else "M")
}


#解析验证码(依赖xml解析驱动,expat使用回调的方式,所以需要给数据加句柄)
class Parser:
    def __init__(self):
        #储存了(x坐标,每个解析的字符),因为字符没有重叠的x座标部分,所以随便一个x座标就可以
        self.chars = []

    #仅捕获元素开始的事件,过滤出所有path元素的d属性(不论层级,并忽略命名空间)
    def start(self, name, attributes):
        d = attributes.get("d")
        if not (d and name.endswith("path")):
            return
        #第一个m命令的x和y是(chars的键(以前的FirstNumber)和以前的FirstMoveY)
        l = len(d)
        d = ParsePathD(d, l)
        x, y = next(d, (None,None))
        if not x:
            return
        #只需长度即可判断的
        char = MapOfLength.get(l)
        if char:
            pass
        #FirstMoveY
        elif l in (1274, 1380):
            char = "y" if 30<y else "L"
        #最小y座标
        elif (char := MapOfMinY.get(l)):
            miny = y
            for _, y in d:
                if y < miny:
                    miny = y
            char = char(miny)
        #字符宽度,x变量还要使用,所以此处y其实是x
        elif l == 2318:
            minx = x
            maxx = x
            for y, _ in d:
                if y < minx:
                    minx = y
                elif maxx < y:
                    maxx = y
            char = "W" if 30 < maxx-minx else "4"
        #没识别出字符则忽略
        else:
            return
        self.chars.append((x, char))


#获取验证码的接口
from xml.parsers.expat import ExpatError, ErrorString, ParserCreate
from operator import itemgetter
itemgetter = itemgetter(0)
def GetSvgCaptcha(svg):
    #由xml解析驱动识别
    g = ParserCreate()
    p = Parser()
    g.StartElementHandler = p.start
    try:
        g.Parse(svg, True)
    except ExpatError:
        raise SvgParseError(f"xml parse error at pos {g.ErrorByteIndex}: {ErrorString(g.ErrorCode)}")
    #根据[0]的x坐标排序字符
    p.chars.sort(key = itemgetter)
    return "".join(svg[1] for svg in p.chars)