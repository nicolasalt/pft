
pft.charts = {};

pft.AddExpenseChart = function(container, data) {
  return new Highcharts.Chart({
    chart: {
        renderTo: container,
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false
    },
    title: {
        text: 'Expenses'
    },
    tooltip: {
        formatter: function() {
            return '<b>'+ this.point.name +'</b>: '+
                Math.round(this.percentage) + ' %';
        }
    },
    plotOptions: {
        pie: {
            allowPointSelect: true,
            cursor: 'pointer',
            dataLabels: {
                enabled: true,
                color: '#000000',
                connectorColor: '#000000',
                formatter: function() {
                    return '<b>'+ this.point.name +'</b>: '+ this.y +' CHF';
                }
            }
        }
    },
    series: [{
        type: 'pie',
        name: 'Expenses',
        data: data
    }]
});
};
