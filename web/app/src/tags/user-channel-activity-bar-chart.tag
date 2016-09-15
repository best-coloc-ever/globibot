<user-channel-activity-bar-chart>

  <div>
    <canvas name="chart" height="200"></canvas>
  </div>

  <style scoped>
  </style>

  <script>
    this.on('mount', () => {
      setTimeout(this.buildChart, 0) // Dom readyness...
    })

    this.buildChart = () => {
      let data = opts.data

      let labels = data.map(d => d.channel.name)

      new Chart(this.chart, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Unique messages',
              data: data.map(d => d.activity.unique),
              backgroundColor: 'rgba(148, 189, 234, 0.5)',
              borderWidth: 0
            },
            {
              label: 'Edited messages',
              data: data.map(d => d.activity.action - d.activity.unique),
              backgroundColor: 'rgba(54, 114, 181, 0.5)',
              borderWidth: 0
            },
            {
              label: 'Deleted messages',
              data: data.map(d => d.activity.deleted),
              backgroundColor: 'rgba(130, 82, 78, 0.5)',
              borderColor: 'grey',
              borderWidth: 0
            }
          ]
        },
        options: {
          title: {
            display: opts.title,
            text: opts.title
          },
          scales: {
            yAxes: [{
              ticks: {
                beginAtZero:true
              },
              stacked: true
            }],
            xAxes: [{
              stacked: true
            }]
          },
        }
      })
    }
  </script>

</user-channel-activity-bar-chart>
