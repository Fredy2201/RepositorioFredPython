// 🧠 Esta función ahora es ASYNC porque usa await
const getOptionChart1 = async () => {
    // Espera la respuesta del servidor Flask
    const response = await fetch("/datos_tresumen");
    const datos = await response.json();

    // Devuelve la configuración del gráfico con los datos reales
    return {
        title: {
            text: 'Gastos de este Mes',
            subtext: 'Datos desde Flask',
            left: 'center'
        },
        tooltip: {
            trigger: 'item'
        },
        legend: {
            orient: 'horizontal',
            bottom: 0,
            left: 'center'
        },
        series: [
            {
                name: 'Access From',
                type: 'pie',
                radius: '50%',
                data: datos,  // 👈 datos recibidos de Flask
                label: {
                    show: true, // 1. Muestra la etiqueta
                    formatter: ' {c} ({d}%)' // 2. Define el formato del contenido
                },
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ]
    };
};

// 🧩 También hacemos async esta función, porque esperará el gráfico
const initCharts = async () => {
    const chart1 = echarts.init(document.getElementById("chart1"));

    // Esperamos que getOptionChart1 termine antes de usar su resultado
    const option = await getOptionChart1();

    chart1.setOption(option);
};

// 👇 Al cargar la página, ejecuta initCharts()
window.addEventListener('load', () => {
    initCharts();
});
