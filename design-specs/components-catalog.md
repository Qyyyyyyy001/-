# Pay B 端设计系统 · 源文件完整组件目录

> 来源 Figma: `vCt8aPJKNCIrvkAo1nLph7` · Pay-B端 组件规范 - Yang
> 数据抓取方式：Figma MCP `use_figma` Plugin API 遍历 `figma.root.children` / `walk(COMPONENT_SET|COMPONENT)`
> 抓取日期：2026-04-13

这份目录是对 [`README.md`](./README.md) "7 个页面"那一版的**重大修正**。之前我误以为除了 `1:64 基础组件` 之外其他页面都是空的，实际情况是：

- **`43:317088` 全剧规范 / `43:317089` 通用组件 / `43:317090` 反馈组件 / `43:317091` 导航组件 / `43:317092` 数据展示 / `43:317093` 数据录入** 这 6 个页面本身确实是空的 —— 它们是**分类标签页**（章节分隔符），而不是真正放组件的地方。
- 真正的组件分布在**另外 50+ 个页面**里，这些页面的 ID 不连续（41:x、42:x 等），紧挨着对应的分类标签页排列。

## 完整页面列表（55 个有内容的页面）

下表按源文件左侧面板的显示顺序组织，**分类标签页**作为章节标题。每行对应一个真正的组件页面，标注了页面内直接子节点的 frame / component / section 数量。

### ▸ Cover / 引导

| 页面 | Node ID | f / c / s |
| --- | --- | ---: |
| `Cover` | `0:1` | 1 / 0 / 0 |

### ▸ 基础组件

| 页面 | Node ID | f / c / s | 说明 |
| --- | --- | ---: | --- |
| **基础组件** | `1:64` | 4 / 0 / 2 | 旧版本总页（Fonts / Color / Spacing / Button / Checkbox / 基础产品图标 section） |

### ▸ 全剧规范 (`43:317088`, 分类标签页)

| 页面 | Node ID | f / c / s | 含组件 |
| --- | --- | ---: | --- |
| `颜色` | `41:2070` | 0 / 0 / 3 | 色板 section 说明 |
| `字体` | `41:3859` | 0 / 0 / 2 | |
| `阴影` | `41:3860` | 0 / 0 / 1 | |
| `Grid` | `41:3861` | 0 / 0 / 2 | |
| `Spacing` | `41:3863` | 0 / 1 / 2 | 1 个 Spacing 组件 |
| `Banner` | `41:3862` | 0 / 3 / 6 | 3 个 Banner 组件 |
| `Icon CEX` | `41:3864` | 0 / 0 / 9 | 9 个 icon section（CEX_* 业务图标） |
| `Icon web3` | `41:3865` | 0 / 0 / 3 | 3 个 web3 图标 section |

### ▸ 通用组件 (`43:317089`, 分类标签页)

| 页面 | Node ID | f / c / s | 含组件 |
| --- | --- | ---: | --- |
| **`Button`** | `41:3867` | 0 / 6 / 4 | 6 个 Button Component Set |
| **`Checkbox`** | `41:3868` | 0 / 0 / 4 | 4 个 Checkbox section |
| `Divider` | `41:3869` | 0 / 1 / 1 | 分割线 |
| `Selector` | `41:3870` | 0 / 0 / 3 | |
| `Switch` | `41:3871` | 0 / 1 / 2 | 开关 |
| `Loading` | `41:3872` | 0 / 0 / 3 | |

### ▸ 反馈组件 (`43:317090`, 分类标签页)

| 页面 | Node ID | f / c / s | 含组件 |
| --- | --- | ---: | --- |
| **`Notification`** | `41:3875` | 0 / 1 / 14 | 通知 / Toast |
| **`Modal`** | `42:71918` | 0 / 0 / 10 | 弹窗 |
| `results` | `42:71919` | 0 / 0 / 3 | 结果页 |
| `Selector` | `42:71920` | 1 / 0 / 8 | 反馈版 Selector |
| `Tooltips` | `42:71921` | 0 / 0 / 3 | |
| `User guide` | `42:71922` | 0 / 1 / 3 | 新手引导 |

### ▸ 导航组件 (`43:317091`, 分类标签页)

| 页面 | Node ID | f / c / s | 含组件 |
| --- | --- | ---: | --- |
| `Anchor` | `42:71925` | 0 / 1 / 0 | 锚点 |
| `Breadrumb` | `42:71926` | 0 / 0 / 3 | 面包屑 |
| `Header footer` | `42:71928` | 0 / 0 / 3 | 页头页脚 |
| `Left menu` | `42:71927` | 0 / 0 / 2 | 左侧菜单 |
| `progress bar` | `42:185508` | 0 / 0 / 3 | 进度条 |
| **`Pagination`** | `42:185509` | 0 / 0 / 3 | 分页 |
| `Announcement` | `42:185510` | 0 / 2 / 1 | 公告 |
| `Steps` | `42:185512` | 0 / 0 / 4 | 步骤条 |
| **`Tab`** | `42:71924` | 1 / 4 / 9 | 4 个 Tab Component Set |

