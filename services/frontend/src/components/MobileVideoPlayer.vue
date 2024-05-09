<template>
  <div class="video-container">

    <video
      ref="videoPlayer"
      class="video-js vjs-16-9 vjs-default-skin vjs-fluid"
      controls
      :autoplay="options.autoplay"
      :preload="options.preload"
      d
      data-setup="{}"
    >
      <source :src="videoUrl" type="video/mp4" />
    </video>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import videojs from 'video.js';
import 'video.js/dist/video-js.css';

const props = defineProps({
  videos: Array,
  videoUrl: String
});
const videoPlayer = ref(null);
const screenWidth = ref(window.innerWidth);

// Assuming a common aspect ratio of 16:9 for videos
const videoHeight = computed(() => (screenWidth.value / 16) * 9);
const videoWidth = ref(100); // Use a reactive property if you need to adjust it dynamically
const options = {
  controls: true,
  autoplay: false,
  playsinline: true,
  responsive: true,
  fluid: true,
  preload: 'auto',
  volume: 0.6,
  playbackRates: [0.7, 1.0, 1.5, 2.0]
};

onMounted(() => {
  const player = videojs(videoPlayer.value, {
    ...options,
    controlBar: {
      playbackRateMenuButton: {
        rates: options.playbackRates
      }
    }
  });

  // Set initial volume
  player.volume(options.volume);

  // Handling multiple events
  const events = [
    'play', 'pause', 'ended', 'loadeddata', 'waiting',
    'playing', 'canplay', 'canplaythrough', 'timeupdate'
  ];

  events.forEach(event => {
    player.on(event, () => {
      if (event === 'timeupdate') {
        console.log(`Event: ${event}, Current Time: ${player.currentTime()}`);
      } else {
        console.log(`Event: ${event}`);
      }
    });
  });

  watch(() => props.videoUrl, (newVal) => {
    if (newVal) {
      player.src({ type: 'video/mp4', src: newVal });
    }
  });

});

</script>
<style scoped>
.video-js {
  margin-bottom:  5px;
}
/* Ensures video.js player fills the container without overflow */
/* .video-js {
  width: 100% !important;
  height: auto !important;
} */
</style>