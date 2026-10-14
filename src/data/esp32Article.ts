// Editorial summary copied into the app from /workspace/x-article/v7-gpt/draft.md.
// This is local content: the web app does not depend on that workspace path.
export const esp32Article = {
  title: '原来，Claude 早就给 ESP32 留了个按钮',
  summary: [
    'Claude 的 Hardware Buddy 让 ESP32 不只显示任务状态，还能通过实体按钮批准或拒绝某一次请求，把人的决定送回电脑；它目前仍是开发者模式中的参考实现。',
    '与小智通过 MCP 执行设备动作不同，Buddy 把审批交给人：状态快照和带编号的请求经 BLE 下发，按钮再回传同一编号及批准或拒绝的决定。',
    '文章进一步提出 BLE → PC 桥接 → WebSocket/HTTPS → 云端 bot 的链路，让云端任务在需要人决定时停到手边；其中 bot 端的 listener 仍需开发。',
  ],
  href: '#', // TODO: replace with the original X article URL.
  source: '@1psumesse',
} as const
