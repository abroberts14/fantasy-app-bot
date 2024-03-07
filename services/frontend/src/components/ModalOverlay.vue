<template>
  <div v-if="isVisible" class="modal">
    <div class="modal-content">
      <!-- Close icon -->
      <button class="close pi pi-times text-primary-400 "  @click="closeModal"/>
      <!-- Slot for parent content -->
      <slot></slot>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import '@/assets/model_components.css'
export default {
  name: 'OverlayModal',
  props: {
    isVisible: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:isVisible'], // To allow v-model binding
  setup(props, { emit }) {
    // Method to close the modal
    const closeModal = () => {
      emit('update:isVisible', false);
    };

    return { closeModal };
  }
};
</script>
  
