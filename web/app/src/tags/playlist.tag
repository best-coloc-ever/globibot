<playlist>

  <h5 align="center" if={ queue.length == 0 }>Nothing is being played at the moment</h5>

  <div class="mdl-snackbar mdl-js-snackbar" name="snackbar">
    <div class="mdl-snackbar__text"></div>
    <button class="mdl-snackbar__action" show={ false }></button>
  </div>

  <ul class="mdl-list">
    <li each={ item in queue } class="mdl-list__item list-item">
      <span class="mdl-list__item-primary-content">
        <img src={ item.user.avatar_url }>{ itemTitle(item) }
      </span>
      <span class="mdl-list__item-secondary-action">
        <!-- <button
          class="mdl-button mdl-button--colored mdl-js-button mdl-js-ripple-effect"
          onclick={ joinChannel(voice.server.id, channel.id) }>
          Join
        </button> -->
      </span>
    </li>
  </ul>

  <style scoped>
    img {
      width: 28px;
      height: 28px;
      margin-right: 10px;
    }

    .list-item {
      -webkit-box-shadow: 2px 3px 5px 0px rgba(0,0,0,0.75);
      -moz-box-shadow: 2px 3px 5px 0px rgba(0,0,0,0.75);
      box-shadow: 2px 3px 5px 0px rgba(0,0,0,0.75);
      margin-top: 5px;
    }
  </style>

  <script>
    this.queue = []

    this.on('mount', () => {
      console.log(`playlist ${opts.snowflake} mounted`)
    })

    this.parent.on(`on-voice-data-${opts.snowflake}`, data => {
      let action = this.actions[data.type]
      if (action)
        action(data)
      else
        console.warn(`unknown action type: ${data.type}`)
    })

    this.onQueueData = data => {
      this.queue = data.items
      this.update()
    }

    this.onQueue = data => {
      this.queue.push(data.item)
      console.log(data.item)
      this.update()
    }

    this.onNext = data => {
      if (this.queue.length > 1)
        this.queue.splice(0, 1)
      this.update()
    }

    this.onError = data => {
      // console.error(data)
      let snackbar = this['snackbar']
      let snackData = {
        message: `while queuing ${data.resource}: ${data.error}`,
        timeout: 5000
      }
      snackbar.MaterialSnackbar.showSnackbar(snackData)
    }

    this.actions = {
      queue_data: this.onQueueData,
      queue: this.onQueue,
      next: this.onNext,
      error: this.onError
    }

    this.itemTitle = item => {
      if (item.tts)
        return 'Text to Speech'
      else {
        let entry = item
        if (item.entries && item.entries.length >= 1)
          entry = item.entries[0]

        return `${entry.extractor_key}   ${entry.title}`
      }
    }
  </script>

</playlist>
