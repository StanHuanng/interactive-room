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
