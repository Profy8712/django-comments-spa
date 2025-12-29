// frontend/src/i18n.js
import { createI18n } from "vue-i18n";

const STORAGE_KEY = "lang";

const messages = {
  en: {
    lang: { change: "Change language" },
    app: {
      title: "Comments SPA",
      language: "Language",
      themeLight: "Light",
      themeDark: "Dark",
    },
    auth: {
      enterCredentials: "Enter username and password.",
      loginFailed: "Login failed.",
      loggingIn: "Logging in...",
      copyBearerTitle: "Copy Authorization: Bearer <token>",
      tokensNote: "Tokens are stored in",
      updatesVia: "UI updates via",
      event: "event",
      title: "Auth",
      authorized: "Authorized",
      anonymous: "Anonymous",
      username: "Username",
      password: "Password",
      login: "Login",
      logout: "Logout",
      admin: "ADMIN",
      show: "Show",
      hide: "Hide",
    },
    form: {
      userInfo: "User information",
      userName: "Name",
      email: "Email",
      homepage: "Website",
      security: "Security",
      captcha: "Captcha",
      newComment: "New comment",
      required: "All fields with * are required.",
      content: "Content",
      write: "Write",
      preview: "Preview",
      send: "Send comment",
      placeholder:
        "Write your comment... (allowed tags: [i] [strong] [code] [a])",
    },
    attachments: {
      title: "Attachments",
      dropTitle: "Drag & drop files here",
      dropSub: "or click to browse",
      chooseFiles: "Choose files",
      chooseBtn: "Choose files",
      allowed:
        "Allowed: images (JPG/PNG/GIF/WEBP) and TXT (≤100 KB).",
      resizeNote: "Images are resized automatically.",
    },
    comments: {
      moreRepliesHidden: "More replies hidden",
      title: "Comments",
      hideReplies: "Hide replies",
      viewMoreReplies: "View more replies",
      showTable: "Show comments table",
      sortBy: "Sort by:",
      newestFirst: "Newest first (LIFO)",
      reply: "Reply",
      delete: "Delete",
      deleteTitle: "Delete comment",
      deleteConfirm: "Delete this comment?",
      deleteFailed: "Failed to delete comment",
    },
    common: {
      loading: "Loading...",
      cancel: "Cancel",
      close: "Close",
      copyBearer: "Copy Bearer",
    },
  },

  ru: {
    lang: { change: "Сменить язык" },
    app: {
      title: "Комментарии SPA",
      language: "Язык",
      themeLight: "Светлая",
      themeDark: "Тёмная",
    },
    auth: {
      enterCredentials: "Введите логин и пароль.",
      loginFailed: "Не удалось войти.",
      loggingIn: "Входим...",
      copyBearerTitle: "Скопировать Authorization: Bearer <token>",
      tokensNote: "Токены хранятся в",
      updatesVia: "Интерфейс обновляется через",
      event: "событие",
      title: "Вход",
      authorized: "Авторизован",
      anonymous: "Гость",
      username: "Логин",
      password: "Пароль",
      login: "Войти",
      logout: "Выйти",
      admin: "АДМИН",
      show: "Показать",
      hide: "Скрыть",
    },
    form: {
      userInfo: "Данные пользователя",
      userName: "Имя",
      email: "Email",
      homepage: "Сайт",
      security: "Безопасность",
      captcha: "Капча",
      newComment: "Новый комментарий",
      required: "Все поля со * обязательны.",
      content: "Текст",
      write: "Написать",
      preview: "Просмотр",
      send: "Отправить комментарий",
      placeholder:
        "Введите комментарий... (разрешённые теги: [i] [strong] [code] [a])",
    },
    attachments: {
      title: "Вложения",
      dropTitle: "Перетащите файлы сюда",
      dropSub: "или нажмите, чтобы выбрать",
      chooseFiles: "Выбрать файлы",
      chooseBtn: "Выбрать файлы",
      allowed:
        "Разрешено: изображения (JPG/PNG/GIF/WEBP) и TXT (≤100 KB).",
      resizeNote: "Изображения автоматически уменьшаются.",
    },
    comments: {
      moreRepliesHidden: "Скрыто больше ответов",
      title: "Комментарии",
      hideReplies: "Скрыть ответы",
      viewMoreReplies: "Показать ещё ответы",
      showTable: "Показать таблицу комментариев",
      sortBy: "Сортировка:",
      newestFirst: "Сначала новые (LIFO)",
      reply: "Ответить",
      delete: "Удалить",
      deleteTitle: "Удалить комментарий",
      deleteConfirm: "Удалить этот комментарий?",
      deleteFailed: "Не удалось удалить комментарий",
    },
    common: {
      loading: "Загрузка...",
      cancel: "Отмена",
      close: "Закрыть",
      copyBearer: "Копировать Bearer",
    },
  },

  uk: {
    lang: { change: "Змінити мову" },
    app: {
      title: "Коментарі SPA",
      language: "Мова",
      themeLight: "Світла",
      themeDark: "Темна",
    },
    auth: {
      loggingIn: "Входимо...",
      copyBearerTitle: "Скопіювати Authorization: Bearer <token>",
      tokensNote: "Токени зберігаються в",
      updatesVia: "Інтерфейс оновлюється через",
      event: "подію",
      title: "Вхід",
      authorized: "Авторизований",
      anonymous: "Гість",
      username: "Логін",
      password: "Пароль",
      login: "Увійти",
      logout: "Вийти",
      admin: "АДМІН",
      show: "Показати",
      hide: "Сховати",
    },
    form: {
      userInfo: "Дані користувача",
      userName: "Ім’я",
      email: "Email",
      homepage: "Сайт",
      security: "Безпека",
      captcha: "Капча",
      newComment: "Новий коментар",
      required: "Усі поля з * обов’язкові.",
      content: "Текст",
      write: "Написати",
      preview: "Перегляд",
      send: "Надіслати коментар",
      placeholder:
        "Напишіть коментар... (дозволені теги: [i] [strong] [code] [a])",
    },
    attachments: {
      title: "Вкладення",
      dropTitle: "Перетягніть файли сюди",
      dropSub: "або натисніть, щоб вибрати",
      chooseFiles: "Вибрати файли",
      chooseBtn: "Вибрати файли",
      allowed:
        "Дозволено: зображення (JPG/PNG/GIF/WEBP) і TXT (≤100 KB).",
      resizeNote: "Зображення автоматично зменшуються.",
    },
    comments: {
      moreRepliesHidden: "Приховано більше відповідей",
      title: "Коментарі",
      hideReplies: "Сховати відповіді",
      viewMoreReplies: "Показати ще відповіді",
      showTable: "Показати таблицю коментарів",
      sortBy: "Сортування:",
      newestFirst: "Спочатку нові (LIFO)",
      reply: "Відповісти",
      delete: "Видалити",
      deleteTitle: "Видалити коментар",
      deleteConfirm: "Видалити цей коментар?",
      deleteFailed: "Не вдалося видалити коментар",
    },
    common: {
      loading: "Завантаження...",
      cancel: "Скасувати",
      close: "Закрити",
      copyBearer: "Скопіювати Bearer",
    },
  },

  de: {
    lang: { change: "Sprache wechseln" },
    app: {
      title: "Kommentare SPA",
      language: "Sprache",
      themeLight: "Hell",
      themeDark: "Dunkel",
    },
    auth: {
      loggingIn: "Anmelden...",
      copyBearerTitle: "Authorization: Bearer <token> kopieren",
      tokensNote: "Tokens werden gespeichert in",
      updatesVia: "UI aktualisiert sich über",
      event: "Event",
      title: "Anmeldung",
      authorized: "Angemeldet",
      anonymous: "Gast",
      username: "Benutzername",
      password: "Passwort",
      login: "Einloggen",
      logout: "Ausloggen",
      admin: "ADMIN",
      show: "Anzeigen",
      hide: "Ausblenden",
    },
    form: {
      userInfo: "Benutzerdaten",
      userName: "Name",
      email: "E-Mail",
      homepage: "Webseite",
      security: "Sicherheit",
      captcha: "Captcha",
      newComment: "Neuer Kommentar",
      required: "Alle Felder mit * sind erforderlich.",
      content: "Inhalt",
      write: "Schreiben",
      preview: "Vorschau",
      send: "Kommentar senden",
      placeholder:
        "Schreibe deinen Kommentar... (erlaubte Tags: [i] [strong] [code] [a])",
    },
    attachments: {
      title: "Anhänge",
      dropTitle: "Dateien hierher ziehen",
      dropSub: "oder klicken zum Auswählen",
      chooseFiles: "Dateien auswählen",
      chooseBtn: "Dateien auswählen",
      allowed:
        "Erlaubt: Bilder (JPG/PNG/GIF/WEBP) und TXT (≤100 KB).",
      resizeNote: "Bilder werden automatisch verkleinert.",
    },
    comments: {
      moreRepliesHidden: "Weitere Antworten ausgeblendet",
      title: "Kommentare",
      hideReplies: "Antworten ausblenden",
      viewMoreReplies: "Mehr Antworten anzeigen",
      showTable: "Kommentartabelle anzeigen",
      sortBy: "Sortieren nach:",
      newestFirst: "Neueste zuerst (LIFO)",
      reply: "Antworten",
      delete: "Löschen",
      deleteTitle: "Kommentar löschen",
      deleteConfirm: "Diesen Kommentar löschen?",
      deleteFailed: "Kommentar konnte nicht gelöscht werden",
    },
    common: {
      loading: "Lädt...",
      cancel: "Abbrechen",
      close: "Schließen",
      copyBearer: "Bearer kopieren",
    },
  },
};

function normalizeLang(lang) {
  if (!lang) return null;
  const v = String(lang).toLowerCase();
  return ["en", "ru", "uk", "de"].includes(v) ? v : null;
}

function detectLang() {
  const saved = normalizeLang(localStorage.getItem(STORAGE_KEY));
  if (saved) return saved;

  const nav = String(navigator.language || "").toLowerCase();
  if (nav.startsWith("de")) return "de";
  if (nav.startsWith("uk")) return "uk";
  if (nav.startsWith("ru")) return "ru";
  return "en";
}

export const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: detectLang(),
  fallbackLocale: "en",
  messages,
});

export function setLang(lang) {
  const v = normalizeLang(lang) || "en";
  i18n.global.locale.value = v;
  localStorage.setItem(STORAGE_KEY, v);
}
