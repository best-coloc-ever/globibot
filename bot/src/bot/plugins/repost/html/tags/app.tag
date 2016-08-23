<app>

  <h2>Reposts on # { serverId }</h2>
  Test your link here: <input id="input" onKeyUp={ checkLink }></input>
  <br>
  <br>
  <br>
  <div if={ result != null }>
    <div if={ result }>
      Your link has already been posted by <user name="user" snowflake={ result[0] }></user> on { new Date(result[1] * 1000) }
    </div>

    <div if={ !result }>
      Your link has never been posted on this server!
    </div>
  </div>

  <script>
    this.serverId = riot.route.query().id;
    this.data = null;
    this.result = null;

    $.get({
      url: '/repost/api/' + this.serverId,
      success: function(data) {
        self.data = data;
      }
    });

    checkLink() {
      var link = $('#input').val();
      if (link in self.data) {
        this.result = self.data[link];
        this.tags.user.fetchUser();
      }
      else
        this.result = false;

      this.update();
    }
  </script>

</app>
