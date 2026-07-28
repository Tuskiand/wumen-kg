# DESIGN.md

# 吴门医案知识图谱管理系统 · 典雅中医古风设计规范

## 1. Visual Theme & Atmosphere

本项目采用“典雅中医古风”视觉风格，整体界面应体现中医古籍、吴门医派、知识图谱和现代管理系统的结合。

界面气质应为：

* 温润、克制、典雅
* 有传统中医文化感，但不能过度装饰
* 有知识管理系统的清晰结构
* 有数据分析系统的专业感
* 避免普通后台模板的冷蓝色科技风

整体视觉关键词：

```text
宣纸 / 古籍 / 水墨 / 竹影 / 印章 / 木色 / 墨绿 / 赭石 / 中医文化 / 知识图谱
```

页面背景以宣纸米白为主，局部可使用淡水墨山形、竹影、云纹、印章等作为弱装饰。装饰元素只能作为辅助氛围，不应影响文字阅读和功能操作。

## 2. Color Palette & Roles

### 2.1 Core Colors

| Token                    | Name | Hex       | Usage         |
| ------------------------ | ---- | --------- | ------------- |
| `--color-bg-page`        | 宣纸背景 | `#F7F1E6` | 页面整体背景        |
| `--color-bg-soft`        | 浅杏纸色 | `#FBF7EF` | 卡片、表单、弹窗背景    |
| `--color-bg-muted`       | 古纸浅灰 | `#EFE6D6` | 表格表头、分割区、次级背景 |
| `--color-text-main`      | 墨色正文 | `#2B2118` | 主标题、正文        |
| `--color-text-secondary` | 淡墨文字 | `#6F6255` | 副标题、说明文字      |
| `--color-border`         | 浅棕边框 | `#D8C8AE` | 卡片、输入框、表格边框   |
| `--color-primary`        | 深木棕  | `#8B5E34` | 主按钮、选中菜单、重点操作 |
| `--color-primary-dark`   | 深茶褐  | `#5C3A21` | 悬停状态、重要标题     |
| `--color-secondary`      | 墨绿   | `#2E6B57` | 成功状态、知识图谱重要节点 |
| `--color-accent`         | 赭石   | `#B86E4A` | 强调标签、图表高亮     |
| `--color-danger`         | 印章红  | `#A33A2A` | 删除、危险操作、错误提示  |
| `--color-warning`        | 杏黄   | `#D9A45F` | 警告、待处理状态      |
| `--color-info`           | 青灰   | `#5C7C7A` | 信息提示、辅助图表     |

### 2.2 Entity Type Colors

知识图谱中的实体类型颜色应保持统一，所有图谱、标签、图例、筛选器都使用同一套颜色。

| Entity Type | Meaning | Color     |
| ----------- | ------- | --------- |
| `A医家`       | 医家      | `#8B5E34` |
| `B病名`       | 病名      | `#B86E4A` |
| `C证型`       | 证型      | `#2E6B57` |
| `D病因`       | 病因      | `#D9A45F` |
| `E病机`       | 病机      | `#5C7C7A` |
| 其他类型        | 扩展实体    | `#8C7B6B` |

### 2.3 Usage Rules

Do:

* 使用宣纸色、木棕色、墨绿色作为主视觉。
* 使用印章红强调删除、错误、危险操作。
* 使用低饱和颜色，保证界面温和耐看。
* 图表颜色应与实体类型颜色保持一致。

Don't:

* 不要大面积使用科技蓝、荧光绿、紫色渐变。
* 不要使用纯黑大背景，除非是小面积强调区域。
* 不要让印章红大面积出现。
* 不要使用过多高饱和颜色。

## 3. Typography Rules

### 3.1 Font Families

项目不强制引入商业字体，应优先使用系统字体。

```css
font-family:
  "Noto Serif SC",
  "Songti SC",
  "SimSun",
  "Microsoft YaHei",
  serif;
```

