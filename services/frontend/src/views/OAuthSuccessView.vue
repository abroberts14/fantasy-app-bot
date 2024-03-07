<script>
export default {
  mounted() {
    console.log('mounted');
    let messageSent = false;

    const sendMessage = () => {
      if (messageSent) return; // Message already sent, exit

      if (window.opener) {
        // Send a message to the opener window
        window.opener.postMessage('oauth_success', '*');
        messageSent = true; // Mark message as sent
        // Close this window
        window.close();
      } 
    };

    sendMessage(); // Initial attempt to send message

   
  }
}
</script>
