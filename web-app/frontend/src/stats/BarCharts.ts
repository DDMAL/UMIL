import * as d3 from 'd3';

interface ChartData {
  name: string;
  count: number;
}

class BarCharts {
  private readonly margin = { top: 20, right: 100, bottom: 20, left: 100 };
  private readonly animationDuration = 800;
  private readonly animationDelay = 100;
  private readonly color = '#876445';

  constructor() {
    this.init();
  }

  private init(): void {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.createCharts());
    } else {
      this.createCharts();
    }
  }

  private createCharts(): void {
    // Get data from Django template
    const instrumentsDataElement = document.getElementById(
      'instruments-chart-data',
    );
    const languagesDataElement = document.getElementById(
      'languages-chart-data',
    );

    if (!instrumentsDataElement || !languagesDataElement) {
      console.error('Chart data elements not found');
      return;
    }

    try {
      const instrumentsData: ChartData[] = JSON.parse(
        instrumentsDataElement.textContent || '[]',
      );
      const languagesData: ChartData[] = JSON.parse(
        languagesDataElement.textContent || '[]',
      );

      this.createInstrumentsChart(instrumentsData);
      this.createLanguagesChart(languagesData);
      this.setupIntersectionObserver();
    } catch (error) {
      console.error('Error parsing chart data:', error);
    }
  }

  private getContainerDimensions(containerId: string): {
    width: number;
    height: number;
  } {
    const container = document.getElementById(containerId.replace('#', ''));
    if (!container) {
      // Fallback dimensions if container not found
      return { width: 400, height: 300 };
    }

    const rect = container.getBoundingClientRect();
    // Use container dimensions with minimum sizes to ensure charts are visible
    const width = Math.max(rect.width || 400, 300);
    const height = Math.max(rect.height || 300, 200);

    return { width, height };
  }

  private createInstrumentsChart(data: ChartData[]): void {
    const container = d3.select('#instruments-chart');
    if (container.empty()) return;

    // Get dynamic dimensions
    const { width: chartWidth, height: chartHeight } =
      this.getContainerDimensions('#instruments-chart');
    const innerWidth = chartWidth - this.margin.left - this.margin.right;
    const innerHeight = chartHeight - this.margin.top - this.margin.bottom;

    // Clear any existing content
    container.selectAll('*').remove();

    // Create SVG
    const svg = container
      .append('svg')
      .attr('width', chartWidth)
      .attr('height', chartHeight);

    const g = svg
      .append('g')
      .attr(
        'transform',
        `translate(${this.margin.left + 20},${this.margin.top})`,
      );

    // Create scales (swapped for horizontal bars)
    const xScale = d3
      .scaleLinear()
      .domain([0, d3.max(data, (d: ChartData) => d.count) || 0])
      .range([0, innerWidth]);

    const yScale = d3
      .scaleBand()
      .domain(data.map((d: ChartData) => d.name))
      .range([0, innerHeight])
      .padding(0.2);

    // Create bars (horizontal) - start with width 0 for animation
    const bars = g
      .selectAll('.bar')
      .data(data)
      .enter()
      .append('rect')
      .attr('class', 'bar')
      .attr('x', 0)
      .attr('y', (d: ChartData) => yScale(d.name) || 0)
      .attr('width', 0) // Start with width 0
      .attr('height', yScale.bandwidth())
      .attr('rx', 4) // Horizontal border radius
      .attr('ry', 4) // Vertical border radius
      .attr('fill', this.color)
      .attr('opacity', 0.8);

    // Store final widths for animation
    bars.each(function (this: SVGRectElement, d: ChartData) {
      d3.select(this).attr('data-final-width', xScale(d.count));
    });

    // Add instrument name labels on the left
    g.selectAll('.name-label')
      .data(data)
      .enter()
      .append('text')
      .attr('class', 'name-label')
      .attr('x', -10)
      .attr(
        'y',
        (d: ChartData) => (yScale(d.name) || 0) + yScale.bandwidth() / 2,
      )
      .attr('text-anchor', 'end')
      .attr('dominant-baseline', 'middle')
      .style('text-transform', 'capitalize')
      .style('font-size', '16px')
      .style('font-weight', '700')
      .style('fill', this.color)
      .text((d: ChartData) => d.name);

    // Add value labels on bars (start hidden)
    g.selectAll('.value-label')
      .data(data)
      .enter()
      .append('text')
      .attr('class', 'value-label')
      .attr('x', (d: ChartData) => xScale(d.count) + 5)
      .attr(
        'y',
        (d: ChartData) => (yScale(d.name) || 0) + yScale.bandwidth() / 2,
      )
      .attr('text-anchor', 'start')
      .attr('dominant-baseline', 'middle')
      .style('font-size', '14px')
      .style('font-weight', 'bold')
      .style('fill', this.color)
      .style('opacity', 0) // Start hidden
      .text((d: ChartData) => d.count);
  }

  private createLanguagesChart(data: ChartData[]): void {
    const container = d3.select('#languages-chart');
    if (container.empty()) return;

    // Get dynamic dimensions
    const { width: chartWidth, height: chartHeight } =
      this.getContainerDimensions('#languages-chart');
    const innerWidth = chartWidth - this.margin.left - this.margin.right;
    const innerHeight = chartHeight - this.margin.top - this.margin.bottom;

    // Clear any existing content
    container.selectAll('*').remove();

    // Create SVG
    const svg = container
      .append('svg')
      .attr('width', chartWidth)
      .attr('height', chartHeight);

    const g = svg
      .append('g')
      .attr('transform', `translate(${this.margin.left},${this.margin.top})`);

    // Create scales (swapped for horizontal bars)
    const xScale = d3
      .scaleLinear()
      .domain([0, d3.max(data, (d: ChartData) => d.count) || 0])
      .range([0, innerWidth]);

    const yScale = d3
      .scaleBand()
      .domain(data.map((d: ChartData) => d.name))
      .range([0, innerHeight])
      .padding(0.2);

    // Create bars (horizontal, right-aligned) - start with width 0 for animation
    const bars = g
      .selectAll('.bar')
      .data(data)
      .enter()
      .append('rect')
      .attr('class', 'bar')
      .attr('x', innerWidth) // Start at right edge
      .attr('y', (d: ChartData) => yScale(d.name) || 0)
      .attr('width', 0) // Start with width 0
      .attr('height', yScale.bandwidth())
      .attr('rx', 4) // Horizontal border radius
      .attr('ry', 4) // Vertical border radius
      .attr('fill', this.color)
      .attr('opacity', 0.8);

    // Store final positions and widths for animation
    bars.each(function (this: SVGRectElement, d: ChartData) {
      const finalWidth = xScale(d.count);
      const finalX = innerWidth - finalWidth;
      d3.select(this)
        .attr('data-final-width', finalWidth)
        .attr('data-final-x', finalX);
    });

    // Add language name labels on the right
    g.selectAll('.name-label')
      .data(data)
      .enter()
      .append('text')
      .attr('class', 'name-label')
      .attr('x', innerWidth + 10)
      .attr(
        'y',
        (d: ChartData) => (yScale(d.name) || 0) + yScale.bandwidth() / 2,
      )
      .attr('text-anchor', 'start')
      .attr('dominant-baseline', 'middle')
      .style('text-transform', 'capitalize')
      .style('font-size', '16px')
      .style('font-weight', '700')
      .style('fill', this.color)
      .text((d: ChartData) => d.name);

    // Add value labels on bars (start hidden)
    g.selectAll('.value-label')
      .data(data)
      .enter()
      .append('text')
      .attr('class', 'value-label')
      .attr('x', (d: ChartData) => innerWidth - xScale(d.count) - 5)
      .attr(
        'y',
        (d: ChartData) => (yScale(d.name) || 0) + yScale.bandwidth() / 2,
      )
      .attr('text-anchor', 'end')
      .attr('dominant-baseline', 'middle')
      .style('font-size', '14px')
      .style('font-weight', 'bold')
      .style('fill', this.color)
      .style('opacity', 0) // Start hidden
      .text((d: ChartData) => d.count);
  }

  private setupIntersectionObserver(): void {
    const instrumentsChart = document.getElementById('instruments-chart');
    const languagesChart = document.getElementById('languages-chart');

    if (!instrumentsChart || !languagesChart) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            if (entry.target.id === 'instruments-chart') {
              this.animateInstrumentsChart();
            } else if (entry.target.id === 'languages-chart') {
              this.animateLanguagesChart();
            }
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.3 },
    );

    observer.observe(instrumentsChart);
    observer.observe(languagesChart);
  }

  private animateInstrumentsChart(): void {
    const instrumentsChart = d3.select('#instruments-chart');
    const bars = instrumentsChart.selectAll('.bar');
    const valueLabels = instrumentsChart.selectAll('.value-label');

    // Animate bars first
    bars
      .transition()
      .duration(this.animationDuration)
      .delay((d: ChartData, i: number) => i * this.animationDelay)
      .attr('width', function (this: SVGRectElement) {
        return d3.select(this).attr('data-final-width');
      });

    // Then animate value labels after bars complete
    const maxDelay = (bars.size() - 1) * this.animationDelay;
    const labelStartDelay = maxDelay + this.animationDuration;

    valueLabels
      .transition()
      .duration(400)
      .delay((d: ChartData, i: number) => labelStartDelay + i * 50)
      .style('opacity', 1);
  }

  private animateLanguagesChart(): void {
    const languagesChart = d3.select('#languages-chart');
    const bars = languagesChart.selectAll('.bar');
    const valueLabels = languagesChart.selectAll('.value-label');

    // Animate bars first
    bars
      .transition()
      .duration(this.animationDuration)
      .delay((d: ChartData, i: number) => i * this.animationDelay)
      .attr('width', function (this: SVGRectElement) {
        return d3.select(this).attr('data-final-width');
      })
      .attr('x', function (this: SVGRectElement) {
        return d3.select(this).attr('data-final-x');
      });

    // Then animate value labels after bars complete
    const maxDelay = (bars.size() - 1) * this.animationDelay;
    const labelStartDelay = maxDelay + this.animationDuration;

    valueLabels
      .transition()
      .duration(400)
      .delay((d: ChartData, i: number) => labelStartDelay + i * 50)
      .style('opacity', 1);
  }
}

// Initialize the charts when this module is loaded
new BarCharts();