后台管理、表格、数字密集区域可使用更清晰的无衬线字体：

```css
font-family:
  "Microsoft YaHei",
  "PingFang SC",
  "Noto Sans SC",
  sans-serif;
```

### 3.2 Typography Hierarchy

| Element        | Font Size | Weight | Color     | Usage |
| -------------- | --------: | -----: | --------- | ----- |
| Page Title     | 28px–32px |    700 | `#2B2118` | 页面主标题 |
| Section Title  | 20px–24px |    600 | `#5C3A21` | 模块标题  |
| Card Title     | 16px–18px |    600 | `#2B2118` | 卡片标题  |
| Body Text      | 14px–16px |    400 | `#2B2118` | 正文内容  |
| Secondary Text | 12px–14px |    400 | `#6F6255` | 说明、提示 |
| Table Text     | 13px–14px |    400 | `#2B2118` | 表格内容  |
| Chart Label    | 12px–13px |    400 | `#5C3A21` | 图表标签  |

### 3.3 Title Style

页面标题可适度使用宋体或仿宋风格，增强古籍感。

示例：

```text
吴门医案知识图谱管理系统
图谱探索
医家比较分析
路径查询
```

标题不应使用过度夸张的书法字体，避免影响可读性。

## 4. Component Stylings

### 4.1 Global Surfaces

页面主体使用浅宣纸背景。

```css
body {
  background: #F7F1E6;
  color: #2B2118;
}
```

主内容区域使用柔和纸张卡片：

```css
.surface-card {
  background: rgba(251, 247, 239, 0.92);
  border: 1px solid #D8C8AE;
  border-radius: 14px;
  box-shadow: 0 8px 24px rgba(92, 58, 33, 0.08);
}
```

### 4.2 Buttons

#### Primary Button

用于主要操作，例如查询、确认、开始比较、上传导入。

```css
.el-button--primary {
  background: #8B5E34;
  border-color: #8B5E34;
  color: #FFFFFF;
  border-radius: 8px;
}

.el-button--primary:hover {
  background: #5C3A21;
  border-color: #5C3A21;
}
```

#### Secondary Button

用于重置、返回、查看详情等次级操作。

```css
.el-button--default {
  background: #FBF7EF;
  border-color: #D8C8AE;
  color: #5C3A21;
  border-radius: 8px;
}

.el-button--default:hover {
  background: #EFE6D6;
  border-color: #8B5E34;
  color: #5C3A21;
}
```

#### Danger Button

用于删除、批量删除、禁用账号。

```css
.el-button--danger {
  background: #A33A2A;
  border-color: #A33A2A;
  color: #FFFFFF;
}
```

### 4.3 Inputs and Selects

输入框应为浅纸色背景，聚焦时使用深木棕边框。

```css
.el-input__wrapper,
.el-select__wrapper,
.el-textarea__inner {
  background: #FBF7EF;
  border-radius: 8px;
  box-shadow: 0 0 0 1px #D8C8AE inset;
}

.el-input__wrapper.is-focus,
.el-select__wrapper.is-focused {
  box-shadow: 0 0 0 1px #8B5E34 inset;
}
```

Placeholder 使用淡墨色：

```css
.el-input__inner::placeholder {
  color: #A79A8B;
}
```

### 4.4 Cards

卡片用于统计指标、图谱面板、筛选区、详情区、比较结果区。

```css
.el-card {
  background: rgba(251, 247, 239, 0.95);
  border: 1px solid #D8C8AE;
  border-radius: 14px;
  box-shadow: 0 8px 24px rgba(92, 58, 33, 0.08);
}
```

卡片标题建议左侧增加细线或印章色点缀：

```css
.card-title::before {
  content: "";
  display: inline-block;
  width: 4px;
  height: 16px;
  margin-right: 8px;
  border-radius: 2px;
  background: #8B5E34;
}
```

### 4.5 Tables

表格用于实体管理、关系管理、导入记录、用户管理、比较结果。

