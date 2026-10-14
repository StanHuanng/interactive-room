# Interactive Personal Room — 开发计划

## 目标综述

构建可公开访问的第一人称 3D Web 房间：自由行走探索 + 电影式坐下动画，接近办公椅进入可操作工作界面，接近红色沙发进入娱乐界面并可启动简单网页小游戏；退出后自然回到 3D 场景对应位置。

技术栈：React、TypeScript、Vite、Three.js、React Three Fiber、@react-three/drei；碰撞与动画库按需引入。3D 资产优先程序化建模与明确授权的现成模型；无 Blender / GPU 时不阻塞，继续用 Three.js 几何。

---

## 阶段 0：环境与初始化（本阶段）

- [x] 检查 Node / npm / Git / Chrome / WebGL / Blender
- [x] 在 `/workspace/interactive-room` 建立 Vite + React + TS + R3F 项目
- [x] 灰盒房间 stub + 本地 Git
- [ ] 用户授权后创建独立 GitHub 仓库并推送
- [ ] 选定 HTTPS 部署目标（建议 Vercel 或 Netlify）

**环境结论摘要**

| 工具 | 状态 | 说明 |
|------|------|------|
| Node.js | ✅ v20.19.2 | 可用 |
| npm | ✅ 9.2.0 | 默认包管理器 |
| pnpm | ✅ 可用 | 备选 |
| yarn | ❌ | 未安装 |
| Git | ✅ 2.47.3 | 本地仓库已初始化 |
| Chrome | ✅ | 可用于构建后预览 |
| WebGL | ⚠️ 软件路径 | 无 `/dev/dri` / 无 NVIDIA；headless 可创建 WebGL 上下文，真实视觉验收建议用户本机浏览器 |
| Blender | ❌ | 未安装 → 使用程序化几何 / 外部授权 GLTF |

---

## 阶段 1：MVP（优先可运行）

目标：简化 3D 房间可进入、自由行走、办公椅 / 沙发交互、网页切换与退出返回。**不做精细装饰。**

1. **第一人称控制**  
   Pointer Lock + WASD 移动；简单碰撞（墙体 / 家具 AABB 或后续 Rapier）。

2. **交互热点**  
   - 接近办公椅 → 提示按 `E` → 相机 sit-down 动画 → 切换到工作界面 Overlay  
   - 接近红色沙发 → 提示按 `E` → 另一套相机动画 → 娱乐界面 Overlay  

3. **UI Overlay（占位）**  
   - 工作界面：模拟数据 / 占位面板（暂不接 Grok API）  
   - 娱乐界面：可启动一个极简网页小游戏（或新标签打开，遵守站点限制）  
   - 退出键（如 `Esc`）→ 回到 3D 中椅子 / 沙发旁的站立位

4. **模块边界**  
   `room` / `camera` / `interaction` / `ui` 相互独立，状态集中（如 Zustand / 简单 React context）。

5. **验收**  
   `npm run build` 通过；本机浏览器走通：进房 → 走 → 坐椅 → 退出 → 坐沙发 → 小游戏 → 退出。

提交点：MVP 功能合并后推送 GitHub（需用户授权仓库）。

---

## 阶段 2：视觉还原

在 MVP 稳定后再投入：

- 按参考图还原深色木质家具、暖色灯光、办公区与红色沙发比例与材质
- 引入有明确授权的 GLTF / 贴图，并在 `assets/licenses` 记录来源与许可
- 必要时再考虑安装 Blender 或离线烘焙；无 Blender 则继续程序化 + 外部资产

提交点：视觉里程碑截图 + 构建产物。

---

## 阶段 3：测试与部署

1. **测试**  
   构建、交互回归；云端无真 GPU 时明确限制，由用户本机做视觉验收；保留测试截图。

2. **部署（建议）**  
   - **Vercel** 或 **Netlify**：静态 `vite build` 产物，自动 HTTPS  
   - 或 GitHub Pages（若仓库公开且可接受路径限制）  
   - 需要账号连接 / 付款时先征得用户同意

3. **交付**  
   可直接打开的 HTTPS 地址 + README 操作说明。

---

## 约束与原则

- 优先可运行结果，避免过早沉溺装饰细节
- 不把 API Key、密码等敏感凭据写入仓库
- 第三方资产必须记录许可；无法嵌入的站点用新标签打开，不绕过网站限制
- 付款、密钥、扩大账号权限前先征得用户同意
- 每个主要阶段结束后提交 GitHub

---

## 建议下一步（需用户确认）

1. 授权创建独立 GitHub 仓库并推送当前 stub  
2. 确认部署偏好：Vercel / Netlify / 其他  
3. 是否提供室内设计参考图的本地副本路径（若尚未放入项目）  
4. 是否允许安装可选依赖（如 `@react-three/rapier`、动画库）
