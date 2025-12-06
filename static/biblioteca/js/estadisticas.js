document.addEventListener('DOMContentLoaded', function () {

    // ========= PIE: Libros por estado =========
    const canvasEstado = document.getElementById('graficoEstado');
    if (canvasEstado && window.etiquetas && window.cantidades) {
        const ctxEstado = canvasEstado.getContext('2d');

        new Chart(ctxEstado, {
            type: 'pie',
            data: {
                labels: window.etiquetas,
                datasets: [{
                    label: 'Libros por estado',
                    data: window.cantidades,
                    backgroundColor: ['#ffccdc', '#b8b8ff', '#a0e7e5', '#fbe7c6', '#d5aaff'],
                    borderColor: '#ffffff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,  
                aspectRatio: 1,              
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: {
                                family: 'Arial',
                                size: 14
                            }
                        }
                    }
                }
            }
        });
    }

    // ========= LÍNEA: Evolución mensual =========
    const canvasMes = document.getElementById('graficoMes');
    if (canvasMes && window.meses && window.datos_linea) {
        const ctxMes = canvasMes.getContext('2d');

        const meses = window.meses;
        const datosLinea = window.datos_linea;
        const datasets = [];

        if (datosLinea.iniciado) {
            datasets.push({
                label: 'Iniciado',
                data: datosLinea.iniciado,
                borderColor: '#ffb6b9',
                backgroundColor: '#ffb6b9',
                tension: 0.3
            });
        }

        if (datosLinea.en_curso) {
            datasets.push({
                label: 'En curso',
                data: datosLinea.en_curso,
                borderColor: '#a0e7e5',
                backgroundColor: '#a0e7e5',
                tension: 0.3
            });
        }

        if (datosLinea.finalizado) {
            datasets.push({
                label: 'Finalizado',
                data: datosLinea.finalizado,
                borderColor: '#b8b8ff',
                backgroundColor: '#b8b8ff',
                tension: 0.3
            });
        }

        new Chart(ctxMes, {
            type: 'line',
            data: {
                labels: meses,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: 2.2,  
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Mes'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        },
                        title: {
                            display: true,
                            text: 'Cantidad'
                        }
                    }
                }
            }
        });
    }

});

