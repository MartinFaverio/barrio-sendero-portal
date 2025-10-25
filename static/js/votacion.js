// ⭐ Pintado visual de estrellas por característica
document.querySelectorAll('.estrellas').forEach(contenedor => {
    const estrellas = contenedor.querySelectorAll('i');
    estrellas.forEach((star, index) => {
        star.addEventListener('click', () => {
            const valor = index + 1;
            estrellas.forEach((s, i) => {
                s.classList.toggle('bi-star-fill', i < valor);
                s.classList.toggle('bi-star', i >= valor);
            });
            const select = contenedor.previousElementSibling;
            if (select && select.tagName === 'SELECT') {
                select.value = valor;
            }
        });
    });
});

// 📩 Envío completo de opinión con comentario
document.getElementById('form-opinion')?.addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());

    fetch('/opiniones/votar', {  // ✅ Ruta corregida
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }).then(res => res.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert('¡Gracias por tu opinión!');
            const promedioElem = document.getElementById(`promedio-${data.id}`);
            if (promedioElem) {
                promedioElem.textContent = `Promedio: ${data.promedio.toFixed(1)}`;
            }
        }
    });
});