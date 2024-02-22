<template>
    <div class="spinner-overlay">
      <ProgressSpinner />
    </div>
  </template>
  
  <script>
  import ProgressSpinner from 'primevue/progressspinner';
  
  import { defineComponent } from 'vue';
  export default defineComponent({
    name: 'LoadingSpinner',
    components: {
      ProgressSpinner
    }
  });
  </script>
  
  <style scoped>
  .spinner-overlay {
    display: flex;
    justify-content: center;
    align-items: center;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(255, 255, 255, 0.829); /* Very semi-transparent off-white */
    z-index: 9999;
   
  }
  </style>

<!-- /* position: fixed;
top: 0;
left: 0;
width: 100%;
height: 100%;
display: flex;
justify-content: center;
align-items: center;
background-color: rgba(255, 255, 255, 0.8); 
z-index: 9999;  */ -->