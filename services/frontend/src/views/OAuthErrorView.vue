<template>
    <h1>Closing window..</h1>
</template>
<script>
export default {
  mounted() {
    if (window.opener) {
      // Send a message to the opener window
      window.opener.postMessage('oauth_error', '*');
      // Close this window
      window.close();
    } else {
      console.error('Error: window.opener is null');
      // Handle the case where window.opener is null
    }
  }
}
</script>