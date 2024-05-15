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

    <div class="video-overlay-text video-overlay-text-top-left" v-if="(!currentVideoStats.hit_speed || !isPlaying)">
          <span v-if="currentVideoStats.batter_name" class="bold-outline">
          {{ currentVideoStats.batter_name }} ( {{ currentIndex + 1}}/{{ videos.length }} )
          </span><br v-if="currentVideoStats.batter_name">
          <span v-if="currentVideoData.date" >
          {{ currentVideoData.formattedDate  }} 
          </span><br v-if="currentVideoData.date">
          <span v-if="currentVideoStats.pitch_name || currentVideoStats.start_speed">
            {{ currentVideoStats.pitch_name }} {{ currentVideoStats.start_speed }} MPH
          </span><br v-if="currentVideoStats.pitch_name || currentVideoStats.start_speed">
         
    </div>
    <div class="video-overlay-text video-overlay-text-top-right" >
          

          <span v-if="currentVideoStats.hit_speed">
          Exit: {{ currentVideoStats.hit_speed }} MPH @ {{ currentVideoStats.hit_angle }}°
          </span><br v-if="currentVideoStats.hit_speed">
          <span v-if="currentVideoStats.hit_distance">
            Distance: {{ currentVideoStats.hit_distance }} ft
          </span><br v-if="currentVideoStats.hit_distance">
          
          <span v-if="currentVideoStats.xba">
            xBA: {{ currentVideoStats.xba }}
          </span><br v-if="currentVideoStats.xba">
          <div v-if="!isPlaying">
            <span v-if="currentVideoStats.bat_speed">
              Bat Speed: {{ currentVideoStats.bat_speed }} MPH
            </span><br v-if="currentVideoStats.bat_speed">
            <span v-if="currentVideoStats.swing_length">
              Swing Length: {{ currentVideoStats.swing_length }} ft
            </span><br v-if="currentVideoStats.swing_length">
          </div>
    </div>
    <div class="video-overlay-text video-overlay-text-bottom-center" v-if="!isPlaying" >
          <span v-if="currentVideoStats.hr_ct !== undefined && currentVideoStats.hr_cat !== undefined" style="color: red;">
            HR Parks: {{ currentVideoStats.hr_ct }} / 30 ->  {{ currentVideoStats.hr_cat }}
          </span><br v-if="currentVideoStats.hr_ct !== undefined && currentVideoStats.hr_cat !== undefined">
    </div>


    <Button @click="prevVideo" :disabled="currentIndex === 0" style="margin-right: 10px;">Previous Video</Button>
     <Button @click="nextVideo" :disabled="currentIndex === videos.length - 1" style="margin-right: 10px;">Next Video</Button>
     <Button @click="copyLinkToClipboard" icon="pi pi-copy" severity="info" rounded  aria-label="Copy Link To Video" />


  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import videojs from 'video.js';
import 'video.js/dist/video-js.css';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
const props = defineProps({
  videos: Array,
  reset: Boolean,
  currentQuery: Object
});

const currentIndex = ref(0);
const videoPlayer = ref(null);
const screenWidth = ref(window.innerWidth);
const router = useRouter();
const formattedDate = ref(null);
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
const isPlaying = ref(false);

const currentVideoUrl = computed(() => props.videos[currentIndex.value].mp4 + '#t=0.5' );
const currentPitch = computed(() => props.currentQuery.current_pitch);

const currentVideoStats = computed(() => {
  let stats = {...props.videos[currentIndex.value]};
  if (stats.bat_speed) {
    stats.bat_speed = parseFloat(stats.bat_speed).toFixed(0);
  }
  if (stats.swing_length) {
    stats.swing_length = parseFloat(stats.swing_length).toFixed(2);
  }
  return stats;
});
const currentVideoData = computed(() => {
  const videoData = props.currentQuery;
  // Check if the date exists and is a valid date string or Date object
  if (videoData.date) {
    let parsedDate;

    // Check if date is already a Date object or a string
    if (videoData.date instanceof Date) {
      // If it's a Date object, use it directly
      parsedDate = videoData.date;
    } else if (typeof videoData.date === 'string') {
      // If it's a string, parse it to avoid timezone issues
      const parts = videoData.date.split('-');
      const year = parseInt(parts[0], 10);
      const month = parseInt(parts[1], 10) - 1; // Month is 0-indexed in JavaScript Date
      const day = parseInt(parts[2], 10);
      parsedDate = new Date(year, month, day);
    }

    // Format the date as mm/dd/yyyy
    videoData.formattedDate = parsedDate.toLocaleDateString('en-US', {
      month: '2-digit',
      day: '2-digit',
      year: 'numeric'
    });
  }

  return videoData;
});

const toast = useToast();
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
      } 
      if (event === 'play') {
        console.log('playing');
        isPlaying.value = true;
      } 
      if (event === 'pause') {
        console.log('paused');
        isPlaying.value = false;
      }
      if (event === 'ended') {
        console.log('ended');
        isPlaying.value = false;
      } else  {
        console.log(event);
      }
    });
  });

    // Initial video setup
    currentIndex.value = props.currentQuery.current_pitch || 0;
    player.src({ type: 'video/mp4', src: currentVideoUrl.value });

    watch(currentIndex, (newVal) => {
      player.src({ type: 'video/mp4', src: props.videos[newVal].mp4 + '#t=0.5' });
      player.pause();
    });

    watch(() => props.reset, (newVal) => {
      if (newVal) {
        player.pause();
      }
    });

    watch(() => props.videos, (newVal) => {
      player.src({ type: 'video/mp4', src: newVal[0].mp4 + '#t=0.5' });
    });
  });
async function copyLinkToClipboard() {
      // Construct the route object with query parameters
      const route = router.resolve({
        path: '/pitch-replays',
        query: {
          date: props.currentQuery.date,
          name: encodeURIComponent(props.currentQuery.name),
          playerId: props.currentQuery.player_id,
          current_pitch: currentIndex.value, 
        }
      });

      // Generate the full URL
      const fullUrl = window.location.origin + route.href;
      console.log('Full URL:', fullUrl);
      if (navigator.clipboard) {

        try {
          // Use the Clipboard API to copy the URL
          await navigator.clipboard.writeText(fullUrl);
          console.log('Link copied to clipboard:', fullUrl);
          toast.info('Sharable link copied to clipboard!');
          // Optionally, show a notification to the user that the link has been copied
        } catch (error) {
          console.error('Failed to copy the URL:', error);
        }
      } else { // Fallback for browsers that do not support the Clipboard API
        console.error('Clipboard API not available');
      }
    }
function nextVideo() {
  if (currentIndex.value < props.videos.length - 1) {
    currentIndex.value += 1;
    isPlaying.value = false;
  }
}

function prevVideo() {
  if (currentIndex.value > 0) {
    currentIndex.value -= 1;
    isPlaying.value = false;
  }
}
</script>

<style scoped>
.video-js {
  margin-bottom: 5px;
}

.bold-outline {
  font-weight: bold;
  -webkit-text-stroke: .25px red; /* width and color of stroke */
}
</style>