<template>
  <div class="video-container" style="position: relative;">
    <video
      ref="videoPlayer"
      class="video-js vjs-16-9 vjs-default-skin vjs-fluid"
      controls
      :autoplay="options.autoplay"
      :preload="options.preload"
      data-setup="{}"
    >
      <source :src="currentVideoUrl" type="video/mp4" />
    </video>
    <div class="video-overlay-text" >
          <span v-if="currentVideoStats.batter_name" class="underline">
          {{ currentVideoStats.batter_name }} ( {{ currentIndex + 1}}/{{ videos.length }} )
          </span><br v-if="currentVideoStats.hit_speed">

          <span v-if="currentVideoStats.pitch_name || currentVideoStats.start_speed">
            {{ currentVideoStats.pitch_name }} {{ currentVideoStats.start_speed }} MPH
          </span><br v-if="currentVideoStats.pitch_name || currentVideoStats.start_speed">
          
          <span v-if="currentVideoStats.hit_speed">
            Exit: {{ currentVideoStats.hit_speed }} MPH @ {{ currentVideoStats.hit_angle }}°
          </span><br v-if="currentVideoStats.hit_speed">
          
          <span v-if="currentVideoStats.hit_distance">
            Distance: {{ currentVideoStats.hit_distance }} ft
          </span><br v-if="currentVideoStats.hit_distance">
          
          <span v-if="currentVideoStats.xba">
            xBA: {{ currentVideoStats.xba }}
          </span><br v-if="currentVideoStats.xba">
          
          <span v-if="currentVideoStats.hr_cat !== undefined" style="color: red;">
            Home Run: {{ currentVideoStats.hr_cat }}
          </span><br v-if="currentVideoStats.hr_cat !== undefined">
          
          <span v-if="currentVideoStats.hr_ct !== undefined" style="color: red;">
            Home Run Parks: {{ currentVideoStats.hr_ct }} / 30
          </span><br v-if="currentVideoStats.hr_ct !== undefined">
    </div>
    <Button @click="prevVideo" :disabled="currentIndex === 0" style="margin-right: 10px;">Previous Video</Button>
     <Button @click="nextVideo" :disabled="currentIndex === videos.length - 1" style="margin-right: 10px;">Next Video</Button>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import videojs from 'video.js';
import 'video.js/dist/video-js.css';

const props = defineProps({
  videos: Array
});

const currentIndex = ref(0);
const videoPlayer = ref(null);
const screenWidth = ref(window.innerWidth);
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

const currentVideoUrl = computed(() => props.videos[currentIndex.value].mp4);
const currentVideoStats = computed(() => props.videos[currentIndex.value]);

onMounted(() => {
  const player = videojs(videoPlayer.value, {
    ...options,
    controlBar: {
      playbackRateMenuButton: {
        rates: options.playbackRates
      }
    }
  });

  player.volume(options.volume);

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

  watch(currentVideoUrl, (newVal) => {
    console.log('Changing video to', newVal);
    player.src({ type: 'video/mp4', src: newVal });
  });
});

function nextVideo() {
  if (currentIndex.value < props.videos.length - 1) {
    currentIndex.value += 1;
  }
}

function prevVideo() {
  if (currentIndex.value > 0) {
    currentIndex.value -= 1;
  }
}
</script>

<style scoped>
.video-js {
  margin-bottom: 5px;
}


</style>