### ▸ 数据展示 (`43:317092`, 分类标签页)

| 页面 | Node ID | f / c / s | 含组件 |
| --- | --- | ---: | --- |
| `Avatar` | `42:185514` | 0 / 0 / 3 | 头像 |
| **`Badge`** | `42:185515` | 0 / 0 / 3 | 徽标 |
| `Carousel` | `42:185516` | 0 / 0 / 4 | 轮播 |
| `Countdown` | `42:185518` | 0 / 0 / 4 | 倒计时 |
| `Collapse` | `42:185520` | 0 / 0 / 3 | 折叠 |
| `Coin title` | `42:185521` | 0 / 0 / 3 | 币种标题 |
| `Description` | `42:185522` | 0 / 0 / 2 | 描述列表 |
| `Empty` | `42:185524` | 0 / 0 / 5 | 空状态 |
| `404` | `42:185525` | 0 / 0 / 0 | 404 页 |
| `Number view` | `42:185526` | 0 / 0 / 3 | 数值展示 |
| `Image` | `42:185528` | 0 / 0 / 3 | 图片 |
| **`Table`** | `42:185529` | 0 / 0 / 3 | 表格 |
| **`Tag`** | `42:185530` | 0 / 0 / 3 | 标签 |
| `Share modal` | `42:185531` | 0 / 0 / 1 | 分享弹窗 |
| `Video player` | `42:185532` | 0 / 0 / 3 | 视频播放器 |

### ▸ 数据录入 (`43:317093`, 分类标签页)

| 页面 | Node ID | f / c / s | 含组件 |
| --- | --- | ---: | --- |
| **`Input`** | `42:185533` | 0 / 0 / 6 | 6 个 Input section |
| **`Search`** | `42:185535` | 0 / 3 / 2 | 3 个 Search 组件 |
| `Number input` | `42:185537` | 0 / 0 / 4 | 数值输入 |
| `Silder` | `42:185538` | 0 / 0 / 3 | 滑块 |
| `Time picker` | `42:185539` | 0 / 0 / 6 | 时间选择 |
| `Rate` | `42:185540` | 0 / 0 / 3 | 评分 |
| **`Upload`** | `42:185541` | 0 / 5 / 2 | 5 个 Upload 组件 |
| `Download` | `42:185542` | 0 / 1 / 1 | |
| `Add fund` | `42:185543` | 0 / 0 / 3 | 充值 |

## 已知的 Component / Component Set 节点 ID（部分）

从源文件抓取的具名组件节点，按页面分组：

### 基础组件 · Spacing_V5 (`33:1626`, 40 个 variants)

完整的 Horizontal / Vertical 间距刻度组件集：

| Node ID | 尺寸 | 变体 |
| --- | --- | --- |
| `33:1627` | 48 × 48 | Type=Vertical, Value=48 |
| `33:1635` | 32 × 32 | Type=Vertical, Value=32 |
| `33:1643` | 24 × 24 | Type=Vertical, Value=24 |
| `33:1651` | 24 × 20 | Type=Vertical, Value=20 |
| `33:1659` | 24 × 28 | Type=Vertical, Value=28 |
| `33:1667` | 22 × 8  | Type=Vertical, Value=8 |
| `33:1675` | 22 × 12 | Type=Vertical, Value=12 |
| `33:1683` | 24 × 16 | Type=Vertical, Value=16 |
| `33:1691` | 22 × 4  | Type=Vertical, Value=4 |
| `33:1699` | 48 × 48 | Type=Horizontal, Value=48 |
| `33:1707` | 32 × 32 | Type=Horizontal, Value=32 |
| `33:1715` | 24 × 24 | Type=Horizontal, Value=24 |
| `33:1723` | 20 × 24 | Type=Horizontal, Value=20 |
| `33:1731` | 28 × 24 | Type=Horizontal, Value=28 |
| `33:1739` | 16 × 24 | Type=Horizontal, Value=16 |
| `33:1747` | 40 × 40 | Type=Vertical, Value=40 |
| `33:1755` ~ `33:1827` | — | Type=Vertical, Value=64/72/80/100/120/140/160/180/200/240 |
| `33:1835` ~ `33:1915` | — | Type=Horizontal, Value=40/64/72/80/100/120/140/160/180/240/200 |
| `33:1923` | 4 × 22  | Type=Horizontal, Value=4 |
| `33:1928` | 8 × 22  | Type=Horizontal, Value=8 |
| `33:1933` | 12 × 22 | Type=Horizontal, Value=12 |

