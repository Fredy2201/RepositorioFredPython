

const getOptionChart2=()=>{
    let dataAxis = ['点', '击', '柱', '子', '或', '者', '两', '指', '在', '触', '屏', '上', '滑', '动', '能', '够', '自', '动', '缩', '放'];
// prettier-ignore
let data = [220, 182, 191, 234, 290, 330, 310, 123, 442, 321, 90, 149, 210, 122, 133, 334, 198, 123, 125, 220];
let yMax = 500;
let dataShadow = [];
for (let i = 0; i < data.length; i++) {
    dataShadow.push(yMax);
}
return {
    title: {
        text: '特性示例：渐变色 阴影 点击缩放',
        subtext: 'Feature Sample: Gradient Color, Shadow, Click Zoom'
    },
    xAxis: {
        data: dataAxis,
        axisLabel: {
        inside: true,
        color: '#fff'
        },
        axisTick: {
        show: false
        },
        axisLine: {
        show: false
        },
        z: 10
    },
    yAxis: {
        axisLine: {
        show: false
        },
        axisTick: {
        show: false
        },
        axisLabel: {
        color: '#999'
        }
    },
    dataZoom: [
        {
        type: 'inside'
        }
    ],
    series: [
        {
        type: 'bar',
        showBackground: true,
        itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
            ])
        },
        emphasis: {
            itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#2378f7' },
                { offset: 0.7, color: '#2378f7' },
                { offset: 1, color: '#83bff6' }
            ])
            }
        },
        data: data
        }
    ]
};
// Enable data zoom when user click bar.
const zoomSize = 6;
myChart.on('click', function (params) {
  console.log(dataAxis[Math.max(params.dataIndex - zoomSize / 2, 0)]);
  myChart.dispatchAction({
    type: 'dataZoom',
    startValue: dataAxis[Math.max(params.dataIndex - zoomSize / 2, 0)],
    endValue:
      dataAxis[Math.min(params.dataIndex + zoomSize / 2, data.length - 1)]
  });
});
};
const initCharts=()=>{
    const chart1=echarts.init(document.getElementById("chart1"))
    const chart2=echarts.init(document.getElementById("chart2"))

    chart1.setOption(getOptionChart1());
    chart2.setOption(getOptionChart2());
};

window.addEventListener('load',()=>{
    initCharts();
});

//ESTA PARTE SIRVE PARA MOSTRAR Y OCULTAR LAS TABLAS EN LOS REGISTROS DE SERVICIOS
const btntodo=document.getElementById('btntodo');
const btnhoy=document.getElementById('btnhoy');
const table1=document.getElementById('table1');
const table2=document.getElementById('table2');
const cuerpo1 = document.querySelector('#tablaResultados');

btntodo.addEventListener('click',()=>{
    table1.classList.add('oculto');
    table2.classList.remove('oculto');    
    cuerpo1.classList.add('oculto');
});

btnhoy.addEventListener('click',()=>{
    table2.classList.add('oculto');
    table1.classList.remove('oculto');
    cuerpo1.classList.add('oculto');
});
//FIN DEL CODIGO

//codigo para mostrar la tabla dinamica segun fechas en el registro de servicios
document.getElementById('formFechas').addEventListener('submit', async (e) => {
    e.preventDefault();
    table1.classList.add('oculto');
    table2.classList.add('oculto');
    cuerpo1.classList.remove('oculto');

    const inicio = document.getElementById('fechaInicio').value;
    const fin = document.getElementById('fechaFin').value;
    const mensaje = document.getElementById('mensajeCarga');
    const cuerpo = document.querySelector('#tablaResultados tbody');


    if (!inicio || !fin) {
        alert('Debe seleccionar ambas fechas.');
        return;
    }

    cuerpo.innerHTML = '';
    mensaje.style.display = 'block'; // mostrar "Cargando..."

    try {
      // 👇 Aquí hacemos la petición al backend Flask
        const respuesta = await fetch(`/api/tregistrosservicios?inicio=${inicio}&fin=${fin}`);
        const datos = await respuesta.json(); // ⬅️ Aquí se convierte el JSON en objeto JS
    
        mensaje.style.display = 'none';
        cuerpo.innerHTML = '';

        if (datos.length === 0) {
            cuerpo.innerHTML = '<tr><td colspan="5">No se encontraron registros en ese rango.</td></tr>';
            return;
        }

      // Insertar filas en la tabla dinámicamente
        datos.forEach(servicio => {
            const fila = document.createElement('tr');
            fila.innerHTML = `
            <td>${servicio.cod_ser}</td>
            <td>${servicio.des_ser}</td>
            <td>${servicio.fec_ser}</td>
            <td>${servicio.nom_cli}</td>
            <td>${servicio.monto}</td>
            <td>
                <a href="/teditarservicios/${servicio.cod_ser}" class="btn btn-warning">Editar</a> |
                <a href="/tborrarservicios/${servicio.cod_ser}" class="btn btn-danger onclick="return confirm('¿Estás seguro de borrar este registro?');">Borrar</a>
            </td>
            `;
            cuerpo.appendChild(fila);
        });

    } catch (error) {
        console.error('Error:', error);
        mensaje.style.display = 'none';
        cuerpo.innerHTML = '<tr><td colspan="5">Error al obtener los datos.</td></tr>';
    }
});

// fin de codigo