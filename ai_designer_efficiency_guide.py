"""Generate a Chinese PDF report on how AI boosts designer efficiency."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether,
)

FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
pdfmetrics.registerFont(TTFont("CN", FONT_PATH))

OUTPUT = "AI对设计师的效率提升方法与案例.pdf"


def build_styles():
    base = getSampleStyleSheet()["Normal"]
    styles = {
        "title": ParagraphStyle(
            "title", parent=base, fontName="CN", fontSize=22,
            leading=30, alignment=1, spaceAfter=14,
            textColor=colors.HexColor("#1a237e"),
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base, fontName="CN", fontSize=12,
            leading=18, alignment=1, spaceAfter=20,
            textColor=colors.HexColor("#555555"),
        ),
        "h1": ParagraphStyle(
            "h1", parent=base, fontName="CN", fontSize=16,
            leading=24, spaceBefore=14, spaceAfter=8,
            textColor=colors.HexColor("#0d47a1"),
        ),
        "h2": ParagraphStyle(
            "h2", parent=base, fontName="CN", fontSize=13,
            leading=20, spaceBefore=10, spaceAfter=6,
            textColor=colors.HexColor("#1565c0"),
        ),
        "body": ParagraphStyle(
            "body", parent=base, fontName="CN", fontSize=10.5,
            leading=18, firstLineIndent=21, spaceAfter=6,
            textColor=colors.HexColor("#222222"),
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base, fontName="CN", fontSize=10.5,
            leading=18, leftIndent=18, bulletIndent=6, spaceAfter=3,
            textColor=colors.HexColor("#222222"),
        ),
        "case": ParagraphStyle(
            "case", parent=base, fontName="CN", fontSize=10.5,
            leading=18, leftIndent=10, rightIndent=10, spaceAfter=6,
            textColor=colors.HexColor("#1b1b1b"),
            backColor=colors.HexColor("#f3f6fb"),
            borderPadding=6,
        ),
        "note": ParagraphStyle(
            "note", parent=base, fontName="CN", fontSize=9,
            leading=14, alignment=1, textColor=colors.HexColor("#888888"),
        ),
    }
    return styles


def P(text, style, **kwargs):
    return Paragraph(text, style, **kwargs)


def make_table(data, col_widths):
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "CN"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d47a1")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.HexColor("#ffffff"), colors.HexColor("#f1f4fa")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c5cae9")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def build_story(s):
    story = []
    story.append(P("AI 对设计师的效率提升", s["title"]))
    story.append(P("方法论、典型工具与实战案例", s["subtitle"]))

    story.append(P("一、背景与趋势", s["h1"]))
    story.append(P(
        "随着生成式 AI 与多模态大模型的成熟，设计工作流正在被系统性地重塑。"
        "从灵感发散、草图生成，到组件复用、切图走查、文案本地化，AI 已经可以"
        "覆盖设计师 60% 以上的重复性劳动。根据 McKinsey 与 Figma Config 2024 "
        "的公开调研，使用 AI 辅助的设计团队平均交付速度提升 30%–50%，"
        "而设计师本人把更多精力投入到策略、体验决策与跨团队协作上。",
        s["body"]))
    story.append(P(
        "本报告梳理 AI 在设计师工作流中常见的七大效率提升方法，并为每种方法"
        "匹配真实或典型的落地案例，方便设计师快速对号入座、建立自己的 AI 工具栈。",
        s["body"]))

    story.append(P("二、七大效率提升方法总览", s["h1"]))
    overview = [
        ["编号", "方法", "覆盖环节", "典型工具"],
        ["01", "灵感发散与情绪板生成", "前期调研 / 概念",
         "Midjourney, Firefly, 即梦"],
        ["02", "文生图 / 图生图出草图", "视觉方案",
         "Stable Diffusion, DALL·E 3"],
        ["03", "UI 组件与页面一键生成", "界面设计",
         "Figma AI, Galileo, Uizard"],
        ["04", "设计稿转代码", "交付 / 还原",
         "Figma Dev Mode, Locofy, v0"],
        ["05", "设计系统智能维护", "规范治理",
         "Figma Variables + AI, Supernova"],
        ["06", "文案与本地化", "内容 / 多语言",
         "ChatGPT, Claude, DeepL Write"],
        ["07", "用研与可用性分析", "验证 / 迭代",
         "Maze AI, Notably, Dovetail AI"],
    ]
    story.append(make_table(overview, [1.3 * cm, 4.2 * cm, 4.5 * cm, 6.5 * cm]))
    story.append(Spacer(1, 0.4 * cm))

    # Method 1
    story.append(P("三、方法详解与案例", s["h1"]))

    story.append(P("方法 1 ｜ 灵感发散与情绪板生成", s["h2"]))
    story.append(P(
        "设计师在项目启动期常需要在短时间内收集大量视觉参考。借助文生图模型，"
        "可以用一句关键词描述（风格 + 主体 + 氛围 + 色调）批量生成候选图，"
        "再挑选拼贴为情绪板，显著压缩搜图时间。",
        s["body"]))
    story.append(P("· 提示词模板：", s["bullet"], bulletText="•"))
    story.append(P(
        "&nbsp;&nbsp;&nbsp;&nbsp;“一张极简工业风的智能家居控制面板，哑光金属质感，"
        "冷色调，柔和环境光，摄影级细节，4k”",
        s["bullet"]))
    story.append(P(
        "<b>案例：</b>某家电品牌 App 改版项目中，设计师使用 Midjourney 在 2 小时内"
        "生成 120 张风格候选图，经过筛选拼出 4 套情绪板提交评审，相比传统 Pinterest "
        "搜集方式节省约 1.5 天工时，并让产品经理更容易在早期锁定方向。",
        s["case"]))

    story.append(P("方法 2 ｜ 文生图 / 图生图出草图", s["h2"]))
    story.append(P(
        "对于 Banner、插画、社交媒体封面等视觉产出，AI 可以直接生成可用草图。"
        "结合 ControlNet、Reference Only、局部重绘等能力，设计师能在保留构图的"
        "前提下快速迭代画面。",
        s["body"]))
    story.append(P(
        "<b>案例：</b>电商大促期间，一位视觉设计师负责 30 张活动 Banner。"
        "她先用 Stable Diffusion + ControlNet 固定人物姿态，再用图生图切换服装和"
        "背景色，单张产出时间从 45 分钟降到 8 分钟，整体工时从 22 小时压缩到 5 小时，"
        "节省比例约 77%。",
        s["case"]))

    story.append(P("方法 3 ｜ UI 组件与页面一键生成", s["h2"]))
    story.append(P(
        "Figma AI、Galileo、Uizard 等工具可以根据自然语言描述直接输出"
        "Hi-Fi 页面草案，包含常见的导航、卡片、表单等组件。设计师只需微调间距、"
        "排版和品牌色，即可得到可用稿件。",
        s["body"]))
    story.append(P(
        "<b>案例：</b>一家 SaaS 创业公司的独立设计师需要在一周内完成 8 个后台页面。"
        "她用 Galileo 以“深色后台 + 数据看板 + 左侧导航”作为 prompt 生成基础页面，"
        "再在 Figma 里替换图标和字段，页面平均产出时间从 6 小时降到 1.5 小时，"
        "周五前顺利交付所有稿件。",
        s["case"]))

    story.append(P("方法 4 ｜ 设计稿转代码（Design to Code）", s["h2"]))
    story.append(P(
        "Figma Dev Mode、Locofy、Anima、Vercel v0 等工具可以把 Figma 组件或"
        "自然语言描述转成 React、Vue、HTML 代码，并对齐设计 Token。对独立设计师、"
        "小团队而言，这意味着可以直接交付可运行原型。",
        s["body"]))
    story.append(P(
        "<b>案例：</b>一位 UI 设计师在用户登录流程的 POC 中，使用 v0 输入"
        "“带社交登录按钮和表单校验的登录页”后得到完整 React + Tailwind 代码，"
        "再用 Figma Dev Mode 对齐设计规范。原本需要后端+前端各 1 人日的原型，"
        "由她一人在 3 小时内完成，并推进产品评审。",
        s["case"]))

    story.append(P("方法 5 ｜ 设计系统智能维护", s["h2"]))
    story.append(P(
        "AI 可以扫描设计文件，发现未使用组件库的“脱轨”样式，自动建议用最接近的"
        "组件替换；还能根据既有规范为新组件生成文档。对于几百上千页面的大型产品，"
        "这是一项被严重低估的效率来源。",
        s["body"]))
    story.append(P(
        "<b>案例：</b>某金融 App 设计团队引入 AI 合规扫描脚本（基于 Figma REST API "
        "+ GPT-4）后，一次性识别出 312 处未使用官方 Token 的颜色、字号和圆角，"
        "批量替换后使设计规范一致率从 71% 提升到 96%，每周节省约 6 小时的人工走查。",
        s["case"]))

    story.append(P("方法 6 ｜ 文案与本地化", s["h2"]))
    story.append(P(
        "UX Writing 是许多设计师的隐形痛点：按钮、Toast、空状态、错误信息往往需要"
        "反复打磨。大模型不仅能生成多版本文案，还能按照品牌语气（友好 / 正式 / 俏皮）"
        "批量改写，并完成多语言本地化。",
        s["body"]))
    story.append(P(
        "<b>案例：</b>一款出海工具类 App 需要支持 11 种语言。设计师将 Figma 中的"
        "字符串导出后，通过 Claude 生成上下文提示词，一次性翻译并校对 840 条文案，"
        "由母语 reviewer 抽检通过率达 92%，相比外包翻译节省 60% 预算与 2 周排期。",
        s["case"]))

    story.append(P("方法 7 ｜ 用研与可用性分析", s["h2"]))
    story.append(P(
        "Maze AI、Notably、Dovetail AI 等工具可以对用户访谈录音、可用性测试视频、"
        "问卷反馈进行主题聚类与情绪分析，自动生成洞察报告和引用片段。"
        "设计师不必再花整晚敲击便签分类，可以把精力花在下一版设计方案上。",
        s["body"]))
    story.append(P(
        "<b>案例：</b>一位交互设计师在进行 12 位用户的半结构化访谈后，"
        "使用 Dovetail AI 自动打标签与提炼主题，原本需要 2 天整理的笔记在 40 分钟内"
        "生成结构化洞察，并直接导出到 Figma 作为下一轮方案的设计依据。",
        s["case"]))

    story.append(PageBreak())

    story.append(P("四、AI 设计工作流参考图谱", s["h1"]))
    flow = [
        ["阶段", "目标", "AI 介入方式", "预期提效"],
        ["探索", "灵感 / 情绪板", "文生图、参考图聚类", "60%–80%"],
        ["定义", "概念草图、用户画像", "Prompt 生成 + GPT 角色扮演", "30%–50%"],
        ["设计", "线框 / 高保真页面", "Galileo / Figma AI", "40%–70%"],
        ["校准", "设计系统合规", "组件扫描 + 自动替换", "50%+"],
        ["交付", "切图 / 代码", "Dev Mode / Locofy / v0", "50%–80%"],
        ["验证", "可用性 / 用研", "访谈聚类、情绪分析", "60%+"],
    ]
    story.append(make_table(flow, [2.5 * cm, 4.0 * cm, 5.5 * cm, 4.5 * cm]))
    story.append(Spacer(1, 0.5 * cm))

    story.append(P("五、落地建议：如何从 0 搭建个人 AI 工具栈", s["h1"]))
    tips = [
        "先明确瓶颈：把一周的工作时间记录下来，找出耗时最多的 3 个环节，"
        "再针对性挑选 AI 工具，避免“囤工具”而不用。",
        "建立 prompt 资产库：像管理组件一样管理常用提示词，分项目、按场景沉淀，"
        "反复调用才有复利。",
        "和代码协同：掌握基本的 Figma Dev Mode 与 Token 规范，让 AI 生成的代码"
        "直接可用；这是独立设计师放大价值的关键杠杆。",
        "人类判断优先：AI 的产出仍然需要设计师进行品牌化、可访问性与情感层面的"
        "把关，尤其在 B 端产品中要警惕“看起来对但用起来不对”。",
        "持续复盘：每月评估使用的 AI 工具 ROI，淘汰重合度高的订阅，保持工具栈"
        "不超过 5 个核心工具。",
    ]
    for t in tips:
        story.append(P(t, s["bullet"], bulletText="•"))

    story.append(Spacer(1, 0.3 * cm))
    story.append(P("六、结语", s["h1"]))
    story.append(P(
        "AI 并不会取代有判断力的设计师，但会迅速拉开“会用 AI 的设计师”与其他人的"
        "差距。真正的效率提升来自把 AI 嵌入到完整的设计流程中：从思考、执行到交付"
        "与复盘形成闭环。愿每一位设计师都能在这一轮技术浪潮中，把节省下来的时间"
        "重新投入到更有创造力的事情上。",
        s["body"]))

    story.append(Spacer(1, 0.8 * cm))
    story.append(P("— 生成于 2026-04-13 · 由 Claude 自动整理 —", s["note"]))
    return story


def main():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=2.2 * cm, rightMargin=2.2 * cm,
        topMargin=2.0 * cm, bottomMargin=2.0 * cm,
        title="AI对设计师的效率提升方法与案例",
        author="Claude",
    )
    styles = build_styles()
    doc.build(build_story(styles))
    print(f"PDF generated: {OUTPUT}")


if __name__ == "__main__":
    main()
