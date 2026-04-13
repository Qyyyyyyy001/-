# Pay B 端 组件规范 — Yang

> 来源 Figma 文件: `Pay-B端 组件规范 - Yang`
> File key: `vCt8aPJKNCIrvkAo1nLph7`
> 入口节点: `1:64`（基础组件 Canvas）
> 导入日期: 2026-04-13

本目录是从 Figma 设计文件导入的 **Pay B 端基础组件设计规范**。它涵盖排版、颜色、间距、按钮与勾选/单选等基础组件的设计 token 与变体定义，可作为前端实现 Pay B 端 UI 时的事实来源（source of truth）。

## 目录结构

| 文档 | 内容 |
| --- | --- |
| [`typography.md`](./typography.md) | 字体家族、字号、字重、行高，以及每种文本样式的使用场景 |
| [`colors.md`](./colors.md) | 颜色 token：文本、背景、线条、图标、品牌、功能（成功/警告/失败）以及交易（买/卖）色 |
| [`spacing.md`](./spacing.md) | 横向/纵向间距尺度 |
| [`components/button.md`](./components/button.md) | 按钮组件：5 种类型 × 5 种状态 × 7 种尺寸 + 图标变体 |
| [`components/checkbox.md`](./components/checkbox.md) | Checkbox / Radio / 半选状态组件 |
| [`icons.md`](./icons.md) | 图标库 · 7 个分组 370+ 个图标完整命名清单（Basic Product / Control / Header / Social / Crypto / Chain / Fiat） |

## 规范全局信息

- **设计语言基础**：参考 Arco Design，按 Pay B 端业务做的二次封装。
- **slogan**：务实的浪漫主义。
- **支持的语言**：中文（PingFang SC）+ 英文 / 数字（Nunito Sans / Switzer）。
- **配色模式**：当前文件以 Light 模式为主（`light/...` 命名空间）。
- **Token 命名空间**：
  - `light/text/*`、`light/line/*`、`light/magenta/*` 等对应 Arco 风格的全局色
  - `Text/*`、`Background/*`、`Line/*`、`Icon/*`、`Brand/*` 对应 Pay B 端语义化 token
  - `var(--color-*)` 对应 Web V5 的 CSS 变量名

## 源 Figma 文件的 7 个页面

| # | Canvas | Node ID | 内容 |
| ---: | --- | --- | --- |
| 1 | **基础组件** | `1:64` | 唯一有内容的页面。包含 Fonts / Color / Spacing / Button / Checkbox / 基础产品图标（~370 图标）/ Color_V5.1 Guidelines |
| 2 | 全剧规范 | `43:317088` | （源文件中尚未填充） |
| 3 | 通用组件 | `43:317089` | （源文件中尚未填充） |
| 4 | 反馈组件 | `43:317090` | （源文件中尚未填充） |
| 5 | 导航组件 | `43:317091` | （源文件中尚未填充） |
| 6 | 数据展示 | `43:317092` | （源文件中尚未填充） |
| 7 | 数据录入 | `43:317093` | （源文件中尚未填充） |

## "基础组件" 页面内的组件区块

| 区块 | Node ID | 尺寸 | 内容 |
| --- | --- | --- | --- |
| Fonts | `1:215` | 1687 × 2578 | 字体规范 |
| Color | `1:393` | 1766 × 2578 | 颜色规范 |
| Spacing | `33:296` | 1687 × 3228 | 间距规范 |
| Button | `33:11329` | 5789 × 5550 | 按钮组件全量变体：5 Type × 5 State × 7 Size × 4 Icon 变体 |
| Checkbox | `33:14060` | 1200 × 5550 | 勾选/单选/半选组件 |
| 基础产品图标 | `33:1971` | 2000 × 8830 | section，包含 7 大类 ~370 个图标 instance |

## 目标 Figma 文件（本次会话生成）

**<https://www.figma.com/design/oA8CbhQplvQVisCVpbUx0r>** · `Pay B 端设计系统 — 收款链接示例 (by Claude)`

| 页面 | 内容 |
| --- | --- |
| `收款链接` | Gate Pay 收款链接 1280×800 应用页面 mockup + Button 7 Size × 5 Type × State 控件参考板 |
| `Design System` | Colors / Typography / Spacing / Checkbox / Button State × Type 矩阵 / Button Icon 变体 / Icons 图标库（370+）|
