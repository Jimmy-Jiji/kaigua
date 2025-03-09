from flask import Flask, render_template, request, jsonify
import random
import time
from openai import OpenAI

app = Flask(__name__)

# 配置 OpenAI 兼容通义千问 API
DASHSCOPE_API_KEY = "sk-e34d2c9281604113afc360d1a9f78136"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

client = OpenAI(api_key=DASHSCOPE_API_KEY, base_url=BASE_URL)

# 64个卦象
HEXAGRAMS = {
    "乾为天": {"description": "象征天，代表创造力和刚健。", "fortune": "大吉卦"},
    "坤为地": {"description": "象征地，代表包容力和柔顺。", "fortune": "吉卦"},
    "水雷屯": {"description": "象征困难初生，需耐心等待。", "fortune": "凶卦"},
    "山水蒙": {"description": "象征启蒙，代表学习和教育。", "fortune": "平卦"},
    "水天需": {"description": "象征等待，时机未到需耐心。", "fortune": "吉卦"},
    "天水讼": {"description": "象征争讼，提醒避免冲突。", "fortune": "大凶卦"},
    "地水师": {"description": "象征军队，代表组织和纪律。", "fortune": "吉卦"},
    "水地比": {"description": "象征亲近，代表和谐与合作。", "fortune": "吉卦"},
    "风天小畜": {"description": "象征积蓄力量，代表渐进发展。", "fortune": "吉卦"},
    "天泽履": {"description": "象征行为规范，提醒遵循礼仪。", "fortune": "平卦"},
    "地天泰": {"description": "象征通达，代表顺利和成功。", "fortune": "大吉卦"},
    "天地否": {"description": "象征闭塞，提醒谨慎行事。", "fortune": "大凶卦"},
    "天火同人": {"description": "象征团结，代表合作与互助。", "fortune": "吉卦"},
    "火天大有": {"description": "象征丰收，代表成就和收获。", "fortune": "大吉卦"},
    "地山谦": {"description": "象征谦虚，提醒保持低调。", "fortune": "吉卦"},
    "雷地豫": {"description": "象征愉悦，代表欢乐和满足。", "fortune": "平卦"},
    "泽雷随": {"description": "象征随和，提醒顺应环境。", "fortune": "吉卦"},
    "山风蛊": {"description": "象征问题，提醒解决隐患。", "fortune": "凶卦"},
    "地泽临": {"description": "象征临近，代表机会到来。", "fortune": "吉卦"},
    "风地观": {"description": "象征观察，提醒审时度势。", "fortune": "平卦"},
    "火雷噬嗑": {"description": "象征决断，提醒果断行动。", "fortune": "吉卦"},
    "山火贲": {"description": "象征装饰，代表外在表现。", "fortune": "平卦"},
    "山地剥": {"description": "象征剥落，提醒注意衰退。", "fortune": "大凶卦"},
    "地雷复": {"description": "象征复兴，代表重新开始。", "fortune": "吉卦"},
    "天雷无妄": {"description": "象征无妄，提醒实事求是。", "fortune": "平卦"},
    "山天大畜": {"description": "象征积蓄，代表积累资源。", "fortune": "吉卦"},
    "山雷颐": {"description": "象征养育，提醒关注健康。", "fortune": "吉卦"},
    "泽风大过": {"description": "象征过度，提醒避免极端。", "fortune": "凶卦"},
    "坎为水": {"description": "象征险难，代表挑战和考验。", "fortune": "大凶卦"},
    "离为火": {"description": "象征光明，代表热情和希望。", "fortune": "吉卦"},
    "泽山咸": {"description": "象征感应，提醒敏锐感知。", "fortune": "平卦"},
    "雷风恒": {"description": "象征恒久，代表坚持和稳定。", "fortune": "吉卦"},
    "天山遁": {"description": "象征退避，提醒适时隐退。", "fortune": "平卦"},
    "雷天大壮": {"description": "象征壮大，代表力量和成长。", "fortune": "吉卦"},
    "火地晋": {"description": "象征晋升，代表进步和发展。", "fortune": "大吉卦"},
    "地火明夷": {"description": "象征受伤，提醒小心保护。", "fortune": "凶卦"},
    "风火家人": {"description": "象征家庭，代表和睦与责任。", "fortune": "吉卦"},
    "火泽睽": {"description": "象征分离，提醒化解矛盾。", "fortune": "凶卦"},
    "水山蹇": {"description": "象征艰难，提醒克服障碍。", "fortune": "大凶卦"},
    "雷水解": {"description": "象征解除，代表解决问题。", "fortune": "吉卦"},
    "山泽损": {"description": "象征损失，提醒减少消耗。", "fortune": "凶卦"},
    "风雷益": {"description": "象征增益，代表收获和成长。", "fortune": "吉卦"},
    "泽天夬": {"description": "象征决断，提醒果断决策。", "fortune": "吉卦"},
    "天风姤": {"description": "象征相遇，代表机遇和缘分。", "fortune": "吉卦"},
    "泽地萃": {"description": "象征聚集，代表合作和团队。", "fortune": "吉卦"},
    "地风升": {"description": "象征上升，代表进步和提升。", "fortune": "吉卦"},
    "泽水困": {"description": "象征困境，提醒寻求突破。", "fortune": "凶卦"},
    "水风井": {"description": "象征源泉，代表持续供给。", "fortune": "吉卦"},
    "泽火革": {"description": "象征变革，提醒主动改变。", "fortune": "吉卦"},
    "火风鼎": {"description": "象征更新，代表改革和创新。", "fortune": "大吉卦"},
    "震为雷": {"description": "象征震动，代表警醒和变化。", "fortune": "平卦"},
    "艮为山": {"description": "象征静止，提醒稳重和守成。", "fortune": "平卦"},
    "风山渐": {"description": "象征渐进，代表逐步发展。", "fortune": "吉卦"},
    "雷泽归妹": {"description": "象征归宿，代表找到方向。", "fortune": "吉卦"},
    "雷火丰": {"description": "象征丰盛，代表繁荣和富足。", "fortune": "大吉卦"},
    "火山旅": {"description": "象征旅行，提醒适应变化。", "fortune": "平卦"},
    "巽为风": {"description": "象征柔和，代表灵活和顺从。", "fortune": "平卦"},
    "兑为泽": {"description": "象征喜悦，代表快乐和满足。", "fortune": "吉卦"},
    "风水涣": {"description": "象征散开，提醒分散风险。", "fortune": "平卦"},
    "水泽节": {"description": "象征节制，提醒控制欲望。", "fortune": "吉卦"},
    "风泽中孚": {"description": "象征诚信，代表信任和承诺。", "fortune": "吉卦"},
    "雷山小过": {"description": "象征小过，提醒注意细节。", "fortune": "凶卦"},
    "水火既济": {"description": "象征成功，代表完成和圆满。", "fortune": "大吉卦"},
    "火水未济": {"description": "象征未完成，提醒继续努力。", "fortune": "凶卦"}
}

