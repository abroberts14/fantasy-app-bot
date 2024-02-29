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

    if (window.opener) {
      // Send a message to the opener window
      window.opener.postMessage('oauth_error', '*');
      messageSent = true; // Mark message as sent
      // Close this window
      window.close();
    } else if (window.parent) {
      // Send a message to the parent window
      window.parent.postMessage('oauth_error', '*');
      messageSent = true; // Mark message as sent
      // Close this window
      window.close();

    } else {
      console.warn('Warning: window.opener and parent is null, retrying in 100ms');
      // Retry after 500ms
      setTimeout(sendMessage, 300);
    }
  };

  sendMessage(); // Initial attempt to send message

  // Set timeout to close the window after 5 seconds if message not sent
  setTimeout(() => {
    if (!messageSent) {
      console.warn('Warning: Message not sent within 5 seconds, closing window');
      //window.close();
    }
  }, 5000);
}
}
</script>