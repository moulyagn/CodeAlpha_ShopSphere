document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".hero-content, .intro-band, .collection-band, .auth-panel").forEach((element) => {
    element.classList.add("is-visible");
  });

  document.querySelectorAll(".product-image-wrap img").forEach((image) => {
    if (!image.complete) {
      image.classList.add("image-loading");
      image.addEventListener("load", () => image.classList.remove("image-loading"), { once: true });
    }
  });

  document.querySelectorAll(".gallery-thumb").forEach((thumb) => {
    thumb.addEventListener("click", () => {
      document.querySelector("#gallery-main-image").src = thumb.dataset.image;
      document.querySelectorAll(".gallery-thumb").forEach((item) => item.classList.remove("active"));
      thumb.classList.add("active");
    });
  });

  const galleryImage = document.querySelector("#gallery-main-image");
  if (galleryImage) {
    galleryImage.addEventListener("click", () => galleryImage.classList.toggle("zoomed"));
  }

  const searchInput = document.querySelector("#search-input");
  const suggestions = document.querySelector("#suggestions");
  if (searchInput && suggestions) {
    searchInput.addEventListener("input", async () => {
      if (searchInput.value.trim().length < 2) { suggestions.innerHTML = ""; return; }
      const response = await fetch(`/search/suggest?q=${encodeURIComponent(searchInput.value.trim())}`);
      const items = await response.json();
      suggestions.innerHTML = items.map((item) => `<a href="${item.url}">${item.label}<small>${item.type}</small></a>`).join("");
    });
  }

  document.querySelectorAll("button").forEach((button) => {
    if (button.textContent.trim() === "Checkout in Phase 3") {
      const checkoutLink = document.createElement("a");
      checkoutLink.href = "/orders/checkout";
      checkoutLink.className = button.className;
      checkoutLink.textContent = "Proceed to checkout";
      button.replaceWith(checkoutLink);
    }
  });
});