```css
.el-table {
  background: #FBF7EF;
  color: #2B2118;
  border-radius: 12px;
}

.el-table th {
  background: #EFE6D6;
  color: #5C3A21;
  font-weight: 600;
}

.el-table td {
  border-bottom: 1px solid #E4D7C3;
}
```

表格 hover 行：

```css
.el-table__body tr:hover > td {
  background: #F3E8D6 !important;
}
```

### 4.6 Tags

实体类型标签必须符合实体颜色系统。

```css
.tag-physician {
  background: rgba(139, 94, 52, 0.12);
  color: #8B5E34;
}

.tag-disease {
  background: rgba(184, 110, 74, 0.12);
  color: #B86E4A;
}

.tag-syndrome {
  background: rgba(46, 107, 87, 0.12);
  color: #2E6B57;
}

.tag-cause {
  background: rgba(217, 164, 95, 0.16);
  color: #9A6426;
}

.tag-mechanism {
  background: rgba(92, 124, 122, 0.14);
  color: #4D6E6C;
}
```

### 4.7 Navigation

侧边栏应采用浅棕米色背景，选中项使用深木棕或浅棕高亮。

```css
.sidebar {
  background: linear-gradient(180deg, #F7F1E6 0%, #EFE6D6 100%);
  border-right: 1px solid #D8C8AE;
}

.sidebar-item {
  color: #5C3A21;
  border-radius: 8px;
}

.sidebar-item.active {
  background: #8B5E34;
  color: #FFFFFF;
}
```

顶部栏保持简洁，避免过重阴影。

```css
.topbar {
  background: rgba(251, 247, 239, 0.92);
  border-bottom: 1px solid #D8C8AE;
  backdrop-filter: blur(8px);
}
```

### 4.8 Dialogs and Drawers

弹窗、抽屉背景采用浅纸色，标题区可加入淡棕色分割线。

```css
.el-dialog,
.el-drawer {
  background: #FBF7EF;
  border-radius: 14px;
}

.el-dialog__header {
  border-bottom: 1px solid #D8C8AE;
}
```

## 5. Layout Principles

### 5.1 Page Layout

用户端页面建议结构：

```text
顶部导航
左侧菜单
主内容区
  - 页面标题
  - 筛选查询区
  - 核心内容卡片
  - 图谱 / 表格 / 图表
```

管理端页面建议结构：

```text
左侧管理菜单
顶部操作栏
统计卡片
表格管理区
分页与批量操作
```

### 5.2 Spacing Scale

使用 4px 基础间距系统。

| Token       | Value | Usage   |
| ----------- | ----: | ------- |
| `--space-1` |   4px | 小图标间距   |
| `--space-2` |   8px | 表单内部间距  |
| `--space-3` |  12px | 标签、按钮间距 |
| `--space-4` |  16px | 卡片内部间距  |
| `--space-5` |  20px | 模块间距    |
| `--space-6` |  24px | 页面区块间距  |
| `--space-8` |  32px | 大区块间距   |

### 5.3 Grid

首页和看板页建议使用响应式网格：

```css
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 16px;
}
```

常见布局：

```text
统计卡片：3列或4列
图谱主面板：8列
右侧统计面板：4列
表格区：12列
```

### 5.4 Whitespace

界面需要留白，不能过度拥挤。古风界面的留白应像古籍页边距一样自然。

规则：

* 页面主内容区左右至少 24px padding。
* 卡片内部至少 16px padding。
* 图谱区域周围保留足够空白。
* 表格上方筛选区与表格之间至少 16px 间距。

## 6. Depth & Elevation

### 6.1 Shadow System

阴影要轻柔，模拟纸张悬浮感，不使用强烈黑色阴影。

```css
--shadow-sm: 0 2px 8px rgba(92, 58, 33, 0.06);
--shadow-md: 0 8px 24px rgba(92, 58, 33, 0.08);
--shadow-lg: 0 16px 40px rgba(92, 58, 33, 0.12);
```

