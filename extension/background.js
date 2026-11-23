chrome.runtime.onMessage.addListener(
  (message, sender, sendResponse) => {

    if (message.type === "lookup") {

      fetch(
        `http://127.0.0.1:8000/lookup?word=${encodeURIComponent(
          message.word
        )}&sentence=${encodeURIComponent(
          message.sentence
        )}`
      )
        .then((response) => {

          if (!response.ok) {
            throw new Error();
          }

          return response.json();
        })
        .then((data) => sendResponse(data))
        .catch(() => sendResponse(null));

      return true;
    }

    if (message.type === "anki") {

      fetch(
        "http://127.0.0.1:8000/anki/add",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify(message.data)
        }
      )
        .then((response) => response.json())
        .then((data) => sendResponse(data))
        .catch(() => sendResponse(null));

      return true;
    }
  }
);