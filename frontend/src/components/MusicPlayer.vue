<template>
  <div class="music-ctrl">
    <button class="mu-btn" @click="prev" title="上一首">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="19 20 9 12 19 4 19 20"/><line x1="5" y1="19" x2="5" y2="5"/></svg>
    </button>
    <button class="mu-btn" @click="toggle" title="暂停/播放">
      <svg v-if="playing" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="5" y="4" width="4" height="16"/><rect x="15" y="4" width="4" height="16"/></svg>
      <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="6,3 20,12 6,21"/></svg>
    </button>
    <button class="mu-btn" @click="next" title="下一首">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="5 4 15 12 5 20 19 20"/><line x1="19" y1="5" x2="19" y2="19"/></svg>
    </button>
    <span class="mu-name">{{ currentName }}</span>
    <audio ref="audioRef" @ended="next" @error="next" :src="currentSrc" preload="auto" autoplay />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const songs = [
  { name: '裹着心的光', file: '/林俊杰 - 裹着心的光.mp3' },
  { name: '光阴副本', file: '/林俊杰 - 光阴副本.mp3' },
  { name: '对的时间点', file: '/林俊杰 - 对的时间点.mp3' },
  { name: '7千3百多天', file: '/林俊杰 - 7千3百多天.mp3' },
  { name: '最好是', file: '/林俊杰 - 最好是.mp3' },
  { name: '最向往的地方', file: '/林俊杰 - 最向往的地方.mp3' },
]

const audioRef = ref(null)
const index = ref(0)
const playing = ref(false)

const currentSrc = computed(() => songs[index.value].file)
const currentName = computed(() => songs[index.value].name)

function toggle() {
  const a = audioRef.value
  if (!a) return
  if (a.paused) { a.play().catch(() => {}); playing.value = true }
  else { a.pause(); playing.value = false }
}

function next() {
  index.value = (index.value + 1) % songs.length
  playing.value = false
  setTimeout(() => {
    const a = audioRef.value
    if (a) { a.play().catch(() => {}); playing.value = true }
  }, 100)
}

function prev() {
  index.value = (index.value - 1 + songs.length) % songs.length
  playing.value = false
  setTimeout(() => {
    const a = audioRef.value
    if (a) { a.play().catch(() => {}); playing.value = true }
  }, 100)
}

let autoPlayTried = false
function tryAutoPlay() {
  const a = audioRef.value
  if (!a) return
  a.play().then(() => { playing.value = true; autoPlayTried = true }).catch(() => { playing.value = false })
}

onMounted(() => {
  // 方式1: HTML autoplay 属性已设置，浏览器会自行尝试
  // 方式2: JS 立即触发
  tryAutoPlay()
  // 方式3: 短延迟重试
  setTimeout(tryAutoPlay, 200)
  setTimeout(tryAutoPlay, 600)
  // 方式4: 页面完全加载后
  window.addEventListener('load', tryAutoPlay)
  // 方式5: 标签页切换回来时
  document.addEventListener('visibilitychange', () => { if (!document.hidden) tryAutoPlay() })
  // 方式6: 兜底——用户任何交互后立即播放
  const resume = () => { if (!autoPlayTried) tryAutoPlay(); document.removeEventListener('click', resume); document.removeEventListener('touchstart', resume) }
  document.addEventListener('click', resume)
  document.addEventListener('touchstart', resume)
})
</script>

<style scoped>
.music-ctrl { display: flex; align-items: center; gap: 4px; }
.mu-btn { width: 28px; height: 28px; border-radius: 50%; border: 1px solid rgba(255,255,255,0.15); background: rgba(255,255,255,0.06); color: #c8c8e0; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all .25s; flex-shrink: 0; }
.mu-btn:hover { background: rgba(255,255,255,0.15); color: #fff; }
.mu-name { font-size: 11px; color: var(--text-secondary); margin-left: 6px; max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>