### 6.2 Border System

边框使用浅棕色，不使用纯灰。

```css
--border-soft: 1px solid #E4D7C3;
--border-default: 1px solid #D8C8AE;
--border-strong: 1px solid #BCA886;
```

### 6.3 Surface Hierarchy

| Level            | Background | Border    | Shadow        |
| ---------------- | ---------- | --------- | ------------- |
| Page             | `#F7F1E6`  | none      | none          |
| Main Card        | `#FBF7EF`  | `#D8C8AE` | `--shadow-md` |
| Nested Panel     | `#F3E8D6`  | `#E4D7C3` | `--shadow-sm` |
| Floating Popover | `#FBF7EF`  | `#BCA886` | `--shadow-lg` |

## 7. Data Visualization Rules

### 7.1 ECharts Graph

图谱背景：

```js
backgroundColor: "#F7F1E6"
```

节点颜色：

```js
const entityColors = {
  "A医家": "#8B5E34",
  "B病名": "#B86E4A",
  "C证型": "#2E6B57",
  "D病因": "#D9A45F",
  "E病机": "#5C7C7A",
  "default": "#8C7B6B"
}
```

边样式：

```js
lineStyle: {
  color: "#BCA886",
  opacity: 0.55,
  width: 1,
  curveness: 0.12
}
```

标签：

```js
label: {
  show: true,
  color: "#2B2118",
  fontSize: 12,
  fontFamily: "Microsoft YaHei"
}
```

Tooltip：

```js
tooltip: {
  backgroundColor: "#FBF7EF",
  borderColor: "#D8C8AE",
  textStyle: {
    color: "#2B2118"
  }
}
```

### 7.2 Charts

柱状图、折线图、环形图、热力图、雷达图都应使用中医古风配色。

推荐图表色板：

```js
const chartPalette = [
  "#8B5E34",
  "#2E6B57",
  "#B86E4A",
  "#D9A45F",
  "#5C7C7A",
  "#A33A2A",
  "#8C7B6B"
]
```

### 7.3 Heatmap

医家比较热力图颜色不要使用默认蓝紫渐变，建议使用浅杏色到深木棕。

```text
low: #F7F1E6
middle: #D9A45F
high: #8B5E34
```

### 7.4 Radar Chart

雷达图用于医家综合比较。线条颜色使用医家对应色，背景网格使用浅棕色。

```text
grid line: #D8C8AE
axis name: #5C3A21
area opacity: 0.12
```

## 8. Page-Specific Guidelines

### 8.1 Login / Register Page

登录页应体现古籍封面和中医系统入口感。

要求：

* 左侧可放系统名称、简短说明、水墨山形或竹影背景。
* 右侧为登录卡片。
* 登录卡片背景使用浅纸色。
* 主按钮使用深木棕。
* 注册入口使用墨绿色或深木棕文字链接。

标题示例：

```text
吴门医案知识图谱管理系统
知识图谱 · 医案整理 · 医家比较
```

### 8.2 Portal Home

首页应展示系统概览。

建议模块：

* 图谱总节点数
* 图谱总关系数
* 医家数量
* 病名数量
* 最近导入记录
* 快捷入口：图谱检索、图谱探索、路径查询、医家比较

视觉要求：

* 统计卡片采用古籍纸张样式。
* 快捷入口图标使用线性图标，颜色为深木棕或墨绿。
* 首页可加入淡水墨背景，不要影响数据阅读。

### 8.3 Graph Exploration Page

图谱探索页是系统视觉重点。

要求：

* 左侧或顶部为筛选区。
* 中间为大面积图谱画布。
* 右侧为图例、节点统计、关系统计。
* 节点颜色严格按实体类型分配。
* 画布背景为浅宣纸色。
* 提供缩放、重置、全屏等操作按钮。

### 8.4 Entity Detail Page

