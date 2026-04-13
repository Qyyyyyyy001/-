# Colors 颜色规范

> 来源 Figma 节点: `1:393` (Color)

颜色 token 采用三层结构：

1. **Primitive（原色阶）** — 例如 `Magenta-1` ~ `Magenta-7`、`Neutral-1` ~ `Neutral-12`
2. **Semantic（语义色）** — 例如 `Text/Text - Primary`、`Background/Bg-Primary`、`Brand/Brand color`
3. **Component（组件色 CSS 变量）** — 例如 `--color-cmpt-button-primary`、`--color-cmpt-button-soft-disable`

## 1. 语义色（Semantic Tokens）

### 1.1 文本 Text

| Token | 值 | 用途 |
| --- | --- | --- |
| `Text/Text - Primary` | `#070808` | 主要文字（标题、正文） |
| `Text/Text - Table` | `#4F4F4F` | 表格内文字 |
| `Text/Text - Secondary` | `#84888C` | 次级 / 辅助文字 |
| `Text/Text - Tertiary` | `#A0A3A7` | 三级 / Placeholder |
| `Text/Text - Disable` | `#C4C7CA` | 不可用文字 |
| `light/text/color-text-1` | `#1D2129` | Arco 体系主文字 |
| `light/text/color-text-3` | `#86909C` | Arco 体系辅助文字 |
| `var(--color-text-text-primary)` | `#070808` | Web V5 主文本 |
| `var(--color-text-text-tertiary)` | `#A0A3A7` | Web V5 三级文本 |
| `var(--color-text-text-disable)` | `#C4C7CA` | Web V5 禁用文本 |
| `var(--color-text-text-brand)` | `#0068FF` | Web V5 品牌文字 |
| `var(--color-text-always-white)` | `#FFFFFF` | 不随主题切换的白文字 |
| `var(--color-text-always-black)` | `#070808` | 不随主题切换的黑文字 |
| `var(--color-text-inverse-primary)` | `#FFFFFF` | 反色主文本（用于深底） |

### 1.2 背景 Background

| Token | 值 | 用途 |
| --- | --- | --- |
| `Background/Bg-Primary` | `#FFFFFF` | 主背景 |
| `Background/Bg-Secondary` | `#FAFAFA` | 次级背景（卡片、面板） |
| `Background/Bg-Tertiary` | `#F2F3F4` | 三级背景 |
| `Background/Bg-quaternary` | `#DFE0E2` | 四级背景 |
| `Background/Bg-Mask` | `#F2F3F4` | 遮罩 |
| `var(--color-bg-primary)` | `#FFFFFF` | Web V5 主背景 |
| `var(--color-bg-always-white)` | `#FFFFFF` | 始终为白的背景 |

### 1.3 线条 / 描边 Line

| Token | 值 | 用途 |
| --- | --- | --- |
| `Line/Line-Border` | `#F2F3F4` | 一般边框 |
| `Line/Line- Divider` | `#F2F3F4` | 分割线 |
| `light/line/color-border-2` | `#E5E6EB` | Arco 中等边框 |
| `var(--color-line-border-strong)` | `#DFE0E2` | 强边框 |

### 1.4 图标 Icon

| Token | 值 | 用途 |
| --- | --- | --- |
| `Icon/Icon-Primary` | `#303236` | 主图标 |
| `Icon/Icon-Secondary` | `#484B51` | 次级图标 |
| `Icon/Icon Tertiary` | `#84888C` | 三级图标 |
| `var(--color-icon-icon-primary)` | `#303236` | Web V5 主图标 |

### 1.5 品牌 Brand

| Token | 值 | 用途 |
| --- | --- | --- |
| `Brand/Brand color` | `#ADF73E` | 主品牌色（Pay 绿） |
| `Brand/Text-Brand` | `#68AD00` | 品牌文字（绿） |
| `Brand/Component hover` | `#E6F4D2` | 品牌组件 hover 浅底 |

### 1.6 功能色 Function（状态）

| 类型 | Bg | Text |
| --- | --- | --- |
| 成功 Success | `#E5F9F3` | `#089767` |
| 警告 Warning | `#FFEACA` | `#F26500` |
| 信息 Information | `#F5F6F7` | `#84888C` |
| 指示 Indicator | `#EBF6FF` | `#0055FF` |
| 失败 Failed | `#FFEBEF` | `#FF2C58` |

通用功能 token：

| Token | 值 |
| --- | --- |
| `var(--color-function-hot)` | `#F7594B` |
| `var(--color-function-trade-buy)` | `#2BC287` |
| `var(--color-function-trade-buy-active)` | `#20A174` |
| `var(--color-function-trade-sell)` | `#F74B60` |
| `var(--color-function-trade-sell-active)` | `#D6364E` |

