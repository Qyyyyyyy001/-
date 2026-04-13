# Button 按钮

> 来源 Figma 节点: `33:11329` (Button → ButtonV5-web)

按钮是 Pay B 端最常用的交互组件之一。Figma 中以 `ButtonV5-web` Component Set 提供完整的变体矩阵，共 **5 种类型 × 5 种状态 × 7 种尺寸 × 4 种图标组合** ≈ 700 个变体（每种 Type 约 140 个变体）。

## 1. 变体矩阵

### 1.1 类型 Type

| Type | 用途 | 默认背景 token |
| --- | --- | --- |
| **Primary-Black** | 主要按钮，强 CTA。页面主按钮、表单提交。 | `var(--color-cmpt-button-primary)` `#303236` |
| **Secondary-Gray** | 次要按钮（Soft）。和 Primary 配合，承接次要操作。 | `var(--color-cmpt-button-soft)` `#F5F6F7` |
| **White** | 白底按钮。深底页面 / 浮层 / 卡片内反色按钮。 | `var(--color-bg-always-white)` `#FFFFFF` |
| **Green** | 成功 / 买入按钮。交易场景买入操作。 | `var(--color-function-trade-buy)` `#2BC287` |
| **Red** | 危险 / 卖出按钮。删除、卖出操作。 | `var(--color-function-trade-sell)` `#F74B60` |

### 1.2 状态 State

| State | 描述 |
| --- | --- |
| **Default** | 默认态 |
| **Hover** | 悬浮态（仅 web） |
| **Pressed** | 按下/激活态 |
| **Loading** | 加载态，文案旁出现 spinner，按钮不可点击 |
| **Disable** | 禁用态，使用 `*-soft-disable` / `*-dis-bg` 系列 token |

### 1.3 尺寸 Size

| Size | 高度 | 推荐字号 | 推荐图标 | 横向内边距 |
| --- | ---: | ---: | ---: | ---: |
| **XXSmall** | 28 px | 12 px | 12 px | 8 px |
| **XSmall** | 32 px | 12 px | 14 px | 12 px |
| **Small** | 36 px | 14 px | 14 px | 12 px |
| **Medium** | 40 px | 14 px | 16 px | 16 px |
| **Large** | 44 px | 14 px | 16 px | 16 px |
| **XLarge** | 48 px | 16 px | 18 px | 20 px |
| **XXLarge** | 56 px | 18 px | 20 px | 24 px |

> 字号映射到 `Web_V5/Body/B11 500 12px` / `B7 500 14px` / `B3 500 16px` / `Subtitle/S5 600 18px`。详见 [`../typography.md`](../typography.md)。

### 1.4 图标位置 Icon

每个尺寸都提供 4 种图标变体：

| Variant | Prefix Icon | Suffix Icon | Only Icon |
| --- | --- | --- | --- |
| Text only | False | False | False |
| With prefix icon | True | False | False |
| With suffix icon | False | True | False |
| Icon only（方形按钮） | False | False | True |

## 2. 颜色 Token 速查

### 2.1 Primary-Black

| State | 背景 | 文字 |
| --- | --- | --- |
| Default | `--color-cmpt-button-primary` `#303236` | `--color-text-inverse-primary` `#FFFFFF` |
| Pressed | （在 Default 上叠加 alpha） | `#FFFFFF` |
| Disable | `--color-cmpt-btn-white-dis-bg` `#303236`（降透明度） | `--color-cmpt-btn-white-dis-txt` `#84888C` |

### 2.2 Secondary-Gray (Soft)

| State | 背景 | 文字 |
| --- | --- | --- |
| Default | `--color-cmpt-button-soft` `#F5F6F7` | `--color-text-text-primary` `#070808` |
| Active / Pressed | `--color-cmpt-button-soft-active` `#DFE0E2` | `#070808` |
| Disable | `--color-cmpt-button-soft-disable` `#F5F6F7` | `--color-text-text-disable` `#C4C7CA` |

### 2.3 White

| State | 背景 | 文字 |
| --- | --- | --- |
| Default | `--color-bg-always-white` `#FFFFFF` | `--color-text-always-black` `#070808` |
| Pressed | `#FFFFFF` | `--color-cmpt-btn-white-pressed-txt` `#A0A3A7` |
| Disable | `--color-cmpt-btn-white-dis-bg` `#303236` | `--color-cmpt-btn-white-dis-txt` `#84888C` |

### 2.4 Green（买入 Buy）

| State | 背景 | 文字 |
| --- | --- | --- |
| Default | `--color-function-trade-buy` `#2BC287` | `--color-text-always-white` `#FFFFFF` |
| Pressed | `--color-function-trade-buy-active` `#20A174` | `#FFFFFF` |
| Disable | `--color-function-trade-buy` + alpha | `#FFFFFF` + alpha |

### 2.5 Red（卖出 Sell / 危险）

| State | 背景 | 文字 |
| --- | --- | --- |
| Default | `--color-function-trade-sell` `#F74B60` | `--color-text-always-white` `#FFFFFF` |
| Pressed | `--color-function-trade-sell-active` `#D6364E` | `#FFFFFF` |
| Disable | `--color-function-trade-sell` + alpha | `#FFFFFF` + alpha |

## 3. 选择指南

- **主操作 → Primary-Black**：每个页面/对话框只有一个。
- **次操作 → Secondary-Gray**：取消、上一步等。
- **深色背景 → White**：悬浮在轮播图、横幅、深色卡片上的反色按钮。
- **交易页面 → Green / Red**：买入用 Green，卖出/确认风险操作用 Red。
- **危险破坏性操作 → Red**：删除、清空。

## 4. Loading 与 Disable

- **Loading**：保留按钮当前类型与尺寸，仅在文案左侧追加 spinner，按钮宽度不重排（避免抖动）。Loading 期间事件被忽略。
- **Disable**：各类型有独立的 disable token（见上方表格）。不要直接降透明度，要使用对应的 `*-disable` token。
