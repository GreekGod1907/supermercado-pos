document.addEventListener('DOMContentLoaded', function() {
    // --- ELEMENTOS DEL DOM ---
    const cancelButton = document.querySelector('.cancel-button');
    const barcodeInput = document.getElementById('barcode-input');
    const saleItemsContainer = document.getElementById('sale-items');
    const totalDisplay = document.getElementById('total-display');
    const totalDisplaySummary = document.getElementById('total-display-summary');
    const subtotalDisplay = document.getElementById('subtotal-display');
    const itemsCountDisplay = document.getElementById('items-count');
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
        if (ventaActual.length > 0) {
            if (confirm('¿Estás seguro de que quieres cancelar la venta actual?')) {
                ventaActual = [];
                actualizarVistaVenta();
                // Enfocar de nuevo el input
                barcodeInput.focus();
            }
        }
    });

    // Listener para los clics en la tabla de venta
    saleItemsContainer.addEventListener('click', function(event) {
        if (event.target.classList.contains('delete-btn')) {
            const codigoBarra = event.target.dataset.codigo;
            eliminarProductoDeVenta(codigoBarra);
        }
    });

    // --- LÓGICA DE LA APLICACIÓN ---
    async function buscarYAgregarProducto() {
        const codigoBarra = barcodeInput.value.trim();
        if (!codigoBarra) return;

        // Mostrar loading en el input
        const originalPlaceholder = barcodeInput.placeholder;
        barcodeInput.placeholder = "Buscando producto...";
        barcodeInput.disabled = true;

        try {
            const response = await fetch(`/pos/api/buscar-producto/?codigo_barra=${codigoBarra}`);
            if (response.ok) {
                const producto = await response.json();
                producto.codigo_barra = codigoBarra;
                agregarProductoAVenta(producto);
                
                // Feedback visual positivo
                barcodeInput.style.borderColor = '#28a745';
                setTimeout(() => {
                    barcodeInput.style.borderColor = '';
                }, 1000);
            } else {
                // Feedback visual de error
                barcodeInput.style.borderColor = '#dc3545';
                setTimeout(() => {
                    barcodeInput.style.borderColor = '';
                }, 2000);
                alert('❌ Error: Producto no encontrado');
            }
        } catch (error) {
            barcodeInput.style.borderColor = '#dc3545';
            setTimeout(() => {
                barcodeInput.style.borderColor = '';
            }, 2000);
            alert('❌ Error de conexión.');
        } finally {
            // Restaurar input
            barcodeInput.placeholder = originalPlaceholder;
            barcodeInput.disabled = false;
            barcodeInput.value = '';
            barcodeInput.focus();
        }
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
        let totalItems = 0;

        if (ventaActual.length === 0) {
            // Mostrar estado vacío
            saleItemsContainer.innerHTML = `
                <tr>
                    <td colspan="5" class="empty-cart">
                        <div class="empty-cart-icon">🛒</div>
                        <div>No hay productos en la venta</div>
                        <div style="font-size: 0.9em; opacity: 0.7; margin-top: 0.5em;">
                            Escanea o ingresa un código de barras para comenzar
                        </div>
                    </td>
                </tr>
            `;
        } else {
            ventaActual.forEach(item => {
                const subtotal = item.cantidad * parseFloat(item.precio);
                totalVenta += subtotal;
                totalItems += item.cantidad;
                
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>
                        <strong>${item.nombre}</strong>
                        <div style="font-size: 0.8em; color: #666;">${item.codigo_barra}</div>
                    </td>
                    <td><strong>${item.cantidad}</strong></td>
                    <td class="mobile-hide">$${parseFloat(item.precio).toFixed(2)}</td>
                    <td><strong>$${subtotal.toFixed(2)}</strong></td>
                    <td><button class="delete-btn" data-codigo="${item.codigo_barra}" title="Eliminar producto">×</button></td>
                `;
                saleItemsContainer.appendChild(row);
            });
        }

        // Actualizar todos los displays
        const totalFormatted = `$${totalVenta.toFixed(2)}`;
        totalDisplay.textContent = totalFormatted;
        totalDisplaySummary.textContent = totalFormatted;
        subtotalDisplay.textContent = totalFormatted;
        itemsCountDisplay.textContent = `${totalItems} items`;
        
        // Actualizar estado de botones
        finalizeButton.disabled = ventaActual.length === 0;
        if (ventaActual.length === 0) {
            finalizeButton.style.opacity = '0.6';
            finalizeButton.style.cursor = 'not-allowed';
        } else {
            finalizeButton.style.opacity = '1';
            finalizeButton.style.cursor = 'pointer';
        }
    }

    function eliminarProductoDeVenta(codigoBarra) {
        const itemIndex = ventaActual.findIndex(item => item.codigo_barra === codigoBarra);

        if (itemIndex > -1) {
            const producto = ventaActual[itemIndex];
            if (confirm(`¿Eliminar "${producto.nombre}" de la venta?`)) {
                ventaActual.splice(itemIndex, 1);
                actualizarVistaVenta();
            }
        }
    }

    async function finalizarVenta() {
        if (ventaActual.length === 0) {
            alert("⚠️ No hay productos en la venta para finalizar.");
            return;
        }

        const totalVenta = ventaActual.reduce((sum, item) => sum + item.cantidad * parseFloat(item.precio), 0);

        // Mostrar loading en el botón
        const originalText = finalizeButton.textContent;
        finalizeButton.textContent = '⏳ Procesando...';
        finalizeButton.disabled = true;

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
                
                // Éxito - abrir recibo y limpiar venta
                window.open(`/pos/recibo/${result.venta_id}/`, '_blank');
                ventaActual = [];
                actualizarVistaVenta();
                
                // Mostrar mensaje de éxito
                const successMessage = document.createElement('div');
                successMessage.innerHTML = '✅ Venta finalizada correctamente';
                successMessage.style.cssText = `
                    position: fixed;
                    top: 100px;
                    right: 20px;
                    background: #28a745;
                    color: white;
                    padding: 1em 2em;
                    border-radius: 5px;
                    z-index: 1000;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                `;
                document.body.appendChild(successMessage);
                setTimeout(() => {
                    document.body.removeChild(successMessage);
                }, 3000);
                
                // Enfocar input para nueva venta
                barcodeInput.focus();
            } else {
                const errorData = await response.json();
                alert(`❌ Error al finalizar la venta: ${errorData.error}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('❌ Error de conexión al finalizar la venta.');
        } finally {
            // Restaurar botón
            finalizeButton.textContent = originalText;
            finalizeButton.disabled = ventaActual.length === 0;
        }
    }

    // Auto-focus en el input cuando se carga la página
    barcodeInput.focus();
    
    // Mantener focus en el input (útil para escáneres)
    document.addEventListener('click', function(event) {
        // Si no se clickeó en un input o botón, regresar focus al barcode input
        if (!event.target.matches('input, button, a')) {
            setTimeout(() => barcodeInput.focus(), 10);
        }
    });

    // Inicializar vista
    actualizarVistaVenta();
});