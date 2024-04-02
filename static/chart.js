document.addEventListener('DOMContentLoaded', function() {

    function drawChart(chartType) {
      fetch('data.json')
        .then(response => response.json())
        .then(data => {
          console.log("Data from JSON file:", data);
  
          let myChart = Chart.getChart('chart');
          if (myChart) {
            myChart.destroy();
          }
  
        let dataset;
  
        // Determine which dataset to use based on the button clicked
        switch (chartType) {
          case "location":
            dataset = data.location;
            break;
          case "season":
            dataset = data.season;
            break;
          case "specialty":
            dataset = data.specialty;
            break;
          case "shift":
            dataset = data.shift;
            break;
          case "contract-length":
            dataset = data.contract_length;
            break;
          default:
            dataset = data.location;
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
                  color: 'rgba(0, 0, 0, 0.7)',
                  callback: function(value, index, values) {
                    return '$' + value;
                  },
                },
                grid: {
                  color: 'rgba(0, 0, 0, 0.1)',
                },
              },
            },
          },
        });
  
  
        });
    }
  
  
    // Add event listeners to the buttons
    document.querySelectorAll(".button-container button").forEach((button) => {
      button.addEventListener("click", () => {
        drawChart(button.getAttribute("data-chart-type"));
      });
    });
  
    // Initial chart
    drawChart("location");
  
  });