def spin_wheel():
    """随机抽取一个卦象"""
    return random.choice(list(HEXAGRAMS.keys()))

def call_qwen_model(hexagram, question):
    """调用通义千问API进行解卦"""
    try:
        completion = client.chat.completions.create(
            model="qwen-max-latest",
            messages=[
                {'role': 'system', 'content': '你是一个解卦助手，能够根据卦象和问题提供详细的解答。'},
                {'role': 'user', 'content': f"卦象：{hexagram}\n问题：{question}\n请提供解卦。"}
            ],
            max_tokens=800
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"发生错误：{str(e)}"

@app.route("/")
def index():
    """加载网页"""
    return render_template("index.html")

@app.route("/spin", methods=["GET"])
def spin():
    """API: 生成随机卦象"""
    hexagram = spin_wheel()
    return jsonify({"hexagram": hexagram, "description": HEXAGRAMS[hexagram]["description"], "fortune": HEXAGRAMS[hexagram]["fortune"]})

@app.route("/interpret", methods=["POST"])
def interpret():
    """API: 解卦"""
    data = request.json
    hexagram = data.get("hexagram")
    question = data.get("question")
    if not hexagram or not question:
        return jsonify({"error": "请提供卦象和问题"}), 400
    response = call_qwen_model(hexagram, question)
    return jsonify({"interpretation": response})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # 获取 Render 提供的端口
    app.run(host='0.0.0.0', port=port, debug=True)

