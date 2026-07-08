(function () {
  const dialog = document.createElement("div");
  dialog.className = "lightbox";
  dialog.hidden = true;
  dialog.innerHTML = `
    <div class="lightbox-backdrop" data-lightbox-close></div>
    <div class="lightbox-panel" role="dialog" aria-modal="true" aria-label="Vista ampliada">
      <button class="lightbox-close" type="button" aria-label="Cerrar" data-lightbox-close>&times;</button>
      <img class="lightbox-image" alt="">
      <p class="lightbox-status" aria-live="polite"></p>
      <div class="lightbox-footer">
        <p class="lightbox-caption"></p>
        <a class="lightbox-download" href="#" download>Descargar</a>
      </div>
    </div>
  `;
  document.body.append(dialog);

  const image = dialog.querySelector(".lightbox-image");
  const status = dialog.querySelector(".lightbox-status");
  const caption = dialog.querySelector(".lightbox-caption");
  const download = dialog.querySelector(".lightbox-download");
  let previousFocus = null;
  let loadToken = 0;

  const close = () => {
    loadToken += 1;
    dialog.hidden = true;
    document.body.classList.remove("has-lightbox");
    image.removeAttribute("src");
    image.hidden = true;
    status.textContent = "";
    if (previousFocus) {
      previousFocus.focus();
    }
  };

  const open = (link) => {
    const thumbnail = link.querySelector("img");
    const label = link.dataset.lightboxTitle || thumbnail?.alt || link.textContent.trim() || "Imagen ampliada";
    const currentToken = loadToken + 1;
    loadToken = currentToken;
    previousFocus = document.activeElement;
    image.hidden = true;
    image.removeAttribute("src");
    image.alt = label;
    status.textContent = "Cargando imagen...";
    caption.textContent = label;
    download.href = link.href;
    dialog.hidden = false;
    document.body.classList.add("has-lightbox");
    dialog.querySelector(".lightbox-close").focus();

    const loader = new Image();
    loader.onload = () => {
      if (currentToken !== loadToken) {
        return;
      }
      image.src = link.href;
      image.hidden = false;
      status.textContent = "";
    };
    loader.onerror = () => {
      if (currentToken !== loadToken) {
        return;
      }
      status.textContent = "No se ha podido cargar la imagen ampliada.";
    };
    loader.src = link.href;
  };

  document.addEventListener("click", (event) => {
    const link = event.target.closest("[data-lightbox]");

    if (!link) {
      return;
    }

    event.preventDefault();
    open(link);
  });

  dialog.addEventListener("click", (event) => {
    if (event.target.closest("[data-lightbox-close]")) {
      close();
    }
  });

  document.addEventListener("keydown", (event) => {
    if (!dialog.hidden && event.key === "Escape") {
      close();
    }
  });
})();
