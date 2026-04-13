# 设计系统使用示例

本目录展示如何使用 [`design-specs/`](../) 中的 token 与组件规范实现真实业务页面。

## payment-links.html — Gate Pay 收款链接管理

> 对应 Gate Pay 商家管理平台 → 收款 → 收款链接 列表页

### 截图复刻清单

| 区块 | 实现要点 | 用到的 token / 组件 |
| --- | --- | --- |
| 顶部 Header | 黑底浅字，左侧 home + Gate Pay logo + 应用切换器，右侧充值/帮助/通知/头像/主题/语言 | `--color-text-always-black`、`--color-text-always-white`、`--space-16` |
| 左侧 Sidebar | 200px 宽度，菜单分组，"收款"展开并 active "收款链接" | `--color-bg-primary`、`--color-line-border`、`--color-icon-icon-secondary`、`--space-8`、`--radius-md` |
| Main 页面卡片 | 白底圆角卡片，24px padding | `--color-bg-primary`、`--radius-lg`、`--space-24` |
| 页面标题 | `20/600` 字号 | `--color-text-text-primary` + typography scale `20/600` |
| 顶部按钮 (客户渠道 / 新增) | Button — Type=Brand，Size=Small-36px | `.btn--brand.btn--sm`，对应 [`components/button.md`](../components/button.md) |
| 表格 | 1px 边框 + 8px 圆角包裹，表头浅灰底 12/400 字号，单元格 14/400 | `--color-bg-secondary`、`--color-line-border`、`--color-text-text-secondary`、`--color-text-text-table` |
| 序号列 | 三级文字色 | `--color-text-text-tertiary` |
| 订单金额 | 主文本色 + Medium 字重 | `--color-text-text-primary` + `font-weight: 500` |
| 二维码状态 | 有效 → 成功色；无效 → 信息（次级）色 | `--color-function-success-text`、`--color-text-text-secondary` |
| "查看二维码" | Link Button（蓝色文字） | `.btn--link`，色值 `--color-text-text-brand` |
| "删除" | Link Button（红色文字） | `.btn--link.is-danger`，色值 `--color-function-failed-text` |
| 红色"付款按钮"标注 | 模拟原稿设计批注，用失败色 + 12/500 字号 | `--color-function-failed-text` |
| 右下角悬浮客服按钮 | 44×44 圆形 FAB，品牌蓝 | `#387cf2`（Brand1-6）+ box-shadow |

### 设计 token → CSS 变量映射

HTML 文件顶部 `:root` 块里把所有 token 都映射成了 CSS 变量，命名规则保持与 Figma 一致：

```css
--color-text-text-primary:    #070808;   /* Text/Text - Primary */
--color-bg-primary:           #ffffff;   /* Background/Bg-Primary */
--color-line-border:          #f2f3f4;   /* Line/Line-Border */
--color-cmpt-button-primary:  #303236;   /* var(--color-cmpt-button-primary) */
--color-function-failed-text: #ff2c58;   /* Failed - Text */
--space-16: 16px;                        /* spacing scale 16 */
--font-cn:  "PingFang SC", ...;          /* typography family CN */
```

### 组件实现

按照 [`components/button.md`](../components/button.md) 的命名约定，本示例提供了 4 种按钮变体：

| Class | 对应 Type | 对应 Size |
| --- | --- | --- |
| `.btn--primary.btn--sm` | Primary-Black | Small-36px |
| `.btn--soft.btn--sm`    | Secondary-Gray | Small-36px |
| `.btn--brand.btn--sm`   | （业务扩展色：Brand1-6 蓝） | Small-36px |
| `.btn--link`            | Link / Text Button | 自适应 |
| `.btn--link.is-danger`  | Danger Link Button | 自适应 |

> Brand 蓝按钮严格意义上不在 Figma 现有的 5 种 Button Type 之内（设计系统中的 Brand 是绿色），但本示例需要复刻 Gate Pay 截图中的蓝色 CTA，因此在设计系统的 _Brand1 蓝色阶_（`#387CF2` / `#2D4ED4`）基础上扩展了一个业务变体。这种"业务扩展"应当反馈给设计同学，决定是把它升级为正式 Type，还是改用 Primary-Black。

### 本地预览

直接在浏览器打开：

```bash
open design-specs/examples/payment-links.html      # macOS
xdg-open design-specs/examples/payment-links.html  # Linux
```

或者用任意静态服务器：

```bash
python3 -m http.server 8000 -d design-specs/examples
# 访问 http://localhost:8000/payment-links.html
```
