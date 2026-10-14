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

`public/models/` 包含 13 个原创程序化 GLB（米、Y-up），`manifest.json` 记录
三角面数量与文件大小。`previews/` 包含每个资产的 PNG 和 `combined.png`。
来源说明见 [MODELS.md](assets/licenses/MODELS.md)，最新视觉规范见
[SCENE_SPEC.md](docs/SCENE_SPEC.md)。现有 `mac.glb` 保持原始字节。

网页与 Blender 预览共享 `src/components/room/scene-layout.json` 中的家具位置，
房间使用原生 6 × 5 × 2.8 米尺寸。点击 Walk / look 后鼠标控制视角，WASD / 方向键
行走，靠近办公椅或沙发按 E 坐下；也可点击座椅或界面坐下按钮。
坐下后按 E / Esc 或 Stand up 返回对应座椅旁的站立位置。
