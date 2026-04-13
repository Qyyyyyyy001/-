# Typography 字体规范

> 来源 Figma 节点: `1:215` (Fonts)

## 字体家族

| 用途 | 家族 | 备注 |
| --- | --- | --- |
| 中文 | **PingFang SC** | 默认中文字体 |
| 英文 / 数字 | **Nunito Sans** | 与中文搭配的英数字 |
| Web V5 通用 | **Switzer** | 用于 Web V5 组件（Button 等） |

设计 slogan：**务实的浪漫主义**。

## 字号 / 字重 / 行高

下表来自 Figma `Fonts` 区块的样式条目（左列字号/字重，右列使用场景）。

| Style | 字号 | 字重 | 行高 | 字间距 | 使用场景 |
| --- | ---: | ---: | ---: | ---: | --- |
| `12/400` | 12 | Regular (400) | 20 | 0 | 辅助文案 — 小 Badge 文字、Helper、Toast 文字、上传描述、Tooltips |
| `12/500` | 12 | Medium (500) | 20 | 0 | 小 Badge 文字、强调辅助文案 |
| `13/400` | 13 | Regular (400) | 22 | 0 | 表单内辅助、密集列表 |
| `14/400` | 14 | Regular (400) | 22 | 0 | 正文 — 标题、内容、辅助信息、Placeholder |
| `14/500` | 14 | Medium (500) | 22 | 0 | 正文 — 标题、内容、按钮文字、导航、Filter、大 Badge 文字 |
| `14/600` | 14 | SemiBold (600) | 22 | 0 | 正文 — 筛选标题 |
| `16/400` | 16 | Regular (400) | 24 | 0 | 长文正文 |
| `16/500` | 16 | Medium (500) | 24 | 0 | 表格 — 表格内容、次级表格金额文字、面包屑、占位符内容 |
| `16/600` | 16 | SemiBold (600) | 24 | 0 | 表格 — 主要表格金额文字、宣传标题 |
| `18/600` | 18 | SemiBold (600) | 28 | 0 | 标题 — Tab 标题、宣传标题、理财标题、Loading 标题 |
| `20/400` | 20 | Regular (400) | 28 | 0 | 大号正文 / 数字 |
| `20/600` | 20 | SemiBold (600) | 28 | 0 | 标题 — 标题、金额数值、设置标题 |
| `24/400` | 24 | Regular (400) | 32 | 0 | 英文大号正文 |
| `24/600` | 24 | SemiBold (600) | 32 | 0 | 标题 — 弹窗标题、标题 |
| `32/600` | 32 | SemiBold (600) | 40 | 0 | 标题 — 模块标题 |

> 中英文同一字号会拆成两个变量，如 `14/CN-Regular`（PingFang SC）与 `14/EN-Regular`（Nunito Sans），运行时按字符脚本切换字体家族即可。

## Figma 字体变量映射

| Token | 字体 | 字号 | 字重 | 行高 |
| --- | --- | ---: | ---: | ---: |
| `12/CN-Regular` | PingFang SC | 12 | 400 | 20 |
| `12/CN-Medium` | PingFang SC | 12 | 500 | 20 |
| `12/EN-Medium` | Nunito Sans | 12 | 600 (SemiBold) | 20 |
| `13/CN-Regular` | PingFang SC | 13 | 400 | 22 |
| `14/CN-Regular` | PingFang SC | 14 | 400 | 22 |
| `14/EN-Regular` | Nunito Sans | 14 | 400 | 22 |
| `16/CN-Regular` | PingFang SC | 16 | 400 | 24 |
| `20/CN-Regular` | PingFang SC | 20 | 400 | 28 |
| `20/EN-Regular` | Nunito Sans | 20 | 400 | 28 |
| `24/EN-Regular` | Nunito Sans | 24 | 400 | 32 |

## Web V5 (Switzer) 字体变量

> Web V5 使用 Switzer，行高以倍数表示（≈ 1.3）。

| Token | 字号 | 字重 | line-height |
| --- | ---: | ---: | ---: |
| `Web_V5/Subtitle/S5 600 18px` | 18 | 600 | 1.3 |
| `Web_V5/Body/B3 500 16px` | 16 | 500 | 1.3 |
| `Web_V5/Body/B7 500 14px` | 14 | 500 | 1.3 |
| `Web_V5/Body/B8 400 14px` | 14 | 400 | 1.3 |
| `Web_V5/Body/B11 500 12px` | 12 | 500 | 1.3 |
| `Web_V5/Body/B13 400 12px` | 12 | 400 | 1.3 |
