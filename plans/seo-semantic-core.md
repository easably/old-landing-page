# SEO: семантическое ядро EasyLang

Цель: охват запросов про обучение языкам через **YouTube**, **Netflix** (и близкие формулировки) плюс бренд и продукт.

## Ядро (англ., высокий приоритет)

| Кластер | Примеры формулировок |
|--------|------------------------|
| YouTube + языки | learn languages with YouTube, language learning with YouTube, learn a language watching YouTube |
| Netflix + языки | learn languages with Netflix, learn language with Netflix shows, Netflix language learning |
| Субтитры / видео | subtitles language learning, learn from videos, watch and learn languages |
| Продукт | EasyLang, EasyLang.app, language tutor app, free language learning app |
| Контекст / метод | context-based learning, vocabulary from content, language learning Chrome extension |

## Русский (доп.)

- учить язык по YouTube / Netflix  
- приложение для изучения языков по видео  
- субтитры для изучения языка  

## Внедрение на сайте

- `<title>`, `meta description`, `meta keywords` на лендинге `index.html`  
- Open Graph для сниппетов в соцсетях  
- `link rel=canonical` на главной и страницах блога (база: `https://easylang.app` — при другом домене заменить в `index.html`, `scripts/build_blog_html.py` константа `SITE_ORIGIN`, пересобрать блог и обновить `robots.txt` / `sitemap.xml`)  
- Тексты EN в `js/en.js` (hero и блок про источники) усилены под ядро  
- `sitemap.xml` генерируется `scripts/build_blog_html.py` вместе с постами  

**Заметка:** Google почти не использует `meta keywords`; основной сигнал — качественный текст, заголовки, `description`, внутренние ссылки и техническая индексация (`robots`, `sitemap`).
