<template>
    <h1>Closing window..</h1>
    <p>Please wait..</p>
</template>
<script>
export default {
  mounted() {
    console.log('mounted');
    if (window.opener) {
      // Send a message to the opener window
      window.opener.postMessage('oauth_success', '*');
      // Close this window
      window.close();
    } else {
      console.error('Error: window.opener is null');
      // Handle the case where window.opener is null
    }
  }
}
</script>