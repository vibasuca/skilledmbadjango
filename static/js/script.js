(new IntersectionObserver(function (e, o) {
    var navbar = document.getElementById('myNavbar');
    if (e[0].intersectionRatio > 0) {
        document.documentElement.removeAttribute('class');
        document.querySelector('.brandingLogo').style.maxWidth = "190px";
        navbar.classList.remove("sticky");
    } else {
        document.documentElement.setAttribute('class', 'stuck');
        document.querySelector('.brandingLogo').style.maxWidth = "150px";
        navbar.classList.add("sticky");
    };
})).observe(document.querySelector('.trigger'));