import { defineStore } from 'pinia';

const useLoadingStore = defineStore('loading', {
  state: () => ({
    isLoading: false,
  }),
  actions: {
    showLoading() {
      // Clear any existing timeout to avoid multiple spinners
      if (this.timeoutId) {
        clearTimeout(this.timeoutId);
      }

      // Set a timeout to change the loading state
      this.timeoutId = setTimeout(() => {
        this.isLoading = true;
      }, 7500); // Adjust the delay as needed
    },
    hideLoading() {
      // Clear the timeout and reset the loading state
      if (this.timeoutId) {
        clearTimeout(this.timeoutId);
      }
      this.isLoading = false;
    }
    },

});

export default useLoadingStore;