实体详情页应像“知识条目卡片”。

建议结构：

```text
实体名称
实体类型标签
摘要说明
来源医案
相关节点
相关关系
局部图谱
```

视觉要求：

* 标题区可使用古籍条目感样式。
* 来源信息以浅棕色标签展示。
* 相关关系表格保持清晰。

### 8.5 Path Query Page

路径查询页应突出“关系链路”。

建议结构：

```text
查询表单
路径结果列表
路径图谱可视化
路径详情面板
```

路径图中的起点、终点应有更明显的边框或光晕，但颜色仍需克制。

### 8.6 Physician Compare Page

医家比较页是重点应用页面，应具有数据分析感。

页面结构：

```text
病名输入 / 选择
分析概览
节点比较 Tab
辨证路径比较 Tab
子图比较 Tab
结果解释区
```

节点比较：

* 使用相似度矩阵、共同节点表、独有节点表。
* RWR Top 节点可用条形图展示。
* FastRP 相似度可用热力图展示。

辨证路径比较：

* D-E-C 路径可用桑基图或路径列表展示。
* 共享路径和独有路径应清晰区分。
* 路径完整度可用进度条或小型统计卡展示。

子图比较：

* 子图统计使用表格或卡片。
* Jaccard、Graph2Vec 等结果用热力图或雷达图展示。
* 局部子图可视化仍按实体颜色规则展示。

### 8.7 Admin Pages

管理端需要比用户端更简洁，但仍保持统一古风。

适用页面：

* 管理看板
* 实体管理
* 关系管理
* 图谱导入
* 用户管理
* 版本记录
* 审计记录

要求：

* 表格清晰优先，装饰减少。
* 操作按钮颜色统一。
* 批量删除等危险操作使用印章红。
* 导入流程可使用步骤条，步骤条颜色使用深木棕。

## 9. Responsive Behavior

### 9.1 Breakpoints

| Breakpoint   |          Width | Behavior        |
| ------------ | -------------: | --------------- |
| Mobile       |      `< 768px` | 侧边栏折叠，卡片单列      |
| Tablet       | `768px–1199px` | 双列布局，图谱面板压缩     |
| Desktop      |    `>= 1200px` | 完整侧边栏，多列卡片      |
| Large Screen |    `>= 1600px` | 图谱区域加宽，右侧统计面板固定 |

### 9.2 Mobile Rules

移动端不需要展示复杂完整图谱细节，应优先保证：

* 查询表单可用
* 列表可读
* 卡片单列展示
* 图谱允许横向滚动或全屏查看
* 表格可横向滚动

### 9.3 Touch Targets

所有按钮和可点击项高度不小于 36px。

```css
button,
.el-button,
.sidebar-item {
  min-height: 36px;
}
```

## 10. Motion & Interaction

交互动效应温和，不使用强烈弹跳动画。

推荐：

```css
transition: all 0.18s ease;
```

Hover 效果：

* 卡片轻微上浮
* 按钮颜色加深
* 表格行浅杏色高亮
* 图谱节点 hover 放大 1.05 倍以内

不要使用：

* 大面积闪烁
* 高速旋转
* 过强发光
* 复杂页面切换动画

## 11. Do's and Don'ts

### Do

* 保持“中医古籍感”和“现代系统可用性”的平衡。
* 使用统一的实体颜色系统。
* 优先保证表格、图谱、图表的可读性。
* 使用浅纸色背景和柔和卡片。
* 控制装饰元素，只作为氛围点缀。
* 保持 Element Plus 组件的一致覆盖样式。
* 保持接口、路由、业务逻辑不变。

### Don't

* 不要把系统做成纯图片展示页。
* 不要为了古风牺牲可读性。
* 不要大面积使用毛笔字。
* 不要使用过多水墨背景导致文字不清。
* 不要使用默认 Element Plus 蓝色作为主色。
* 不要修改接口字段、数据结构和后端逻辑。
* 不要重写整个项目结构。
* 不要引入过重的 UI 库替换现有 Element Plus。

