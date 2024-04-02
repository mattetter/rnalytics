function drawChart(chartType) {
    fetch('/chart_data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ chartType: chartType })
    })
    .then(response => response.json())
    .then(data => {
      console.log("Data from database:", data);
  
      let myChart = Chart.getChart('chart');
      if (myChart) {
        myChart.destroy();
      }
  
      let dataset;
  
      // Determine which dataset to use based on the button clicked
      switch (chartType) {
        case "location":
          dataset = { 
            label: "Pay rate by location",
            data: data.map(row => row[6]), 
            labels: data.map(row => row[5]), 
            backgroundColor: "rgba(255, 99, 132, 0.2)" 
          };
          break;
        case "season":
          // TODO: add implementation for season chart
          break;
        case "specialty":
          // TODO: add implementation for specialty chart
          break;
        case "shift":
          // TODO: add implementation for shift chart
          break;
        case "contract-length":
          // TODO: add implementation for contract-length chart
          break;
        default:
          dataset = { 
            label: "Pay rate by location",
            data: data.map(row => row[6]), 
            labels: data.map(row => row[5]), 
            backgroundColor: "rgba(255, 99, 132, 0.2)" 
          };
      }
  
      const ctx = document.getElementById("chart").getContext("2d");
  
      myChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: dataset.labels,
          datasets: [
            {
              label: dataset.label,
              data: dataset.data,
              backgroundColor: dataset.backgroundColor,
              borderColor: 'rgba(255, 99, 132, 1)',
              borderWidth: 2,
              pointRadius: 3,
              pointBackgroundColor: 'rgba(255, 99, 132, 1)',
              pointBorderColor: 'rgba(255, 99, 132, 1)',
              pointHoverRadius: 6,
              pointHoverBackgroundColor: 'rgba(255, 99, 132, 1)',
              pointHoverBorderColor: 'rgba(255, 99, 132, 1)',
              pointHitRadius: 10,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false,
            },
            tooltip: {
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              titleFont: {
                size: 16,
                weight: 'bold',
              },
              bodyFont: {
                size: 14,
              },
              displayColors: true,
            },
          },
          scales: {
            x: {
              ticks: {
                font: {
                  size: 14,
                },
                color: 'rgba(0, 0, 0, 0.7)',
              },
              grid: {
                display: false,
              },
            },
            y: {
              ticks: {
                font: {
                  size: 14,
                },
  