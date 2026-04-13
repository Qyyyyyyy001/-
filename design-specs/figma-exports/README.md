# Figma 导出

> 来源 Figma 文件: `Pay-B端 组件规范 - Yang` (`vCt8aPJKNCIrvkAo1nLph7`)
> 入口 Canvas: `1:64` (基础组件)

本目录用于存放从 Figma 文件导出的 5 个核心区块的 PNG 图片，作为 [`design-specs/`](../) 文档的视觉参考。

## 导出清单

| 区块 | Node ID | 尺寸（pt） | 文件 | 对应规范 | Figma 直链 |
| --- | --- | ---: | --- | --- | --- |
| Fonts | `1:215` | 1687 × 2578 | `fonts.png` | [`typography.md`](../typography.md) | [打开](https://www.figma.com/design/vCt8aPJKNCIrvkAo1nLph7/Pay-B%E7%AB%AF-%E7%BB%84%E4%BB%B6%E8%A7%84%E8%8C%83---Yang?node-id=1-215) |
| Color | `1:393` | 1766 × 2578 | `color.png` | [`colors.md`](../colors.md) | [打开](https://www.figma.com/design/vCt8aPJKNCIrvkAo1nLph7/Pay-B%E7%AB%AF-%E7%BB%84%E4%BB%B6%E8%A7%84%E8%8C%83---Yang?node-id=1-393) |
| Spacing | `33:296` | 1687 × 3228 | `spacing.png` | [`spacing.md`](../spacing.md) | [打开](https://www.figma.com/design/vCt8aPJKNCIrvkAo1nLph7/Pay-B%E7%AB%AF-%E7%BB%84%E4%BB%B6%E8%A7%84%E8%8C%83---Yang?node-id=33-296) |
| Button | `33:11329` | 5789 × 5550 | `button.png` | [`components/button.md`](../components/button.md) | [打开](https://www.figma.com/design/vCt8aPJKNCIrvkAo1nLph7/Pay-B%E7%AB%AF-%E7%BB%84%E4%BB%B6%E8%A7%84%E8%8C%83---Yang?node-id=33-11329) |
| Checkbox | `33:14060` | 1200 × 5550 | `checkbox.png` | [`components/checkbox.md`](../components/checkbox.md) | [打开](https://www.figma.com/design/vCt8aPJKNCIrvkAo1nLph7/Pay-B%E7%AB%AF-%E7%BB%84%E4%BB%B6%E8%A7%84%E8%8C%83---Yang?node-id=33-14060) |

## 使用 fetch.py 自动下载

`fetch.py` 通过 Figma 官方 REST API 把 `manifest.json` 中列出的所有节点渲染成 PNG，写入本目录：

```bash
# 1. 在 https://www.figma.com/developers/api#access-tokens 申请个人访问 token
export FIGMA_TOKEN=figd_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 2. 运行脚本
python3 design-specs/figma-exports/fetch.py

# 可选: 指定缩放比例 / 格式
python3 design-specs/figma-exports/fetch.py --scale 2 --format png
```

运行后会得到：

```
design-specs/figma-exports/
├── fonts.png       # 1687 × 2578 (×2 = 3374 × 5156)
├── color.png       # 1766 × 2578
├── spacing.png     # 1687 × 3228
├── button.png      # 5789 × 5550 — 大图，含全部 ~700 个按钮变体
└── checkbox.png    # 1200 × 5550
```

## 通过 Claude / MCP 重新导出

如果使用 Claude Code 配合 Figma MCP，可以通过 `get_screenshot` 工具直接获取截图（无需 token）：

```text
@figma get screenshot of nodeId=1:215 fileKey=vCt8aPJKNCIrvkAo1nLph7
```

或者一次性触发本目录的导出流程：

> 把 design-specs/figma-exports/manifest.json 中列出的 5 个节点都用 Figma MCP 截屏一遍

## 注意

- `button.png` 因为包含 5 类型 × 5 状态 × 7 尺寸 × 4 图标变体 ≈ 700 个变体，
  原始尺寸接近 6000 × 5500，建议导出 `--scale 1` 节省体积。
- `manifest.json` 中保存的 `imageUrl` 字段只是 REST API 的查询模板，
  真实下载链接需要通过 token 调用 `GET /v1/images/:fileKey?ids=...` 之后从响应里取。
- 仓库默认不会落地 PNG 文件（避免大量二进制污染历史），
  如确需提交，请在 git add 之前确认 `.gitignore` 没有屏蔽 `design-specs/figma-exports/*.png`。
