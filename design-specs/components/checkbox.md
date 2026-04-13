# Checkbox / Radio / Half-select

> 来源 Figma 节点: `33:14060` (Checkbox)
> 主组件集: `CheckboxV5-Web`、`GTCheckboxV5/item-12px`、`GTCheckboxV5/item-16px`、`GTCheckboxV5/label-12px`、`GTCheckboxV5/label-14px`

## 1. 组件类型

| Type | 含义 | 形状 |
| --- | --- | --- |
| **Checkbox** | 多选框 | 方形 |
| **Half / Half Select** | 半选状态（用于父子级联） | 方形 + 横线 |
| **Radio** | 单选 | 圆形 |

## 2. 变体维度

每种组件都遵循同一组变体维度：

| 维度 | 取值 | 备注 |
| --- | --- | --- |
| **Status** | `Active` / `Inactive` | 选中 / 未选中 |
| **Size** | `Small-12px` / `Medium-16px` | 小尺寸 12px、中尺寸 16px |
| **Disable** | `False` / `True` | 是否禁用 |
| **Hover** | `False` / `True` | 是否悬浮（仅 web） |

> 由于 Disable 与 Hover 不能同时为 True，每个组件实际有 12 个有效变体（Status × Size × {Default, Hover, Disable}）。

## 3. 尺寸与排版

| Size | 控件尺寸 | 推荐 label 字号 |
| --- | --- | --- |
| Small | 12 × 12 px | 12 px (`12/CN-Regular`) |
| Medium | 16 × 16 px | 14 px (`14/CN-Regular`) |

控件与文字的水平间距固定为 8 px。

## 4. 颜色 Token

| 用途 | Token | 值 |
| --- | --- | --- |
| 选中态填充 | `--color-cmpt-button-primary` | `#303236` |
| 未选中描边 | `--color-line-border-strong` | `#DFE0E2` |
| 禁用态背景 | `--color-cmpt-button-soft-disable` | `#F5F6F7` |
| 禁用态文字 | `--color-text-text-disable` | `#C4C7CA` |
| 主文字 | `--color-text-text-primary` | `#070808` |
| 控件 ✓ 颜色 | `--color-text-inverse-primary` | `#FFFFFF` |
| 默认背景 | `--color-bg-primary` | `#FFFFFF` |

## 5. Label 子组件

`GTCheckboxV5/label-12px` 与 `GTCheckboxV5/label-14px` 提供 3 种独立的视觉样式，用于不同场景：

| 名称 | 含义 |
| --- | --- |
| `Dash=False, Solid=False` | 默认（无装饰） |
| `Dash=True,  Solid=False` | 半选状态（短横） |
| `Dash=False, Solid=True`  | 完全选中（实心） |

## 6. 状态变体清单（CheckboxV5-Web 中的命名）

完整变体命名以 `Type=…, Status=…, Size=…, Disable=…, Hover=…` 形式给出，例如：

```
Type=Checkbox, Status=Active,   Size=Small-12px,  Disable=False, Hover=False
Type=Checkbox, Status=Active,   Size=Small-12px,  Disable=False, Hover=True
Type=Checkbox, Status=Active,   Size=Small-12px,  Disable=True,  Hover=False
Type=Checkbox, Status=Inactive, Size=Medium-16px, Disable=False, Hover=False
Type=Half,     Status=Active,   Size=Medium-16px, Disable=False, Hover=False
Type=Radio,    Status=Active,   Size=Small-12px,  Disable=False, Hover=False
```

> 三种 Type（Checkbox / Half / Radio）共有 36 个变体（12 × 3）。
