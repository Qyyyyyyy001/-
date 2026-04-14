# Component Library · 组件参考库

> 目标 Figma 文件: <https://www.figma.com/design/oA8CbhQplvQVisCVpbUx0r>
> 页面: `Component Library` (`24:2`)

这是对源文件 55+ 组件页的简化参考实现，**全部使用设计系统 token**（颜色 / 字号 / 间距）绘制。每个 board 对应源文件的一个或多个 component page，用最精简的尺寸演示了组件的核心变体。

## 34 个组件板

| # | 组件 | 对应源 Figma page | 变体 |
| ---: | --- | --- | --- |
| 1  | **Tag** 标签              | `42:185530 Tag`                  | Soft / Solid × Success/Warning/Failed/Info/Neutral × Small/Medium/Large |
| 2  | **Badge** 徽标            | `42:185515 Badge`                | Dot / Number (1/8/99/99+) / Text (NEW/HOT/VIP/BETA) |
| 3  | **Switch** 开关           | `41:3871 Switch`                 | Small-16/Medium-20/Large-24 × On/Off × Disabled |
| 4  | **Divider** 分割线         | `41:3869 Divider`                | Horizontal solid/dashed/labeled × Vertical |
| 5  | **Input** 输入框           | `42:185533 Input`                | 3 Sizes × Default/Focus/Error/Disabled × Prefix/Suffix/Both × Error message |
| 6  | **Textarea** 文本域        | `42:185533 Input`                | Default (400×96) |
| 7  | **Select** 下拉选择        | `41:3870 Selector`               | 3 Sizes × Default/Value/Open/Disabled · Open state with option list |
| 8  | **Alert / Toast** 通知     | `41:3875 Notification`           | Alert: 4 状态 (Success/Warning/Failed/Info) + close · Toast: Success/Failed/Info |
| 9  | **Modal** 弹窗             | `42:71918 Modal`                 | Basic · Confirm w/ icon · Info · 遮罩 + 卡片 + 取消/确定 按钮 |
| 10 | **Tooltip** 气泡提示       | `42:71921 Tooltips`              | Dark (default) · Light variant |
| 11 | **Tabs** 标签页            | `42:71924 Tab`                   | Line · Card · Pill style |
| 12 | **Pagination** 分页        | `42:185509 Pagination`           | Full with ellipsis · 带总数/页大小 · Simple |
| 13 | **Steps** 步骤条           | `42:185512 Steps`                | Vertical · Horizontal · 三种状态 (done/active/upcoming) |
| 14 | **Breadcrumb** 面包屑      | `42:71926 Breadrumb`             | Text · With home icon |
| 15 | **Table** 表格             | `42:185529 Table`                | 表头 + 3 行 + 状态 Tag + 操作列 |
| 16 | **Avatar** 头像            | `42:185514 Avatar`               | 6 Sizes (24/32/40/48/64/80) × Circle/Square × Group stack |
| 17 | **Loading** 加载           | `41:3872 Loading`                | Spinner (4 sizes) · Dot loading · Skeleton · Progress bar (30/60/100%) |
| 18 | **Empty** 空状态           | `42:185524 Empty`                | Icon + 文案 + 新建按钮 |
| 19 | **Search** 搜索            | `42:185535 Search`               | Plain · With button |
| 20 | **Slider** 滑块            | `42:185538 Slider`               | Single (30%/75%) · Range slider (min/max) |
| 21 | **Rate** 评分              | `42:185540 Rate`                 | 5 Star · 3.5/5 half star · Large size |
| 22 | **Upload** 上传            | `42:185541 Upload`               | Drag & drop zone · File list with progress (done/uploading/error) |
| 23 | **Date / Time Picker**     | `42:185539 Time picker`          | Input trigger (empty/value) · Full calendar panel (5 weeks) |
| 24 | **Number Input** 数值输入  | `42:185537 Number input`         | With stepper · Without stepper · With unit (USDT/BTC/%) |
| 25 | **Banner** 横幅            | `41:3862 Banner`                 | Announcement (warning) · Promo gradient (blue → purple) |
| 26 | **Collapse** 折叠面板      | `42:185520 Collapse`             | Accordion 4 items (1 expanded) |
| 27 | **Countdown** 倒计时       | `42:185518 Countdown`            | Block style (天/时/分/秒) · Inline |
| 28 | **Description** 描述列表   | `42:185522 Description`          | Horizontal inline key-value 5 rows |
| 29 | **Coin Title** 币种标题    | `42:185521 Coin title`           | BTC / ETH / USDT / GT with icon + symbol + full name |
| 30 | **Anchor** 锚点            | `42:71925 Anchor`                | Vertical menu 5 items (1 active) |
| 31 | **Announcement** 公告条    | `42:185510 Announcement`         | 滚动公告条 + 分类 pill + close |
| 32 | **Carousel** 轮播          | `42:185516 Carousel`             | 600×240 gradient slide + indicator dots + nav arrows |
| 33 | **Image** 图片状态         | `42:185528 Image`                | Normal / Loading / Error / Placeholder |
| 34 | **404 Error Pages**        | `42:185525 404`                  | 404 / 500 / 403 with title + description + 返回首页 button |
| 35 | **Header + Left Menu**     | `42:71928 Header footer` / `42:71927 Left menu` | 960×64 Header + Collapsed (64px) + Expanded (220px) 左侧菜单 |