### 基础组件 · ButtonV5-web (`33:11345`, 700+ variants)

完整的按钮组件集，命名遵循
`Type=<Primary-Black|Secondary-Gray|White|Green|Red>, State=<Default|Hover|Pressed|Loading|Disable>, Size=<XXSmall-28px..XXLarge-56px>, Prefix Icon=<True|False>, Suffix Icon=<True|False>, Only Icon=<True|False>`。

已知的节点 ID 片段（抓取时因 15000 字符限制被截断，完整列表需要再次遍历）：

| Node ID | 变体 |
| --- | --- |
| `33:11346` | Primary-Black / Default / XXLarge-56px |
| `33:11348` | White / Default / XXLarge-56px |
| `33:11350` | Secondary-Gray / Default / XXLarge-56px |
| `33:11352` | Green / Default / XXLarge-56px |
| `33:11354` | Red / Default / XXLarge-56px |
| `33:11356 ~ 33:11374` | Large-44px / XLarge-48px × 5 types · Default |
| `33:11376 ~ 33:11392` | ... / Loading |
| `33:11506 ~ 33:11533` | ... / Hover / Prefix Icon=True |
| `33:11536 ~ 33:11563` | ... / Pressed / Prefix Icon=True |
| `33:11566 ~ 33:11593` | ... / Disable / Prefix Icon=True |
| ... | ... |

> ⚠️ 抓取被 15000 字符上限截断，实际有 700 左右个 Button component（按 `variants` 字段，ButtonV5-web component set 自己声明了 `700v`）。

## 待补齐的 Figma 目标文件（`oA8CbhQplvQVisCVpbUx0r`）

当前我创建的目标 Figma 文件里只复刻了：

1. Gate Pay 收款链接 mockup
2. Button 7 Size × 5 Type × State 控件参考板
3. Design System 页面：Colors / Typography / Spacing / Checkbox 板
4. Button — State × Type 矩阵板 + Icon 变体板
5. Icons 图标库板（370+ 图标命名）

**尚未补齐**（等 Figma MCP 恢复后继续）：

| 优先级 | 组件 | 源 page | 估计工作量 |
| --- | --- | --- | --- |
| P0 | Tag / Badge | `42:185530 Tag` / `42:185515 Badge` | 小（size × color variants） |
| P0 | Input | `42:185533 Input` | 中（size × state × prefix/suffix） |
| P0 | Switch | `41:3871 Switch` | 小 |
| P0 | Notification / Toast | `41:3875 Notification` | 中 |
| P1 | Modal | `42:71918 Modal` | 中 |
| P1 | Tabs | `42:71924 Tab` | 中（4 个 component set） |
| P1 | Pagination | `42:185509 Pagination` | 小 |
| P1 | Table | `42:185529 Table` | 中 |
| P1 | Upload | `42:185541 Upload` | 中（5 components） |
| P1 | Steps | `42:185512 Steps` | 小 |
| P2 | Banner | `41:3862 Banner` | 小 |
| P2 | Breadcrumb | `42:71926 Breadrumb` | 小 |
| P2 | Avatar | `42:185514 Avatar` | 小 |
| P2 | Collapse / Carousel / Countdown / Empty / Image / Number view / Video player | 数据展示 分类 | 小~中 |
| P2 | Number input / Slider / Time picker / Rate / Search / Download / Add fund | 数据录入 分类 | 小~中 |
| P2 | Anchor / Left menu / Header footer / progress bar / Announcement | 导航组件 分类 | 小 |
| P3 | Banner / Divider / Selector / Loading / Tooltips / User guide / results / Share modal / Coin title / Description / 404 | 剩余 | 小 |

## 可靠的重新抓取命令

下次 MCP 恢复后，用这段代码在源文件上重新 dump 完整目录（放到 `use_figma` 里跑）：

```js
const out = [];
const walk = (n) => {
  if (!("children" in n) || !n.children) return;
  for (const c of n.children) {
    if (c.type === "COMPONENT" || c.type === "COMPONENT_SET") {
      out.push(`${c.id}\t${c.type}\t${Math.round(c.width)}x${Math.round(c.height)}\t${c.name}`);
    }
    walk(c);
  }
};
for (const p of figma.root.children) {
  if (p.name.indexOf("---") === 0) continue;
  out.push(`# PAGE ${p.id} ${p.name}`);
  walk(p);
}
throw new Error(out.join("\n"));  // 抛出让 stderr 捕获
```

因为 throw 的 message 有长度限制，最好分页跑 —— 每次只跑一个 page 或一批 page，`slice(0, 15000)` 输出。
