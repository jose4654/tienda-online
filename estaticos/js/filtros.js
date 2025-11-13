// Script sencillo para filtrar productos por categoría en el listado principal.
document.addEventListener("DOMContentLoaded", () => {
  const botones = document.querySelectorAll("[data-category]");
  const productos = document.querySelectorAll(".producto");

  if (!botones.length || !productos.length) {
    return;
  }

  botones.forEach((boton) => {
    boton.addEventListener("click", () => {
      botones.forEach((b) => b.classList.remove("active"));
      boton.classList.add("active");

      const categoriaElegida = boton.getAttribute("data-category");

      productos.forEach((producto) => {
        const categoriaProducto = producto.getAttribute("data-category");
        const mostrar =
          categoriaElegida === "todos" || categoriaProducto === categoriaElegida;
        producto.style.display = mostrar ? "block" : "none";
      });
    });
  });
});

