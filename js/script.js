document.addEventListener('DOMContentLoaded', ready)

function ready() {
	var wow = new WOW();
	wow.init();

	setAutoLanguage();

	$('.slides').slick({
		dots: true,
		infinite: true,
		speed: 900,
		fade: true
	});

	$('.menu-btn').on('click', function (e) {
		e.preventDefault;
		$(this).toggleClass('menu-btn_active');
		$('.menu-main').toggleClass('menu-main_active');
	});
	$('.overlay').on('click', function () {
		closeMenu()
	});
	$('.menu-nav__link').on('click', function () {
		closeMenu()
	});

	window.onscroll = function showHeader() {
		var stickyMenu = document.querySelector('.navbar');
		if (window.pageYOffset > 50) {
			stickyMenu.classList.add('fixed-bar');
			stickyMenu.classList.remove('no-fixed-bar');
		} else {
			stickyMenu.classList.add('no-fixed-bar');
			stickyMenu.classList.remove('fixed-bar');
		}

		if (document.body.scrollTop > 150 || document.documentElement.scrollTop > 150) {
			document.getElementById("btnTop").style.display = "block";
		} else {
			document.getElementById("btnTop").style.display = "none";
		}
	}

	document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
		anchor.addEventListener('click', function (e) {
			e.preventDefault();
			var el = document.querySelector(this.getAttribute('href'));
			var top =  el.getBoundingClientRect().top + window.pageYOffset;
			var offset = - 100;
			window.scrollTo({
				top: top + offset,
				behavior: 'smooth'
			})
		});
	});
}

function getUserLanguage() {
	return navigator.language ||
		navigator.languages && navigator.languages[0] ||
		navigator.userLanguage ||
		'en';
}

function setAutoLanguage() {
	var userLang = getUserLanguage();
	var selectLang = document.querySelector('#getLang');
	selectLang.querySelectorAll('option').forEach(function (e) {
		if (userLang.indexOf(e.value) !== -1) {
			selectLang.value = e.value;
		}
	})
	changeLocale();
}

function closeMenu() {
	$('.menu-btn').removeClass('menu-btn_active');
	$('.menu-main').removeClass('menu-main_active');
}

function topFunction() {
	$('html, body').animate({
		scrollTop: 0
	}, '50');
}

function changeLocale() {
	var selectLang = document.getElementById('getLang');
	var locale = languageEN;
	if (selectLang.value == 'en') {
		locale = languageEN;
	} else if (selectLang.value == 'ru') {
		locale = languageRU;
	} else if (selectLang.value == 'cn') {
		locale = languageCN;
	}
	Object.keys(locale).forEach(function (id) {
		document.getElementById(id).innerHTML = locale[id];
	});

}
