<template>
    <h1>Closing window..</h1>
</template>
<script>
export default {
  mounted() {
    console.log('mounted');
    let messageSent = false;

    const sendMessage = () => {
      if (messageSent) return; // Message already sent, exit

      if (window.opener) {
        // Send a message to the opener window
        window.opener.postMessage('oauth_error', '*');
        messageSent = true; // Mark message as sent
        // Close this window
        window.close();
      } else {
        console.warn('Warning: window.opener is null, retrying in 100ms');
        // Retry after 500ms
        setTimeout(sendMessage, 100);
      }
    };

    sendMessage(); // Initial attempt to send message

    // Set timeout to close the window after 5 seconds if message not sent
    setTimeout(() => {
      if (!messageSent) {
        console.warn('Warning: Message not sent within 5 seconds, closing window');
        window.close();
      }
    }, 5000);
  }
}
</script>