<template>
  <div class="progress-panel">
    <div v-for="(value, key) in percentiles" :key="key" >
      <div v-if="isValidValue(value)" class="percentile-container">
          <strong>{{ getFriendlyKey(key) }}:</strong>
          <ProgressBar :value="value" :class="getClass(value)"></ProgressBar>
      </div>
    </div>
  </div>
</template>

<script>

export default {

  props: {
    percentiles: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      keyMap: {
        xwoba: 'xwOBA',
        xba: 'xBA',
        xslg: 'xSLG',
        xiso: 'xISO',
        xobp: 'xOBP ',
        brl: 'Barrel',
        brl_percent: 'Barrel %',
        exit_velocity: 'Avg EV',
        max_ev: 'Max EV',
        hard_hit_percent: 'HH %',
        k_percent: 'K %',
        bb_percent: 'BB %',
        whiff_percent: 'Whiff %',
        chase_percent: 'Chase %',
        arm_strength: 'Arm Strength',
        sprint_speed: 'Sprint Speed',
        oaa: 'OAA',
        bat_speed: 'Bat Speed',
        swing_length: 'Swing Length'
      }
    };
  },


  methods: {
    getClass(value) {
        if (value < 10) return 'darker-blue';
        else if (value < 20) return 'dark-blue';
        else if (value < 30) return 'mid-dark-blue';
        else if (value < 40) return 'light-blue';
        else if (value < 50) return 'very-light-blue';
        else if (value < 55) return 'light-red';
        else if (value < 60) return 'less-light-red';
        else if (value < 70) return 'mid-red';
        else if (value < 80) return 'red';
        else if (value < 90) return 'dark-red';
        else return 'darker-red';
        },
    progressBarStyle(value) {
        const red = Math.round((255 * value) / 100);
        const blue = 255 - red;
        return {
            'background-color': `rgb(${red}, 0, ${blue}) !important`, // Computed color for filled part
            'border-radius': '5px',
            'height': '20px'
        };
    },
    getFriendlyKey(key) {
      return this.keyMap[key] || key;
    },
    isValidValue(value) {
      return value !== null && value !== undefined && value >= 0 && value <= 100;
    }
  }
}
</script>

<style scoped>

.percentile-container {
  margin: 5px 0;
  display: flex;
  align-items: center;
  min-width: 100px;
  position: relative; /* Essential for positioning the label absolutely */
}

.percentile-container strong {
  min-width: 100px; /* Ensure labels have enough space */
  font-size: 0.85em; /* Smaller font size for compactness */
  position: relative; /* For proper stacking context of the label */

}
</style>

