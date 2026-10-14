# Interactive Personal Room

第一人称可交互 3D Web 房间（React + TypeScript + Vite + Three.js / R3F）。

## 本地开发

```bash
npm install
npm run dev
```

## 构建

```bash
npm run build
npm run preview
```

## 目录结构（模块化）

- `src/components/room` — 房间几何与灯光
- `src/components/camera` — 第一人称 / 电影式相机
- `src/components/interaction` — 椅子、沙发等交互触发
- `src/components/ui` — 工作台 / 娱乐界面叠加层
- `assets/licenses` — 第三方模型与贴图许可记录

详见 `DEVELOPMENT_PLAN.md`。

## Blender 模型与预览

使用 Blender 4.2.3 LTS（无需 GPU）：

```bash
blender -b -P blender/build_assets.py
blender -b -P blender/render_previews.py
```

`public/models/` 包含 5 个原创低多边形 GLB（米、Y-up、平面着色），
`manifest.json` 记录三角面数量与文件大小。`previews/` 包含各模型和组合场景的
1280 × 720 Cycles CPU 预览。来源说明见 [MODELS.md](assets/licenses/MODELS.md)。

`src/components/room/models/` 使用 `useGLTF`、预加载和 Suspense。
`layout.ts` 保留原有家具 X/Z 坐标；6 × 5 米房间模型在网页中缩放至原有的
10 × 10 米范围，电脑放置在 0.75 米桌面上。
