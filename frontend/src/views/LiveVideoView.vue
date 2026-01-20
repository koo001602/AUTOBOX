<template>
  <div class="live-container">
    <div class="video-feed">
      <div class="feed-header">
        <span class="record-dot">●</span>
        <span class="cam-name">LIVE CAM 01</span>
      </div>

      <div class="feed-placeholder">
        <span class="icon">📹</span>
        <p>Camera Feed Unavailable</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.live-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.video-feed {
  flex: 1;
  background-color: #000;
  border-radius: 16px;
  border: 1px solid #334155;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}

.feed-header {
  position: absolute;
  top: 20px;
  left: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: monospace;
}

.record-dot {
  color: #ef4444;
  font-size: 1.2rem;
  animation: blink 2s infinite;
}

.cam-name {
  color: #fff;
  font-weight: bold;
  letter-spacing: 1px;
}

.feed-placeholder {
  text-align: center;
  color: #475569;
}

.feed-placeholder .icon {
  font-size: 4rem;
  display: block;
  margin-bottom: 10px;
  opacity: 0.5;
}

.feed-placeholder p {
  font-size: 1.2rem;
  font-weight: 300;
}

/* 깜빡임 애니메이션 */
@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0.4; }
  100% { opacity: 1; }
}
</style>