## 12. Implementation Notes for Coding Agents

当前项目技术栈：

```text
Vue 3
TypeScript
Element Plus
Vue Router
ECharts
FastAPI
Neo4j
MySQL
```

前端美化时应优先修改：

```text
src/styles/
src/assets/
src/components/
src/layouts/
src/views/
```

建议新增：

```text
src/styles/ancient-tcm-theme.css
src/styles/echarts-theme.ts
src/assets/patterns/
src/assets/design-reference/
```

不要改动：

```text
接口字段
API 路径
登录鉴权逻辑
Neo4j 查询逻辑
医家比较算法逻辑
CSV 导入数据结构
```

如果需要改动页面结构，只能在不影响数据流和业务功能的前提下调整布局。

## 13. CSS Variables Starter

建议在全局样式中定义以下变量：

```css
:root {
  --color-bg-page: #F7F1E6;
  --color-bg-soft: #FBF7EF;
  --color-bg-muted: #EFE6D6;

  --color-text-main: #2B2118;
  --color-text-secondary: #6F6255;

  --color-border: #D8C8AE;
  --color-border-soft: #E4D7C3;
  --color-border-strong: #BCA886;

  --color-primary: #8B5E34;
  --color-primary-dark: #5C3A21;
  --color-secondary: #2E6B57;
  --color-accent: #B86E4A;
  --color-danger: #A33A2A;
  --color-warning: #D9A45F;
  --color-info: #5C7C7A;

  --entity-physician: #8B5E34;
  --entity-disease: #B86E4A;
  --entity-syndrome: #2E6B57;
  --entity-cause: #D9A45F;
  --entity-mechanism: #5C7C7A;
  --entity-default: #8C7B6B;

  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 14px;
  --radius-xl: 20px;

  --shadow-sm: 0 2px 8px rgba(92, 58, 33, 0.06);
  --shadow-md: 0 8px 24px rgba(92, 58, 33, 0.08);
  --shadow-lg: 0 16px 40px rgba(92, 58, 33, 0.12);

  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
}
```

## 14. Agent Prompt Guide

When using Codex or another coding agent, use this instruction:

```text
请读取项目根目录 DESIGN.md，并严格按照其中“吴门医案知识图谱管理系统 · 典雅中医古风设计规范”美化当前前端。

要求：
1. 保持现有 Vue3 + TypeScript + Element Plus + ECharts 技术栈不变。
2. 不修改后端接口、接口字段、路由逻辑和业务逻辑。
3. 优先新增全局主题样式文件，并统一覆盖 Element Plus 默认蓝色风格。
4. 将用户端和管理端页面统一调整为宣纸背景、深木棕主色、墨绿辅助色、印章红危险色的典雅中医古风。
5. 图谱节点颜色必须按 A医家、B病名、C证型、D病因、E病机 的实体类型固定映射。
6. ECharts 图谱、热力图、雷达图、柱状图均使用 DESIGN.md 中的古风配色。
7. 保留所有现有功能，包括登录、注册、图谱检索、图谱探索、实体详情、路径查询、医家比较、后台管理、CSV 导入。
8. 修改完成后列出改动文件、主要改动点和运行方式。
```

## 15. Acceptance Criteria

美化完成后应满足：

* 页面整体不再是默认 Element Plus 蓝白后台风格。
* 登录页、首页、图谱探索页、路径查询页、医家比较页、后台管理页风格统一。
* 主色为深木棕，辅助色为墨绿，背景为宣纸米白。
* 表格、按钮、输入框、卡片、弹窗都符合古风主题。
* ECharts 图谱节点颜色与实体类型一致。
* 图谱画布、图例、tooltip 视觉统一。
* 删除和危险操作使用印章红。
* 页面可读性良好，没有装饰遮挡文字。
* 业务功能、接口调用和数据展示不受影响。
