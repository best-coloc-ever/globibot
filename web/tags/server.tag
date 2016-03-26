<server>

  <h2>{ name } ({ id })</h2>

  <div class="container">
    <channel each={ channel in channels } data={ channel } class="channel"></channel>
  </div>

  <script>
    var self = this;

    this.name = opts.data.name;
    this.id = opts.data.id;

    onMessage(message) {
      for (var channel of this.tags.channel) {
        if (channel.id == message.channel.id) {
          channel.onMessage(message)
        }
      }
    }

    $.ajax({
      url: '/bot/servers/' + this.id,
      success: function(data) {
        self.channels = data;
        self.update();
      }
    })
  </script>

  <style>
    .container{
      display: flex;
    }

    .channel {
      min-width: 300px;
    }
  </style>

</server>
