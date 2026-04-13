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
| [`icons.md`](./icons.md) | 图标库说明：Header、Social Media、Currency、Currency Chain、Fiat |

## 规范全局信息

- **设计语言基础**：参考 Arco Design，按 Pay B 端业务做的二次封装。
- **slogan**：务实的浪漫主义。
- **支持的语言**：中文（PingFang SC）+ 英文 / 数字（Nunito Sans / Switzer）。
- **配色模式**：当前文件以 Light 模式为主（`light/...` 命名空间）。
- **Token 命名空间**：
  - `light/text/*`、`light/line/*`、`light/magenta/*` 等对应 Arco 风格的全局色
  - `Text/*`、`Background/*`、`Line/*`、`Icon/*`、`Brand/*` 对应 Pay B 端语义化 token
  - `var(--color-*)` 对应 Web V5 的 CSS 变量名

## Figma 顶层结构

| 区块 | Node ID | 尺寸 | 内容 |
| --- | --- | --- | --- |
| Fonts | `1:215` | 1687 × 2578 | 字体规范 |
| Color | `1:393` | 1766 × 2578 | 颜色规范 + 图标库 |
| Spacing | `33:296` | 1687 × 3228 | 间距规范 |
| Button | `33:11329` | 5789 × 5550 | 按钮组件全量变体 |
| Checkbox | `33:14060` | 1200 × 5550 | 勾选/单选/半选组件 |
