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

## 使用建议

- **实现新 UI 时**：先打开 `Component Library` 找对应组件参考板 → 按 token 抄到代码
- **改配色 / 改字号时**：不要直接改 board 里的硬编码 —— 去 `Design System → Colors / Typography` 里改原 token，整套页面联动
- **加新组件时**：参考这里的 board 命名规范（`<Component> · <中文名>`），用相同的 40px padding + 白底 + 16px 圆角
- **对照源文件时**：每条组件表格都标注了源 Figma page 的 node ID，可以直接在源文件 `node-id=<id>` 拼接打开
