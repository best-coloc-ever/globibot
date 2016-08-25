<user>

  <span> { name } (# { opts.snowflake }) </span>

  <script>
    var self = this;
    this.name = '# ' + opts.snowflake;

    fetchUser() {
      if (opts.snowflake)
        $.get({
          url: '/user/' + opts.snowflake,
          success: function(data) {
            self.name = data.username;
            self.update();
          }
        });
    }

    this.on('mount', self.fetchUser)
  </script>

</user>
