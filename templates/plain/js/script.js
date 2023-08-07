(new IntersectionObserver(function (e, o) {
    if (e[0].intersectionRatio > 0) {
        document.documentElement.removeAttribute('class');
        document.querySelector('.brandingLogo').style.maxWidth = "190px";
    } else {
        document.documentElement.setAttribute('class', 'stuck');
        document.querySelector('.brandingLogo').style.maxWidth = "150px";
    };
})).observe(document.querySelector('.trigger'));