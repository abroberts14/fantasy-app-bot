<template>
  <h1>Closing window..</h1>
  <p>Please wait..</p>
</template>

<script>
export default {
  mounted() {
    console.log('mounted');
    let messageSent = false;

    const sendMessage = () => {
      if (messageSent) return; // Message already sent, exit

      // Create a new Broadcast Channel
      const channel = new BroadcastChannel('oauth_channel');

      // Send a message to the channel
      channel.postMessage('oauth_success');
      messageSent = true; // Mark message as sent

      // Close this window
      window.close();
    };

    // Try to send the message immediately
    sendMessage();

    // If the message wasn't sent, try again after 300ms
    if (!messageSent) {
      setTimeout(sendMessage, 500);
    }
  },
};
</script>