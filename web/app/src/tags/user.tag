<user>

  <span> { name } <img src={ avatarUurl } if={ avatarUurl }></span>

  <style scoped>
    img {
      max-width: 32px;
      max-height: 32px;
    }
  </style>

  <script>
    var self = this;
    this.name = '# ' + opts.snowflake;
    this.avatarUurl = null

    this.fetchUser = () => {
      if (opts.snowflake) {

        fetch('/bot/api/user/' + opts.snowflake, { credentials: 'same-origin'})
          .then(r => r.json())
          .then(data => {
            self.name = data.name
            self.avatarUurl = data.avatar_url
            self.update()
          })
      }
    }

    this.on('mount', this.fetchUser)
  </script>

</user>
