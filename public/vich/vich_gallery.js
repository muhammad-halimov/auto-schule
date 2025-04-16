function openModal(modalId) {
    var modal = document.getElementById(modalId);
    modal.style.display = "block";
    var carousel = new bootstrap.Carousel(document.querySelector("#" + modalId + " .carousel"));
    carousel.to(0); // Показать первый слайд
}

function closeModal(modalId) {
    var modal = document.getElementById(modalId);
    modal.style.display = "none";
}
