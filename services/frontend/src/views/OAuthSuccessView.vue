<script>
export default {
  mounted() {
    console.log('mounted');
    let messageSent = false;
    document.cookie = 'oauth_success=true; path=/';

    const sendMessage = () => {
      if (messageSent) return; // Message already sent, exit

      if (window.opener) {
        // Send a message to the opener window
        window.opener.postMessage('oauth_success', '*');
        messageSent = true; // Mark message as sent
        // Close this window
        window.close();
      } else {
        const channel = new BroadcastChannel('oauth_channel');
        channel.postMessage('oauth_success');

        console.warn('Warning: window.opener is null, using broadcast channel');
        //window close
      }
    };

    sendMessage(); // Initial attempt to send message

   
  }
}
</script>