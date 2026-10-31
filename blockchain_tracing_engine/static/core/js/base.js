const menuButton = document.querySelector(".mobile-menu-btn");
const mobileMenu = document.querySelector(".mobile-nav");

if (menuButton) {

    menuButton.addEventListener("click", () => {

        mobileMenu.classList.toggle("active");

    });

}