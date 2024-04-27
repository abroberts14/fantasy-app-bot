<template>

  <div class="video-container" style="position: relative;">

        <video ref="videoPlayer" @ended="playNextVideo"  controls>
            <source :src="currentVideo" type="video/mp4">
        </video>

        <div class="overlay-text" style="position: absolute;  top: 2%; left: 2%; color: white; font-size: 20px; font-weight: bolder; text-shadow: 2px 2px 4px #000000; background-color: rgba(0, 0, 0, 0.8); padding: 10px; border-radius: 5px;">
          <span v-if="currentVideoStats.batter_name" class="underline">
          {{ currentVideoStats.batter_name }} 
          </span><br v-if="currentVideoStats.hit_speed">
          <span v-if="videos.length">
            Video: {{ currentVideoIndex + 1}}/{{ videos.length }} 
          </span><br v-if="videos.length">
          <span v-if="currentVideoStats.pitch_name || currentVideoStats.start_speed">
            Pitch: {{ currentVideoStats.pitch_name }} {{ currentVideoStats.start_speed }} MPH
          </span><br v-if="currentVideoStats.pitch_name || currentVideoStats.start_speed">
          
          <span v-if="currentVideoStats.hit_speed">
            EV: {{ currentVideoStats.hit_speed }} mph
          </span><br v-if="currentVideoStats.hit_speed">
          
          <span v-if="currentVideoStats.hit_distance">
            Distance: {{ currentVideoStats.hit_distance }} ft
          </span><br v-if="currentVideoStats.hit_distance">
          
          <span v-if="currentVideoStats.xba">
            Expected BA: {{ currentVideoStats.xba }}
          </span><br v-if="currentVideoStats.xba">
          
          <span v-if="currentVideoStats.hit_angle !== undefined">
            Launch Angle: {{ currentVideoStats.hit_angle }}°
          </span><br v-if="currentVideoStats.hit_angle !== undefined">
          
          <span v-if="currentVideoStats.is_barrel !== undefined">
            Barrel: {{ currentVideoStats.is_barrel ? 'Yes' : 'No' }}
          </span><br v-if="currentVideoStats.is_barrel !== undefined">

          <span v-if="currentVideoStats.hr_cat !== undefined" style="color: red;">
            Home Run: {{ currentVideoStats.hr_cat }}
          </span><br v-if="currentVideoStats.hr_cat !== undefined">
          
          <span v-if="currentVideoStats.hr_ct !== undefined" style="color: red;">
            Home Run Parks: {{ currentVideoStats.hr_ct }} / 30
          </span><br v-if="currentVideoStats.hr_ct !== undefined">
        </div>
      <div class="">
        <Button @click="playPreviousVideo" :disabled="currentVideoIndex === 0" style="margin-right: 10px;">Previous Video</Button>
        <Button @click="playNextVideo" :disabled="currentVideoIndex === videos.length - 1" style="margin-right: 10px;">Next Video</Button>
        <Dropdown v-model="playbackSpeed" :options="playbackOptions" optionLabel="label" optionValue="value" @change="changePlaybackSpeed" style="width: 100px;" />
      </div>
    </div>
  </template>
  
  <script>
  
  export default {

    props: ['videos'],
    data() {
      return {
        currentVideoIndex: 0,
        playbackSpeed: 1,
        playbackOptions: [
          { label: '1x', value: 1 },
          { label: '1.25x', value: 1.25 },
          { label: '1.5x', value: 1.5 },
          { label: '2x', value: 2 },
        ],
        
      };
    },
    computed: {
      currentVideo() {
        return this.videos[this.currentVideoIndex].mp4;
      },
      currentVideoStats(){
        return this.videos[this.currentVideoIndex];
      }
    },
    mounted() {
      this.$refs.videoPlayer.play();

    },
    props: ['videos', 'resetPlayer'],
    watch: {
      resetPlayer(newVal) {
        console.log("resetPlayer changed to", newVal);
        if (newVal === true) {
          this.handleResetVideoPlayer();
        }
      },
     
    },
    methods: {
        playPreviousVideo() {
            if (this.currentVideoIndex > 0) {
                this.currentVideoIndex--;
                this.$refs.videoPlayer.src = this.currentVideo;

                this.$refs.videoPlayer.play();
                this.$refs.videoPlayer.playbackRate = this.playbackSpeed;

            }
        },
        playNextVideo() {
            if (this.currentVideoIndex < this.videos.length - 1) {
                this.currentVideoIndex++;
                this.$refs.videoPlayer.src = this.currentVideo;

                this.$refs.videoPlayer.play();
                this.$refs.videoPlayer.playbackRate = this.playbackSpeed;
                this.preloadNextVideo()
            }
        },
        changePlaybackSpeed() {
            this.$refs.videoPlayer.playbackRate = this.playbackSpeed;
        },

        preloadNextVideo() {
            if (this.currentVideoIndex < this.videos.length - 1) {
                let nextVideoElement = document.createElement('video');
                nextVideoElement.src = this.videos[this.currentVideoIndex + 1];
                nextVideoElement.preload = 'auto';
            }
        },
        handleResetVideoPlayer() {
            this.$refs.videoPlayer.pause();
            console.log("currentVideoIndex: ", this.currentVideoIndex);

            this.$refs.videoPlayer.currentTime = 0;
            this.$refs.videoPlayer.playbackRate = 1;
            this.playbackSpeed = 1;
            this.currentVideoIndex = 0;
            this.$refs.videoPlayer.src = this.currentVideo;
            console.log("Resetting video player...");
            console.log("currentVideoIndex: ", this.currentVideoIndex);
            //this.$refs.videoPlayer.play();
            // Reset all other values here...
        },

    },
  };
  </script>