<script lang="ts">
  export let values: number[] = [10, 18, 15, 24, 20, 32, 28];
  const width = 320;
  const height = 120;

  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);
  const range = max - min || 1;

  const points = values
    .map((value, index) => {
      const x = (index / (values.length - 1)) * width;
      const y = height - ((value - min) / range) * height;
      return `${x},${y}`;
    })
    .join(' ');
</script>

<svg viewBox={`0 0 ${width} ${height}`} aria-label="Portfolio trend">
  <defs>
    <linearGradient id="chart-gradient" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#f05d38" />
      <stop offset="100%" stop-color="#2d6cdf" />
    </linearGradient>
  </defs>
  <polyline
    fill="none"
    stroke="url(#chart-gradient)"
    stroke-width="4"
    stroke-linecap="round"
    stroke-linejoin="round"
    points={points}
  />
</svg>

<style>
  svg {
    width: 100%;
    height: auto;
  }
</style>
