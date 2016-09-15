<logs-view-user>

  <div class="mdl-color--white mdl-shadow--2dp mdl-cell mdl-cell--12-col">
    <h4 align="center">Log details for <user snowflake={ userId }></user></h4>

    <div class="mdl-tabs mdl-js-tabs mdl-js-ripple-effect">
      <div class="mdl-tabs__tab-bar">
        <a href="#logs-user-stats" class="mdl-tabs__tab is-active">Stats</a>
        <a href="#logs-user-messages" class="mdl-tabs__tab">Messages</a>
        <a href="#logs-user-words" class="mdl-tabs__tab">Words</a>
      </div>

      <div class="mdl-tabs__panel is-active" id="logs-user-stats">
        <div class="mdl-grid">
          <div class="mdl-cell mdl-cell--6-col">
            <table class="mdl-data-table mdl-js-data-table">
              <tr>
                <td class="mdl-data-table__cell--non-numeric">Raw actions</td>
                <td>{ stats.rawActionCount }</td>
              </tr>
              <tr>
                <td class="mdl-data-table__cell--non-numeric">Unique messages</td>
                <td>{ stats.uniqueMessageCount }</td>
              </tr>
              <tr>
                <td class="mdl-data-table__cell--non-numeric">Edited messages</td>
                <td>{ stats.editedMessageCount }</td>
              </tr>
              <tr>
                <td class="mdl-data-table__cell--non-numeric">Deleted messages</td>
                <td>{ stats.deletedMessageCount }</td>
              </tr>
              <tr>
                <td class="mdl-data-table__cell--non-numeric">Characters typed</td>
                <td>{ stats.characterCount }</td>
              </tr>
              <tr>
                <td class="mdl-data-table__cell--non-numeric">Words typed</td>
                <td>{ stats.wordCount }</td>
              </tr>
              <tr>
                <td class="mdl-data-table__cell--non-numeric">Average word count per message</td>
                <td>{ stats.averageWordCount.toFixed(2) }</td>
              </tr>
              <tr>
                <td class="mdl-data-table__cell--non-numeric">Average character count per message</td>
                <td>{ stats.averageMessageLength.toFixed(2) }</td>
              </tr>
              <tr>
                <td class="mdl-data-table__cell--non-numeric">First message logged</td>
                <td>{ new Date(stats.firstMessageStamp).toLocaleString() }</td>
              </tr>
              <tr>
                <td class="mdl-data-table__cell--non-numeric">Last message logged</td>
                <td>{ new Date(stats.lastMessageStamp).toLocaleString() }</td>
              </tr>
              <tr>
                <td class="mdl-data-table__cell--non-numeric">Average message count per day</td>
                <td>{ stats.averageMessagePerDay.toFixed(2) }</td>
              </tr>
              <tr>
                <td class="mdl-data-table__cell--non-numeric">Average word count per day</td>
                <td>{ stats.averageWordCountPerDay.toFixed(2) }</td>
              </tr>
              <tr>
                <td class="mdl-data-table__cell--non-numeric">Average character count per day</td>
                <td>{ stats.averageMessageLengthPerDay.toFixed(2) }</td>
              </tr>
            </table>
          </div>
          <div class="mdl-cell mdl-cell--6-col">
            <user-daily-activity-bar-chart
              if={ stats }
              data={ stats.activityPerDay }
              title="Last activity per day">
            </user-daily-activity-bar-chart>
            <user-channel-activity-bar-chart
              if={ stats }
              data={ stats.activityPerChannel }
              title="Activity per channel in the last 24h">
            </user-channel-activity-bar-chart>
          </div>
        </div>
      </div>

      <div class="mdl-tabs__panel" id="logs-user-messages">
        <div class="mdl-grid">
          <div class="mdl-cell mdl-cell--2-col"></div>
          <div class="mdl-cell mdl-cell--8-col">
            <ul class="mdl-list">
              <li each={ message in stats.lastMessages } class="mdl-list__item">
                <message data={ message } ></message>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div class="mdl-tabs__panel" id="logs-user-words">
        <div class="mdl-grid">
          <div class="mdl-cell mdl-cell--2-col"></div>
          <div class="mdl-cell mdl-cell--8-col">
            <table class="mdl-data-table mdl-js-data-table">
              <tr>
                <th>#</th>
                <th class="mdl-data-table__cell--non-numeric">word</th>
                <th class="mdl-data-table__header--sorted-descending">count</th>
              </tr>

              <tr each={ wordAndCount, i in stats.words }>
                <td>{ i + 1 }</td>
                <td class="mdl-data-table__cell--non-numeric">{ wordAndCount[0] }</td>
                <td>{ wordAndCount[1] }</td>
              </tr>
            </table>
          </div>
        </div>
      </div>

    </div>
  </div>

  <style scoped>
    table {
      width: 100%;
    }
    td, th {
      word-wrap:break-word;
      overflow-wrap:break-word;
      max-width: 300px;
    }
  </style>

  <script>
    import API from '../api.js'

    this.userId = opts.userId
    this.stats = null

    class Stats {

      constructor(data) {
        this.rawActionCount = 0
        this.uniqueMessageCount = 0
        this.editedMessageCount = 0
        this.deletedMessageCount = 0

        this.wordCount = 0
        this.characterCount = 0

        this.firstMessageStamp = data[data.length - 1].stamp * 1000
        this.lastMessageStamp = data[0].stamp * 1000

        this.wordMap = new Map
        this.words = new Array

        this.lastMessages = data.slice(0, 200)

        this.activityPerDay = new Array
        this.activityPerChannel = new Array

        this.build(data)
      }

      get averageWordCount() {
        return (this.wordCount / this.uniqueMessageCount)
      }

      get averageMessageLength() {
        return (this.characterCount / this.uniqueMessageCount)
      }

      get averageMessagePerDay() {
        return (this.uniqueMessageCount / this.daysSince)
      }

      get averageWordCountPerDay() {
        return (this.wordCount / this.daysSince)
      }

      get averageMessageLengthPerDay() {
        return (this.characterCount / this.daysSince)
      }

      get daysSince() {
        const DAYS = 1000 * 60 * 60 * 24

        return (new Date().getTime() - this.firstMessageStamp) / DAYS
      }

      build(data) {
        let uniqueMessages = new Set,
            activityMap = new Map,
            channelActivityMap = new Map,
            nowStamp = new Date().getTime() / 1000,
            channelMap = new Map,
            newPeriodActivity = () => new Object({ action: 0, unique: 0, deleted: 0 })

        let nextDay = new Date
        nextDay.setUTCHours(0, 0, 0, 0)
        let nextDayStamp = nextDay.setDate(nextDay.getDate() + 1) / 1000

        data.forEach(message => {
          let daysFrom = Math.round((nextDayStamp - message.stamp) / (24 * 3600)),
              activity = activityMap.get(daysFrom),
              channelId = (message.channel ? message.channel.id : undefined),
              channelActivity = channelActivityMap.get(channelId),
              h24FromNow = (nowStamp - message.stamp < 24 * 3600)

          if (!activity) {
            activityMap.set(daysFrom, newPeriodActivity())
            activity = activityMap.get(daysFrom)
          }
          if (!channelActivity) {
            channelActivityMap.set(channelId, newPeriodActivity())
            channelActivity = channelActivityMap.get(channelId)
          }

          channelMap.set(channelId, [message.server, message.channel])
          // Count actions and messages
          this.rawActionCount += 1
          activity.action += 1
          if (h24FromNow) channelActivity.action += 1

          if (!(uniqueMessages.has(message.id))) {
            this.uniqueMessageCount += 1
            activity.unique += 1
            if (h24FromNow) channelActivity.unique += 1
            uniqueMessages.add(message.id)
          }
          else {
            this.editedMessageCount += 1
            return
          }

          if (message.is_deleted) {
            this.deletedMessageCount += 1
            this.rawActionCount += 1
            activity.deleted += 1
            if (h24FromNow) channelActivity.deleted += 1
          }

          this.characterCount += message.content.length

          // Dissect messages
          let words = message.content.split(' ')
          words.forEach(word => {
            if (!word)
              return

            this.wordCount += 1

            word = word.toLowerCase()
            let count = this.wordMap.get(word)
            if (count == undefined)
              this.wordMap.set(word, 1)
            else
              this.wordMap.set(word, count + 1)
          })

        })

        // transform the wordMap back to an array (riotjs doesn't handle map iteration yet)
        this.wordMap.forEach((value, key) => {
          this.words.push([key, value])
        })

        this.words.sort((a, b) => b[1] - a[1])
        this.words.splice(200)

        // Build the activity per day dataset
        for (let i = 0; i < 10; ++i) {
          let activity = activityMap.get(i) || newPeriodActivity()
          this.activityPerDay.unshift(activity)
        }

        // Build the activity per channel dataset
        console.log(channelActivityMap)
        channelActivityMap.forEach((value, key) => {
          if (key && value.action > 0) {
            let [server, channel] = channelMap.get(key)
            this.activityPerChannel.push({
              server: server,
              channel: channel,
              activity: channelActivityMap.get(key)
            })
          }
        })

      }

    }

    this.on('mount', () => {
      componentHandler.upgradeElements(this.root)

      API.userLogs(this.userId).then(data => {
        this.stats = new Stats(data)
        this.update()
      })

    })

  </script>

</logs-view-user>
