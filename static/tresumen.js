// ✅ 1. Función que obtiene los datos desde Flask, filtrando por mes
const getOptionChart1 = async (mes) => {
    // Si no hay mes elegido, usa el actual
    const mesParam = mes || new Date().toISOString().slice(0, 7); // Ej: "2025-11"

    // Llamada al backend Flask, pasando el mes como parámetro GET
    const response = await fetch(`/datos_tresumen?mes=${mesParam}`);
    const datos = await response.json();

    // Devuelve la configuración del gráfico con los datos reales
    return {
        title: {
            text: `Gastos del mes ${mesParam}`,
            subtext: 'Datos desde Flask',
            left: 'center'
        },
        tooltip: { trigger: 'item' },
        legend: {
            orient: 'horizontal',
            bottom: 0,
            left: 'center'
        },
        series: [
            {
                name: 'Categoría',
                type: 'pie',
                radius: '50%',
                data: datos,  // 👈 datos recibidos de Flask
                label: {
                    show: true,
                    formatter: '{b}: {c} ({d}%)'
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

// ✅ 2. Inicializa el gráfico
const initCharts = async (mes) => {
    const chart1 = echarts.init(document.getElementById("chart1"));

    const option = await getOptionChart1(mes);
    chart1.setOption(option);

    return chart1; // Devuelve el gráfico para poder actualizarlo después
};

// ✅ 3. Al cargar la página, muestra el gráfico del mes actual
let chartInstance;
window.addEventListener('load', async () => {
    chartInstance = await initCharts();
});

// ✅ 4. Escucha cuando el usuario cambia el mes
document.getElementById('mesSeleccionado').addEventListener('change', async (e) => {
    const mesElegido = e.target.value; // Ej: "2025-10"
    if (!mesElegido) return;

    const nuevaConfig = await getOptionChart1(mesElegido);
    chartInstance.setOption(nuevaConfig, true); // 🔁 Actualiza el gráfico sin recargar la página
});
