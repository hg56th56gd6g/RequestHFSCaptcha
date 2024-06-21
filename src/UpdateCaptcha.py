from GetSvgCaptcha import GetSvgCaptcha, itemgetter
from Sender import Sender
import webbrowser, asyncio, sys

def Draw(data):
    raw = GetSvgCaptcha(data)
    code = "".join(c[1] for c in sorted(raw, key = itemgetter))
    html = f"<html><body>{data}<h1>{raw}</h1><h1>{code}</h1></body></html>"
    open("svg.html", "w").write(html)
    webbrowser.open("svg.html")

if len(sys.argv) > 1:
    Draw(open(sys.argv[1], "r").read())
else:
    async def Main():
        sd = Sender(1)
        sd.NewPhone()
        sd.Connect()
        while True:
            Draw(await sd.NewSvg())
            input()

    asyncio.run(Main())