### 1.7 特殊 Black / White

| Token | 值 |
| --- | --- |
| `light/特殊/Black` | `#000000` |
| `light/特殊/White` | `#FFFFFF` |
| `var(--color-alpha-black-10)` | `rgba(0, 0, 0, 0.10)` |
| `var(--color-alpha-white-20)` | `rgba(255, 255, 255, 0.20)` |
| `var(--color-cmpt-gradient-bg-20)` | `rgba(255, 255, 255, 0.20)` |
| `var(--color-cmpt-carousel-bg)` | `rgba(0, 0, 0, 0.10)` |

## 2. Primitive 原色阶

### 2.1 Neutral（中性灰）

| Step | Hex |
| --- | --- |
| Neutral-White | `#FFFFFF` |
| Neutral-1 | `#FAFAFA` |
| Neutral-2 | `#F2F3F4` |
| Neutral-3 | `#DFE0E2` |
| Neutral-4 | `#C4C7CA` |
| Neutral-5 | `#A0A3A7` |
| Neutral-6 | `#74777B` |
| Neutral-7 | `#484B51` |
| Neutral-9 | `#18191B` |
| Neutral-10 | `#131516` |
| Neutral-11 | `#1F2023` |
| Neutral-12 | `#070808` |

### 2.2 Brand 蓝色阶（Brand1-*，备选品牌色）

| Step | Hex |
| --- | --- |
| Brand-3 | `#95BFFB` |
| Brand-4 | — |
| Brand-6 | `#387CF2` |
| Brand-7 | `#2D4ED4` |
| Brand-9 | `#203588` |

### 2.3 Magenta 品红

| Token | Hex |
| --- | --- |
| `light/magenta/magenta-1` | `#FFE8F1` |
| `light/magenta/magenta-2` | `#FDC2DB` |
| `light/magenta/magenta-3` | `#FB9DC7` |
| `light/magenta/magenta-5` | `#F754A8` |
| `light/magenta/magenta-6` | `#F5319D` |
| `light/magenta/magenta-7` | `#CB1E83` |

### 2.4 Success 绿（Arco Style）

| Step | Hex |
| --- | --- |
| Success-1 | `#E8FFEA` |
| Success-2 | `#AFF0B5` |
| Success-3 | `#7BE188` |
| Success-5 | `#23C343` |
| Success-6 | `#00B42A` |
| Success-7 | `#009A29` |

### 2.5 Trade 交易 — 买入（绿）

| Token | Hex |
| --- | --- |
| GreenTrade-1 | `#DFF5EA` |
| GreenTrade-6 | `#2BC287` |
| GreenTrade-10 | `#092117` |
| GreenFunct-6 | `#2BC287` |
| Green-7 | `#20A174` |

### 2.6 Trade 交易 — 卖出（红）

| Token | Hex |
| --- | --- |
| RedTrade-1 | `#FFEBEB` |
| RedTrade-6 | `#F74B60` |
| RedTrade-10 | `#341C1D` |
| RedFunct-6 | `#F7594B` |

### 2.7 其他原色

| Token | Hex |
| --- | --- |
| Yellow-6 | `#FEBE00` |
| Orange-5 | `#FFAE6B` |
| Orange-6 | `#FF9447` |

## 3. 组件级 CSS 变量（Web V5）

来自 Button、Checkbox 组件的样式 token：

| 变量 | 值 | 用途 |
| --- | --- | --- |
| `--color-cmpt-button-primary` | `#303236` | 主要按钮（黑） |
| `--color-cmpt-button-soft` | `#F5F6F7` | 弱化按钮底 |
| `--color-cmpt-button-soft-active` | `#DFE0E2` | 弱化按钮按下 |
| `--color-cmpt-button-soft-disable` | `#F5F6F7` | 弱化按钮禁用 |
| `--color-cmpt-btn-white-pressed-txt` | `#A0A3A7` | 白底按钮按下文字 |
| `--color-cmpt-btn-white-dis-txt` | `#84888C` | 白底按钮禁用文字 |
| `--color-cmpt-btn-white-dis-bg` | `#303236` | 白底按钮禁用背景 |

## 4. 图表色（Charts）

Figma 中定义了 `Chart-1` ~ `Chart-9` 共 9 个图表色，配套环形图与辅助色：

- 环形图: `环形图-红1`、`环形图-红2`、`环形图-绿1`、`环形图-绿2`
- 辅助色: 灰色 / 蓝绿色 / 黄色 / 黑色
- 图表主色: 蓝色
- 火 (热门): `var(--color-function-hot)` `#F7594B`
