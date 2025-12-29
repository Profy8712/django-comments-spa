// frontend/src/i18n.js
import { createI18n } from "vue-i18n";

const STORAGE_KEY = "lang";

const messages = {
  en: {
    app: {
      title: "Comments",
      language: "Language",
      theme: "Theme",
    },
    auth: {
      title: "Auth",
      authorized: "Authorized",
      anonymous: "Anonymous",
      username: "Username",
      password: "Password",
      login: "Login",
      logout: "Logout",
      admin: "ADMIN",
    },
    comments: {
      addTitle: "Add comment",
      reply: "Reply",
      delete: "Delete",
      send: "Send",
      preview: "Preview",
      attachments: "Attachments",
      moreRepliesHidden: "More replies hidden",
      showMore: "Show more",
      hide: "Hide",
      empty: "No comments yet",
    },
    common: {
      loading: "Loading...",
      cancel: "Cancel",
      save: "Save",
      close: "Close",
    },
  },

  ru: {
    app: {
      title: "Комментарии",
      language: "Язык",
      theme: "Тема",
    },
    auth: {
      title: "Вход",
      authorized: "Авторизован",
      anonymous: "Гость",
      username: "Логин",
      password: "Пароль",
      login: "Войти",
      logout: "Выйти",
      admin: "АДМИН",
    },
    comments: {
      addTitle: "Добавить комментарий",
      reply: "Ответить",
      delete: "Удалить",
      send: "Отправить",
      preview: "Предпросмотр",
      attachments: "Вложения",
      moreRepliesHidden: "Скрыто ответов",
      showMore: "Показать",
      hide: "Скрыть",
      empty: "Комментариев пока нет",
    },
    common: {
      loading: "Загрузка...",
      cancel: "Отмена",
      save: "Сохранить",
      close: "Закрыть",
    },
  },

  uk: {
    app: {
      title: "Коментарі",
      language: "Мова",
      theme: "Тема",
    },
    auth: {
      title: "Вхід",
      authorized: "Авторизований",
      anonymous: "Гість",
      username: "Логін",
      password: "Пароль",
      login: "Увійти",
      logout: "Вийти",
      admin: "АДМІН",
    },
    comments: {
      addTitle: "Додати коментар",
      reply: "Відповісти",
      delete: "Видалити",
      send: "Надіслати",
      preview: "Попередній перегляд",
      attachments: "Вкладення",
      moreRepliesHidden: "Приховано відповіді",
      showMore: "Показати",
      hide: "Сховати",
      empty: "Коментарів ще немає",
    },
    common: {
      loading: "Завантаження...",
      cancel: "Скасувати",
      save: "Зберегти",
      close: "Закрити",
    },
  },

  de: {
    app: {
      title: "Kommentare",
      language: "Sprache",
      theme: "Thema",
    },
    auth: {
      title: "Anmeldung",
      authorized: "Angemeldet",
      anonymous: "Gast",
      username: "Benutzername",
      password: "Passwort",
      login: "Einloggen",
      logout: "Ausloggen",
      admin: "ADMIN",
    },
    comments: {
      addTitle: "Kommentar hinzufügen",
      reply: "Antworten",
      delete: "Löschen",
      send: "Senden",
      preview: "Vorschau",
      attachments: "Anhänge",
      moreRepliesHidden: "Weitere Antworten sind verborgen",
      showMore: "Mehr anzeigen",
      hide: "Ausblenden",
      empty: "Noch keine Kommentare",
    },
    common: {
      loading: "Lädt...",
      cancel: "Abbrechen",
      save: "Speichern",
      close: "Schließen",
    },
  },
};

function normalizeLang(lang) {
  if (!lang) return null;
  const v = String(lang).toLowerCase();
  if (v === "en" || v === "ru" || v === "uk" || v === "de") return v;
  return null;
}

function detectLang() {
  const saved = normalizeLang(localStorage.getItem(STORAGE_KEY));
  if (saved) return saved;

  const nav = String(navigator.language || "").toLowerCase(); // e.g. "de-DE"
  if (nav.startsWith("de")) return "de";
  if (nav.startsWith("uk")) return "uk";
  if (nav.startsWith("ru")) return "ru";
  return "en";
}

export const i18n = createI18n({
  legacy: false,
  globalInjection: true, // чтобы можно было $t(...) в шаблонах
  locale: detectLang(),
  fallbackLocale: "en",
  messages,
});

export function setLang(lang) {
  const v = normalizeLang(lang) || "en";
  i18n.global.locale.value = v;
  localStorage.setItem(STORAGE_KEY, v);
}

export function getLang() {
  return i18n.global.locale.value;
}
