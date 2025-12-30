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
      homepage: "Home page",
      security: "Security",
      captcha: "Captcha",
      newComment: "New comment",
      required: "All fields with * are required.",
      content: "Content",
      write: "Write",
      preview: "Preview",
      send: "Send comment",
      sendShort: "Send",

      text: "Message",
      previewEmpty: "Nothing to preview",
      editorMode: "Editor mode",
      captchaReload: "Reload CAPTCHA",
      captchaPlaceholder: "Enter CAPTCHA",

      tags: {
        iTitle: "Italic",
        strongTitle: "Bold",
        codeTitle: "Code",
        aTitle: "Link",
      },

      captchaLoadFail: "Failed to load CAPTCHA. Please reload.",
      tagsUnclosed: "Please make sure all tags are properly closed.",
      requestFailed: "Request failed. Please try again.",
      errTextRequired: "Text is required.",
      errUserRequired: "User name is required.",
      errEmailRequired: "E-mail is required.",
      errCaptchaRequired: "CAPTCHA is required.",
      validationFailed: "Validation failed.",
      commentAdded: "Comment added.",
      placeholder:
        "Write your comment... (allowed tags: [i] [strong] [code] [a])",
    },
    attachments: {
      chooseTitle: "Choose file",
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
      homepage: "Домашняя страница",
      security: "Безопасность",
      captcha: "Капча",
      newComment: "Новый комментарий",
      required: "Все поля со * обязательны.",
      content: "Текст",
      write: "Написать",
      preview: "Просмотр",
      send: "Отправить комментарий",
      sendShort: "Отправить",

      text: "Сообщение",
      previewEmpty: "Нечего показывать",
      editorMode: "Режим редактора",
      captchaReload: "Обновить капчу",
      captchaPlaceholder: "Введите капчу",

      tags: {
        iTitle: "Курсив",
        strongTitle: "Жирный",
        codeTitle: "Код",
        aTitle: "Ссылка",
      },

      captchaLoadFail: "Не удалось загрузить капчу. Обновите страницу.",
      tagsUnclosed: "Проверьте, что все теги закрыты.",
      requestFailed: "Ошибка запроса. Попробуйте ещё раз.",
      errTextRequired: "Текст обязателен.",
      errUserRequired: "Имя обязательно.",
      errEmailRequired: "Email обязателен.",
      errCaptchaRequired: "Капча обязательна.",
      validationFailed: "Проверка не пройдена.",
      commentAdded: "Комментарий добавлен.",
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
      homepage: "Домашняя страница",
      security: "Безпека",
      captcha: "Капча",
      newComment: "Новий коментар",
      required: "Усі поля з * обов’язкові.",
      content: "Текст",
      write: "Написати",
      preview: "Перегляд",
      send: "Надіслати коментар",
      sendShort: "Надіслати",

      text: "Повідомлення",
      previewEmpty: "Немає що показувати",
      editorMode: "Режим редактора",
      captchaReload: "Оновити капчу",
      captchaPlaceholder: "Введіть капчу",

      tags: {
        iTitle: "Курсив",
        strongTitle: "Жирний",
        codeTitle: "Код",
        aTitle: "Посилання",
      },

      captchaLoadFail: "Не вдалося завантажити капчу. Оновіть сторінку.",
      tagsUnclosed: "Перевірте, що всі теги закриті.",
      requestFailed: "Помилка запиту. Спробуйте ще раз.",
      errTextRequired: "Текст обовʼязковий.",
      errUserRequired: "Імʼя обовʼязкове.",
      errEmailRequired: "Email обовʼязковий.",
      errCaptchaRequired: "Капча обовʼязкова.",
      validationFailed: "Перевірка не пройдена.",
      commentAdded: "Коментар додано.",
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
      homepage: "Startseite",
      security: "Sicherheit",
      captcha: "Captcha",
      newComment: "Neuer Kommentar",
      required: "Alle Felder mit * sind erforderlich.",
      content: "Inhalt",
      write: "Schreiben",
      preview: "Vorschau",
      send: "Kommentar senden",
      sendShort: "Senden",

      text: "Nachricht",
      previewEmpty: "Nichts zum Anzeigen",
      editorMode: "Editor-Modus",
      captchaReload: "Captcha neu laden",
      captchaPlaceholder: "Captcha eingeben",

      tags: {
        iTitle: "Kursiv",
        strongTitle: "Fett",
        codeTitle: "Code",
        aTitle: "Link",
      },

      captchaLoadFail: "Captcha konnte nicht geladen werden. Bitte neu laden.",
      tagsUnclosed: "Bitte prüfe, ob alle Tags korrekt geschlossen sind.",
      requestFailed: "Anfrage fehlgeschlagen. Bitte erneut versuchen.",
      errTextRequired: "Text ist erforderlich.",
      errUserRequired: "Name ist erforderlich.",
      errEmailRequired: "E-Mail ist erforderlich.",
      errCaptchaRequired: "Captcha ist erforderlich.",
      validationFailed: "Validierung fehlgeschlagen.",
      commentAdded: "Kommentar hinzugefügt.",
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
  fallbackLocale: "en",
  legacy: false,
  globalInjection: true,
  locale: (localStorage.getItem("lang") || "en").toLowerCase().split("-")[0],
  messages,
});
export function setLang(lang) {
  const v = normalizeLang(lang) || "en";
  i18n.global.locale.value = v;
  localStorage.setItem(STORAGE_KEY, v);
}
