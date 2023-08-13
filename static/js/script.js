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

function getOS() {
    var userAgent = window.navigator.userAgent,
        platform = window.navigator?.userAgentData?.platform || window.navigator.platform,
        macosPlatforms = ['Macintosh', 'MacIntel', 'MacPPC', 'Mac68K'],
        windowsPlatforms = ['Win32', 'Win64', 'Windows', 'WinCE'],
        iosPlatforms = ['iPhone', 'iPad', 'iPod'],
        os = null;

    if (macosPlatforms.indexOf(platform) !== -1) {
        os = 'Mac OS';
    } else if (iosPlatforms.indexOf(platform) !== -1) {
        os = 'iOS';
    } else if (windowsPlatforms.indexOf(platform) !== -1) {
        os = 'Windows';
    } else if (/Android/.test(userAgent)) {
        os = 'Android';
    } else if (/Linux/.test(platform)) {
        os = 'Linux';
    }

    return os;
}

if (getOS() == "Windows") {
    document.body.style.zoom = "80%"
}