## 未覆盖的源 Figma 页面

下面这些页面因为内容简单或重复度高，没有单独做 board（已合并或省略）：

| 源 page | 合并到 | 原因 |
| --- | --- | --- |
| `42:185508 progress bar` | Loading 板的 Progress bar | 重复 |
| `42:185526 Number view` | Typography scale | 纯数字展示，token 已覆盖 |
| `42:185531 Share modal` | Modal | 特化版 Modal |
| `42:185532 Video player` | — | 暂省略 |
| `42:185542 Download` | — | 与 Upload 反向，共用 token |
| `42:185543 Add fund` | Number Input | 特化版 |
| `42:71919 results` | Empty | 结果页 ≈ Empty 状态 |
| `42:71922 User guide` | Tooltip | 引导蒙层 ≈ 多个 Tooltip |
| `41:2070 颜色 / 41:3859 字体 / 41:3860 阴影 / 41:3861 Grid / 41:3863 Spacing` | Design System 页的 Colors / Typography / Spacing 板 | 已覆盖 |
| `41:3864 Icon CEX / 41:3865 Icon web3` | Design System 页的 Icons 板 | 已覆盖 (370+ 命名) |

## 已绑定为 Figma Component 的变体

下面 6 个变体已经升级成真正的 Figma `COMPONENT` 节点，放在 Component Library 页面底部的 `__COMPONENTS_SOURCE__` 容器里，可以通过 `createInstance()` / `clone()` 复用：

| Component 名 | Node ID | 用途 |
| --- | --- | --- |
| `Button / Primary-Black / Small-36px` | `39:4`  | 主 CTA |
| `Button / Secondary-Gray / Small-36px` | `39:6`  | 次要 CTA (Soft) |
| `Link Button / Brand` | `39:8`  | 表格内蓝色链接文字（如 "查看二维码"） |
| `Link Button / Danger` | `39:10` | 表格内红色链接文字（如 "删除"） |
| `Tag / Soft / Success` | `39:12` | 绿色状态标签 |
| `Tag / Soft / Neutral` | `39:14` | 灰色次级状态标签 |

### 真实使用示例

**页面** `收款链接 (Components v2)` (`49:2`) — Gate Pay 收款链接列表页用这 6 个 Component 重画了一遍：

- 顶部 "客户渠道" + "新增" 两颗按钮 = `btnSoft.clone()` + `btnPrimary.clone()` · 文本通过 `findOne(TEXT).characters = "..."` 覆写
- 表格 8 行的 "二维码状态" Tag = `tagValid.clone() / tagExpired.clone()` · 文本同上
- "查看二维码" / "删除" 两个 Link Button × 8 行 = `linkBrand.clone()` + `linkDanger.clone()`

### 为什么用 `clone()` 而不是 `createInstance()`

Figma Plugin API 里 `createInstance()` 生成的 INSTANCE 节点对子 Text 做 `characters` 覆写时，虽然 API 层面看起来成功（inspect 能读到新值、fills 正确），但实际画布渲染会把文字变成不可见/截断。使用 `component.clone()` 生成一个普通的 FRAME 副本，可以自由修改子节点，渲染正常。代价是失去了"instance → 跟随 master 更新"的能力，但对这次复刻页面来说足够好。

### Target Figma 文件的 5 个页面

| 页面 | Node ID | 说明 |
| --- | --- | --- |
| `收款链接` | `0:1` | v1 —— 原始硬编码版（所有样式直接写死） |
| `Design System` | `5:2` | 设计 token + Button/Checkbox/Icons 参考板 |
| `Component Library` | `24:2` | 34 个组件参考板 + `__COMPONENTS_SOURCE__` 隐藏容器（6 个 Component 源） |
| `收款链接 (Components v2)` | `49:2` | v2 —— 使用 Component clone 的版本，按钮/Tag/Link 都是从 Component 源复制出来的 |
| **`Payment Dashboard (v1)`** | `55:2` | **Payment 仪表盘 1:1 复刻**：Sidebar + 4 KPI cards + 筛选条 + 表格 7 列 × 6 行（6 种状态 Tag：Pending/Expired/Successful/Canceled/Failed/Payment Abnormal）+ Action 菜单浮层 |

