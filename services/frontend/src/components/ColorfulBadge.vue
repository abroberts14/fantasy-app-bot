<template>
  <Badge :value="value" :style="{ backgroundColor: badgeBackgroundColor }"></Badge>
</template>

<script>
import { computed, ref } from 'vue';

export default {
  props: {
    value: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    const badgeCustom = ref({
      colorScheme: {
        light: {
          root: {
            primaryBackground: '{amber.500}',
          },
        },
        dark: {
          root: {
            primaryBackground: '{amber.500}',
          },
        }
      }
    });

    const badgeBackgroundColor = computed(() => {
      const value = props.value;
      if (value < 5) return 'var(--p-blue-950)';
      else if (value < 10) return 'var(--p-blue-900)';
      else if (value < 15) return 'var(--p-blue-800)';
      else if (value < 20) return 'var(--p-blue-700)';
      else if (value < 25) return 'var(--p-blue-600)';
      else if (value < 30) return 'var(--p-blue-500)';
      else if (value < 35) return 'var(--p-blue-400)';
      else if (value < 40) return 'var(--p-blue-300)';
      else if (value < 45) return 'var(--p-blue-300)';
      else if (value < 50) return 'var(--p-blue-200)';
      else if (value < 52) return 'var(--p-red-100)';
      else if (value < 54) return 'var(--p-red-100)';
      else if (value < 56) return 'var(--p-red-200)';
      else if (value < 58) return 'var(--p-red-300)';
      else if (value < 60) return 'var(--p-red-400)';
      else if (value < 65) return 'var(--p-red-500)';
      else if (value < 70) return 'var(--p-red-600)';
      else if (value < 75) return 'var(--p-red-700)';
      else if (value < 80) return 'var(--p-red-800)';
      else if (value < 85) return 'var(--p-red-800)';
      else return 'var(--p-red-900)';
    });

    return { badgeBackgroundColor, badgeCustom };
  }
};
</script>

<style scoped>
/* No changes needed in the style section */
</style>