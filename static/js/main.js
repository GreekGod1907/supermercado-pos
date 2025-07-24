document.addEventListener('DOMContentLoaded', function() {
            // --- ELEMENTOS DEL DOM ---
            const cancelButton = document.querySelector('.cancel-button');
            const barcodeInput = document.getElementById('barcode-input');
            const saleItemsContainer = document.getElementById('sale-items');
            const totalDisplay = document.getElementById('total-display');
            const finalizeButton = document.querySelector('.finalize-button');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            // --- ESTADO DE LA APLICACIÓN ---
            let ventaActual = [];

            // --- EVENT LISTENERS ---
            barcodeInput.addEventListener('keypress', async function(event) {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    await buscarYAgregarProducto();
                }
            });

            finalizeButton.addEventListener('click', async function() {
                await finalizarVenta();
            });

            cancelButton.addEventListener('click', function() {
            // Solo muestra la confirmación si hay productos en la venta
                if (ventaActual.length > 0) {
                    if (confirm('¿Estás seguro de que quieres cancelar la venta actual?')) {
                    ventaActual = []; // Vacía el array de la venta
                    actualizarVistaVenta(); // Redibuja la tabla y el total
                    }
                }
            });

            // Listener para los clics en la tabla de venta
            saleItemsContainer.addEventListener('click', function(event) {
            // Verifica si el elemento clickeado es un botón de eliminar
                if (event.target.classList.contains('delete-btn')) {
                    const codigoBarra = event.target.dataset.codigo;
                    eliminarProductoDeVenta(codigoBarra);
                }
            });

            // --- LÓGICA DE LA APLICACIÓN ---
            async function buscarYAgregarProducto() {
                const codigoBarra = barcodeInput.value;
                if (!codigoBarra) return;

                try {
                    const response = await fetch(`/pos/api/buscar-producto/?codigo_barra=${codigoBarra}`);
                    if (response.ok) {
                        const producto = await response.json();
                        producto.codigo_barra = codigoBarra; // Añadimos el código para usarlo después
                        agregarProductoAVenta(producto);
                    } else {
                        alert('Error: Producto no encontrado');
                    }
                } catch (error) {
                    alert('Error de conexión.');
                }
                barcodeInput.value = '';
            }

            function agregarProductoAVenta(producto) {
                const productoExistente = ventaActual.find(item => item.codigo_barra === producto.codigo_barra);
                if (productoExistente) {
                    productoExistente.cantidad++;
                } else {
                    ventaActual.push({ ...producto, cantidad: 1 });
                }
                actualizarVistaVenta();
            }

            function actualizarVistaVenta() {
                saleItemsContainer.innerHTML = '';
                let totalVenta = 0;

                ventaActual.forEach(item => {
                    const subtotal = item.cantidad * parseFloat(item.precio);
                    totalVenta += subtotal;
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${item.nombre}</td>
                        <td>${item.cantidad}</td>
                        <td>$${parseFloat(item.precio).toFixed(2)}</td>
                        <td>$${subtotal.toFixed(2)}</td>
                        <td><button class="delete-btn" data-codigo="${item.codigo_barra}">X</button></td>
                    `;
                    saleItemsContainer.appendChild(row);
                });
                totalDisplay.textContent = `$${totalVenta.toFixed(2)}`;
            }

            function eliminarProductoDeVenta(codigoBarra) {
                const itemIndex = ventaActual.findIndex(item => item.codigo_barra === codigoBarra);

                if (itemIndex > -1) {
                    // Elimina el producto del array
                    ventaActual.splice(itemIndex, 1);
                    // Vuelve a dibujar la tabla y actualizar el total
                    actualizarVistaVenta();
                }
            }

            async function finalizarVenta() {
                if (ventaActual.length === 0) {
                    alert("No hay productos en la venta para finalizar.");
                    return;
                }

                const totalVenta = ventaActual.reduce((sum, item) => sum + item.cantidad * parseFloat(item.precio), 0);

                try {
                    const response = await fetch('/pos/api/finalizar-venta/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({ 
                            items: ventaActual,
                            total: totalVenta
                        })
                    });

                    if (response.ok) {
                        const result = await response.json();
                        window.open(`/pos/recibo/${result.venta_id}/`, '_blank'); // Abre el recibo
                        ventaActual = [];
                        actualizarVistaVenta();
                    } else {
                        const errorData = await response.json();
                        alert(`Error al finalizar la venta: ${errorData.error}`);
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Error de conexión al finalizar la venta.');
                }
            }
        });