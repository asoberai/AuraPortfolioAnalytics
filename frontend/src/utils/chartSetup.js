import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  RadialLinearScale
} from 'chart.js';

// Register all Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement, // This was missing - needed for Doughnut/Pie charts
  Title,
  Tooltip,
  Legend,
  Filler,
  RadialLinearScale // Needed for Radar charts
);

// Robinhood-style color palette
export const ROBINHOOD_COLORS = {
  primary: '#00D09C', // Robinhood green
  primaryDark: '#00B389',
  primaryLight: '#1AE5B5',
  danger: '#FF6B6B', // Red for losses
  warning: '#FFD93D', // Yellow for warnings
  neutral: '#9B9B9B', // Gray for neutral
  background: '#0D1421', // Dark background
  surface: '#1B2232', // Card background
  text: '#FFFFFF',
  textSecondary: '#9B9B9B',
  black: '#000000'
};

// Chart default options with Robinhood styling
export const getChartOptions = (title) => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      labels: {
        color: ROBINHOOD_COLORS.text,
        font: {
          family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
          size: 12,
          weight: '500'
        },
        usePointStyle: true,
        padding: 20
      }
    },
    tooltip: {
      backgroundColor: ROBINHOOD_COLORS.surface,
      titleColor: ROBINHOOD_COLORS.text,
      bodyColor: ROBINHOOD_COLORS.text,
      borderColor: ROBINHOOD_COLORS.primary,
      borderWidth: 1,
      cornerRadius: 8,
      titleFont: {
        family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
        size: 14,
        weight: '600'
      },
      bodyFont: {
        family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
        size: 13
      }
    },
    title: title ? {
      display: true,
      text: title,
      color: ROBINHOOD_COLORS.text,
      font: {
        family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
        size: 16,
        weight: '600'
      },
      padding: 20
    } : { display: false }
  },
  scales: {
    x: {
      ticks: {
        color: ROBINHOOD_COLORS.textSecondary,
        font: {
          family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
          size: 11
        }
      },
      grid: {
        color: 'rgba(155, 155, 155, 0.1)',
        borderColor: 'rgba(155, 155, 155, 0.2)'
      }
    },
    y: {
      ticks: {
        color: ROBINHOOD_COLORS.textSecondary,
        font: {
          family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
          size: 11
        }
      },
      grid: {
        color: 'rgba(155, 155, 155, 0.1)',
        borderColor: 'rgba(155, 155, 155, 0.2)'
      }
    }
  }
});

// Specific options for doughnut/pie charts
export const getDoughnutOptions = (title) => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right',
      labels: {
        color: ROBINHOOD_COLORS.text,
        font: {
          family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
          size: 12,
          weight: '500'
        },
        usePointStyle: true,
        padding: 15,
        generateLabels: function(chart) {
          const data = chart.data;
          if (data.labels.length && data.datasets.length) {
            return data.labels.map((label, i) => {
              const dataset = data.datasets[0];
              const value = dataset.data[i];
              const total = dataset.data.reduce((a, b) => a + b, 0);
              const percentage = ((value / total) * 100).toFixed(1);
              
              return {
                text: `${label} (${percentage}%)`,
                fillStyle: dataset.backgroundColor[i],
                strokeStyle: dataset.backgroundColor[i],
                lineWidth: 0,
                index: i
              };
            });
          }
          return [];
        }
      }
    },
    tooltip: {
      backgroundColor: ROBINHOOD_COLORS.surface,
      titleColor: ROBINHOOD_COLORS.text,
      bodyColor: ROBINHOOD_COLORS.text,
      borderColor: ROBINHOOD_COLORS.primary,
      borderWidth: 1,
      cornerRadius: 8,
      callbacks: {
        label: function(context) {
          const label = context.label || '';
          const value = context.parsed;
          const total = context.dataset.data.reduce((a, b) => a + b, 0);
          const percentage = ((value / total) * 100).toFixed(1);
          return `${label}: ${percentage}%`;
        }
      }
    },
    title: title ? {
      display: true,
      text: title,
      color: ROBINHOOD_COLORS.text,
      font: {
        family: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
        size: 16,
        weight: '600'
      },
      padding: 20
    } : { display: false }
  }
});

export default ChartJS;