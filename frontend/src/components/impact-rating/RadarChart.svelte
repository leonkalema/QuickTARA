<script>
  import { onMount } from 'svelte';
  import Chart from 'chart.js/auto';
  
  export let data = {
    labels: ['Safety', 'Financial', 'Operational', 'Privacy'],
    values: [0, 0, 0, 0]
  };
  
  let canvas;
  let chart;
  
  onMount(() => {
    createChart();
    return () => {
      if (chart) chart.destroy();
    };
  });
  
  $: if (chart && data) {
    updateChart();
  }
  
  function createChart() {
    const ctx = canvas.getContext('2d');
    
    chart = new Chart(ctx, {
      type: 'radar',
      data: {
        labels: data.labels,
        datasets: [{
          label: 'Impact Ratings',
          data: data.values,
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 2,
          pointBackgroundColor: 'rgba(54, 162, 235, 1)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
        }]
      },
      options: {
        scales: {
          r: {
            angleLines: {
              display: true
            },
            suggestedMin: 0,
            suggestedMax: 4,
            ticks: {
              stepSize: 1,
              callback: function(value) {
                if (value === 0) return 'None';
                if (value === 1) return 'Low';
                if (value === 2) return 'Medium';
                if (value === 3) return 'High';
                if (value === 4) return 'Critical';
                return '';
              }
            }
          }
        },
        plugins: {
          legend: {
            display: false
          }
        }
      }
    });
  }
  
  function updateChart() {
    chart.data.labels = data.labels;
    chart.data.datasets[0].data = data.values;
    chart.update();
  }
</script>

<div class="radar-chart-container">
  <canvas bind:this={canvas}></canvas>
</div>

<style>
  .radar-chart-container {
    width: 100%;
    height: 300px;
    position: relative;
  }
</style>
